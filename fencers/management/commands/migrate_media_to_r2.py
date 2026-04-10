import mimetypes
import os
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from fencers.models import (
    CircuitSong,
    EquipmentItem,
    EventPhoto,
    FencerProfile,
    PaymentStatus,
    PhotoAlbum,
    RulesDocument,
)
from fencers.r2_storage import get_r2_client, r2_ready


def _slug_part(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "unknown"


def _upload_file(client, src_path: Path, key: str) -> None:
    content_type = mimetypes.guess_type(str(src_path))[0] or "application/octet-stream"
    with src_path.open("rb") as fp:
        client.put_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=key,
            Body=fp,
            ContentType=content_type,
        )


class Command(BaseCommand):
    help = "Upload existing local MEDIA_ROOT files to Cloudflare R2 in structured folders."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only print what would be uploaded.",
        )

    def handle(self, *args, **options):
        if not r2_ready():
            raise CommandError("R2 is not configured. Check R2_* environment variables.")

        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.exists():
            raise CommandError(f"MEDIA_ROOT does not exist: {media_root}")

        client = get_r2_client()
        dry_run = options["dry_run"]
        uploaded = 0
        failed = 0
        seen_rel_paths = set()

        def process(src_rel_path: str, target_key: str):
            nonlocal uploaded, failed
            if not src_rel_path:
                return
            src_rel_path = str(src_rel_path).replace("\\", "/")
            src_path = media_root / src_rel_path
            if not src_path.exists() or not src_path.is_file():
                return
            seen_rel_paths.add(src_rel_path)
            if dry_run:
                self.stdout.write(f"[DRY] {src_rel_path} -> {target_key}")
                uploaded += 1
                return
            try:
                _upload_file(client, src_path, target_key)
                uploaded += 1
            except Exception as exc:
                failed += 1
                self.stderr.write(f"[FAIL] {src_rel_path} -> {target_key}: {exc}")

        # Profile photos
        for p in FencerProfile.objects.filter(profile_photo__isnull=False).exclude(profile_photo=""):
            rel = p.profile_photo.name
            filename = Path(rel).name
            key = f"profile_photos/{p.id}-{_slug_part(p.get_full_name())}/{filename}"
            process(rel, key)

        # Event album covers
        for album in PhotoAlbum.objects.filter(cover_photo__isnull=False).exclude(cover_photo="").select_related("event"):
            rel = album.cover_photo.name
            filename = Path(rel).name
            key = f"album_covers/{album.event.id}-{_slug_part(album.event.title)}/{filename}"
            process(rel, key)

        # Event photos (event / owner / subalbum)
        for photo in EventPhoto.objects.filter(photo__isnull=False).exclude(photo="").select_related(
            "subalbum",
            "subalbum__album",
            "subalbum__album__event",
            "uploaded_by",
        ):
            rel = photo.photo.name
            filename = Path(rel).name
            event = photo.subalbum.album.event if photo.subalbum and photo.subalbum.album else None
            subalbum = photo.subalbum
            owner = subalbum.created_by if subalbum else photo.uploaded_by
            event_part = (
                f"{event.id}-{_slug_part(event.title)}"
                if event
                else f"date-{photo.event_date.isoformat() if photo.event_date else 'unknown'}"
            )
            owner_part = (
                f"{owner.id}-{_slug_part(owner.get_full_name())}"
                if owner
                else "unknown-owner"
            )
            subalbum_part = (
                f"{subalbum.id}-{_slug_part(subalbum.name)}"
                if subalbum
                else "no-subalbum"
            )
            key = f"event_photos/{event_part}/{owner_part}/{subalbum_part}/{filename}"
            process(rel, key)

        # Equipment images
        for item in EquipmentItem.objects.filter(image__isnull=False).exclude(image=""):
            rel = item.image.name
            filename = Path(rel).name
            key = f"equipment/{item.id}-{_slug_part(item.name)}/{filename}"
            process(rel, key)

        # QR codes
        for payment in PaymentStatus.objects.filter(qr_code__isnull=False).exclude(qr_code="").select_related("fencer"):
            rel = payment.qr_code.name
            filename = Path(rel).name
            fencer = payment.fencer
            key = f"qr_codes/{fencer.id}-{_slug_part(fencer.get_full_name())}/{filename}"
            process(rel, key)

        # Circuit songs
        for song in CircuitSong.objects.filter(audio_file__isnull=False).exclude(audio_file="").select_related("circuit"):
            rel = song.audio_file.name
            filename = Path(rel).name
            key = f"circuit_songs/{song.circuit.id}-{_slug_part(song.circuit.name)}/{filename}"
            process(rel, key)

        # Rules docs
        for rule in RulesDocument.objects.filter(file__isnull=False).exclude(file=""):
            rel = rule.file.name
            filename = Path(rel).name
            key = f"rules/{rule.id}-{_slug_part(rule.title)}/{filename}"
            process(rel, key)

        # Any remaining file under media (unreferenced)
        for path in media_root.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(media_root).as_posix()
            if rel in seen_rel_paths:
                continue
            process(rel, f"legacy_media/{rel}")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Uploaded: {uploaded}"))
        self.stdout.write(self.style.WARNING(f"Failed: {failed}"))
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run mode: no files uploaded."))
        if failed:
            raise CommandError("Some uploads failed.")
