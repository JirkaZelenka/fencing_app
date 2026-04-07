import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from fencers.i18n import TRANSLATIONS_EN, normalize_text


class Command(BaseCommand):
    help = "Sync missing EN translation keys from {% tr %} tags in templates."

    TR_PATTERN = re.compile(r"\{%\s*tr\s+([\"'])(.*?)\1\s*%\}")

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only print what would change; do not modify fencers/i18n.py.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        templates_dir = Path(settings.BASE_DIR) / "templates"
        i18n_file = Path(settings.BASE_DIR) / "fencers" / "i18n.py"

        texts = self._collect_tr_texts(templates_dir)
        if not texts:
            self.stdout.write("No {% tr %} usages found in templates.")
            return

        missing = []
        for text in texts:
            key = normalize_text(text)
            if key not in TRANSLATIONS_EN:
                missing.append((key, text))

        if not missing:
            self.stdout.write("Translations are already in sync.")
            return

        self.stdout.write(f"Found {len(missing)} missing EN translation key(s).")
        for key, text in missing[:25]:
            self.stdout.write(f' - {key!r} (from "{text}")')
        if len(missing) > 25:
            self.stdout.write(f" ... and {len(missing) - 25} more")

        if dry_run:
            self.stdout.write("Dry run mode: no files changed.")
            return

        updated_map = dict(TRANSLATIONS_EN)
        for key, _text in missing:
            updated_map[key] = key

        self._rewrite_translations_dict(i18n_file, updated_map)
        self.stdout.write("Updated fencers/i18n.py with missing keys.")

    def _collect_tr_texts(self, templates_dir: Path):
        texts = set()
        for template_file in templates_dir.rglob("*.html"):
            content = template_file.read_text(encoding="utf-8")
            matches = self.TR_PATTERN.findall(content)
            for _quote, raw_text in matches:
                if raw_text.strip():
                    texts.add(raw_text)
        return sorted(texts)

    def _rewrite_translations_dict(self, i18n_file: Path, translations: dict):
        content = i18n_file.read_text(encoding="utf-8")
        start = content.find("TRANSLATIONS_EN = {")
        if start == -1:
            raise RuntimeError("Could not find TRANSLATIONS_EN dictionary in i18n.py")

        end = content.find("\n}\n\n", start)
        if end == -1:
            raise RuntimeError("Could not locate end of TRANSLATIONS_EN dictionary in i18n.py")

        dict_lines = ["TRANSLATIONS_EN = {"]
        for key in sorted(translations.keys()):
            value = translations[key]
            dict_lines.append(f'    "{self._escape(key)}": "{self._escape(value)}",')
        dict_lines.append("}")
        new_block = "\n".join(dict_lines)

        new_content = content[:start] + new_block + content[end + 2 :]
        i18n_file.write_text(new_content, encoding="utf-8")

    @staticmethod
    def _escape(value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"')
