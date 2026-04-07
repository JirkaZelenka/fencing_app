from django.db import migrations


def update_badges(apps, schema_editor):
    Badge = apps.get_model("fencers", "Badge")
    desired = {
        "Trenér": {
            "icon_class": "ti ti-chalkboard",
            "color": "#1d4ed8",
            "tooltip": "Trenér",
        },
        "Zbrojíř": {
            "icon_class": "ti ti-sword",
            "color": "#64748b",
            "tooltip": "Zbrojíř",
        },
        "Veterán": {
            "icon_class": "ti ti-star",
            "color": "#991b1b",
            "tooltip": "Veterán",
        },
        "Správce pokladny": {
            "icon_class": "ti ti-coin",
            "color": "#ca8a04",
            "tooltip": "Správce pokladny",
        },
        "Dohlížitel": {
            "icon_class": "ti ti-eye",
            "color": "#7e22ce",
            "tooltip": "Dohlížitel",
        },
        "Nováček": {
            "icon_class": "ti ti-leaf",
            "color": "#16a34a",
            "tooltip": "Nováček",
        },
        "Senior": {
            "icon_class": "ti ti-check",
            "color": "#f97316",
            "tooltip": "Senior",
        },
    }

    for name, attrs in desired.items():
        badge, _created = Badge.objects.get_or_create(name=name)
        badge.icon_class = attrs["icon_class"]
        badge.color = attrs["color"]
        badge.tooltip = attrs["tooltip"]
        badge.save(update_fields=["icon_class", "color", "tooltip"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("fencers", "0033_badge_and_fencerprofile_badges"),
    ]

    operations = [
        migrations.RunPython(update_badges, noop_reverse),
    ]
