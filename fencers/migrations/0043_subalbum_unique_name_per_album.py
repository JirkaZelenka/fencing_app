from collections import defaultdict

from django.db import migrations, models


def dedupe_subalbum_names(apps, _schema_editor):
    SubAlbum = apps.get_model("fencers", "SubAlbum")
    albums = SubAlbum.objects.values_list("album_id", flat=True).distinct()
    for album_id in albums:
        subs = list(
            SubAlbum.objects.filter(album_id=album_id).order_by("id")
        )
        by_name = defaultdict(list)
        for s in subs:
            by_name[s.name].append(s)
        existing = {s.name for s in subs}
        for name, group in by_name.items():
            if len(group) <= 1:
                continue
            for s in group[1:]:
                candidate = f"{name}-copy"
                n = 2
                while candidate in existing:
                    candidate = f"{name}-copy-{n}"
                    n += 1
                s.name = candidate
                s.save(update_fields=["name"])
                existing.add(candidate)


class Migration(migrations.Migration):

    dependencies = [
        ("fencers", "0042_fencerprofile_profile_photo"),
    ]

    operations = [
        migrations.RunPython(dedupe_subalbum_names, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="subalbum",
            constraint=models.UniqueConstraint(
                fields=("album", "name"),
                name="fencers_subalbum_album_name_uniq",
            ),
        ),
    ]
