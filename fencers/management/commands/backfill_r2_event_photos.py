"""Create EventPhoto rows for objects in R2 that have no matching DB row yet."""

import os

from django.core.management.base import BaseCommand, CommandError

from fencers.models import EventPhoto, SubAlbum
from fencers.r2_storage import list_subalbum_images, r2_ready


class Command(BaseCommand):
    help = "Backfill EventPhoto from R2 keys listed per subalbum (orphan uploads)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print actions only.",
        )

    def handle(self, *args, **options):
        if not r2_ready():
            raise CommandError("R2 is not configured.")

        dry_run = options["dry_run"]
        created = 0
        for subalbum in SubAlbum.objects.select_related(
            "album__event", "created_by"
        ).order_by("id"):
            event = subalbum.album.event
            owner = subalbum.created_by
            try:
                objects = list_subalbum_images(
                    event=event, subalbum=subalbum, owner_profile=owner
                )
            except Exception as exc:
                self.stderr.write(f"Subalbum {subalbum.id}: list failed: {exc}")
                continue
            for item in objects:
                url = item["url"]
                key = item["key"]
                if EventPhoto.objects.filter(remote_image_url=url).exists():
                    continue
                filename = os.path.basename(key)
                stem, _ = os.path.splitext(filename)
                title = (stem or "foto")[:200]
                if dry_run:
                    self.stdout.write(f"[DRY] would create: {key}")
                    created += 1
                    continue
                EventPhoto.objects.create(
                    title=title,
                    description="",
                    remote_image_url=url,
                    event_date=event.date,
                    uploaded_by=owner,
                    subalbum=subalbum,
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Created EventPhoto rows: {created}"))
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run: no rows written."))
