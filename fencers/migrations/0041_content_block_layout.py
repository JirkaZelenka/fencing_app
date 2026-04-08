from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fencers", "0040_content_pages"),
    ]

    operations = [
        migrations.AddField(
            model_name="contentblock",
            name="layout",
            field=models.CharField(
                choices=[("full", "Celá šířka"), ("half", "1/2 šířky")],
                default="full",
                max_length=10,
                verbose_name="Rozložení",
            ),
        ),
    ]
