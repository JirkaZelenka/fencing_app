from django.db import migrations


def set_trainer_icon(apps, schema_editor):
    Badge = apps.get_model("fencers", "Badge")
    Badge.objects.filter(name="Trenér").update(icon_class="ti ti-barbell")


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("fencers", "0034_update_default_badges"),
    ]

    operations = [
        migrations.RunPython(set_trainer_icon, noop_reverse),
    ]
