from django.db import migrations, models


def seed_content_pages(apps, _schema_editor):
    ContentPage = apps.get_model("fencers", "ContentPage")
    defaults = [
        ("wiki", "glossary", "Slovníček"),
        ("wiki", "videos", "Videonávody"),
        ("wiki", "rules", "Pravidla"),
        ("wiki", "equipment-assembly", "Technická část"),
        ("equipment", "tools", "Nářadí"),
        ("equipment", "weapon-diagnosis", "Diagnostika zbraně"),
        ("equipment", "blade-assembly", "Sestavení čepele"),
        ("equipment", "equipment-maintenance", "Údržba vybavení"),
    ]
    for section, slug, title in defaults:
        ContentPage.objects.get_or_create(
            section=section,
            slug=slug,
            defaults={"title": title, "is_published": True},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("fencers", "0039_equipment_kord_snura_numbered_pairs"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContentPage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("section", models.CharField(choices=[("wiki", "Wiki"), ("equipment", "Výbava")], max_length=20, verbose_name="Sekce")),
                ("slug", models.SlugField(max_length=120, verbose_name="Slug")),
                ("title", models.CharField(max_length=200, verbose_name="Název stránky")),
                ("intro", models.TextField(blank=True, verbose_name="Úvod")),
                ("is_published", models.BooleanField(default=True, verbose_name="Publikováno")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Upraveno")),
            ],
            options={
                "verbose_name": "Obsahová stránka",
                "verbose_name_plural": "Obsahové stránky",
                "ordering": ["section", "title"],
                "unique_together": {("section", "slug")},
            },
        ),
        migrations.CreateModel(
            name="ContentBlock",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("block_type", models.CharField(choices=[("heading", "Nadpis"), ("text", "Text"), ("image", "Obrázek"), ("link", "Odkaz / článek"), ("html", "Vlastní HTML")], max_length=20, verbose_name="Typ bloku")),
                ("position", models.PositiveIntegerField(default=0, verbose_name="Pořadí")),
                ("title", models.CharField(blank=True, max_length=200, verbose_name="Nadpis bloku")),
                ("body", models.TextField(blank=True, verbose_name="Text / HTML")),
                ("image_url", models.URLField(blank=True, verbose_name="URL obrázku")),
                ("image_alt", models.CharField(blank=True, max_length=200, verbose_name="ALT obrázku")),
                ("link_url", models.URLField(blank=True, verbose_name="URL odkazu")),
                ("link_text", models.CharField(blank=True, max_length=200, verbose_name="Text odkazu")),
                ("is_visible", models.BooleanField(default=True, verbose_name="Viditelný")),
                ("page", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="blocks", to="fencers.contentpage", verbose_name="Stránka")),
            ],
            options={
                "verbose_name": "Obsahový blok",
                "verbose_name_plural": "Obsahové bloky",
                "ordering": ["position", "id"],
            },
        ),
        migrations.RunPython(seed_content_pages, migrations.RunPython.noop),
    ]
