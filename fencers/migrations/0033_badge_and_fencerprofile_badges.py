from django.db import migrations, models


def seed_default_badges(apps, schema_editor):
    Badge = apps.get_model("fencers", "Badge")
    defaults = [
        {
            "name": "Trenér",
            "icon_class": "ti ti-megaphone",
            "color": "#1d4ed8",
            "tooltip": "Trenér",
        },
        {
            "name": "Zbrojíř",
            "icon_class": "ti ti-tool",
            "color": "#64748b",
            "tooltip": "Zbrojíř",
        },
        {
            "name": "Veterán",
            "icon_class": "ti ti-star",
            "color": "#991b1b",
            "tooltip": "Veterán",
        },
        {
            "name": "Správce pokladny",
            "icon_class": "ti ti-coin",
            "color": "#ca8a04",
            "tooltip": "Správce pokladny",
        },
        {
            "name": "Dohlížitel",
            "icon_class": "ti ti-eye",
            "color": "#7e22ce",
            "tooltip": "Dohlížitel",
        },
    ]
    for badge in defaults:
        Badge.objects.get_or_create(name=badge["name"], defaults=badge)


def unseed_default_badges(apps, schema_editor):
    Badge = apps.get_model("fencers", "Badge")
    Badge.objects.filter(
        name__in=["Trenér", "Zbrojíř", "Veterán", "Správce pokladny", "Dohlížitel"]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("fencers", "0032_user_email_blank_not_null"),
    ]

    operations = [
        migrations.CreateModel(
            name="Badge",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True, verbose_name="Název")),
                (
                    "icon_class",
                    models.CharField(
                        default="ti ti-award",
                        help_text='Např. "ti ti-whirl", "ti ti-coin".',
                        max_length=100,
                        verbose_name="Ikona (Tabler class)",
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        default="#6c757d",
                        help_text="Hex barva, např. #0d6efd",
                        max_length=20,
                        verbose_name="Barva pozadí",
                    ),
                ),
                ("tooltip", models.CharField(blank=True, max_length=200, verbose_name="Text po najetí")),
            ],
            options={
                "verbose_name": "Badge",
                "verbose_name_plural": "Badges",
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="fencerprofile",
            name="badges",
            field=models.ManyToManyField(blank=True, related_name="fencers", to="fencers.badge", verbose_name="Badges"),
        ),
        migrations.RunPython(seed_default_badges, unseed_default_badges),
    ]
