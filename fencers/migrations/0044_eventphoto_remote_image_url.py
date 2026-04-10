from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fencers", "0043_subalbum_unique_name_per_album"),
    ]

    operations = [
        migrations.AddField(
            model_name="eventphoto",
            name="remote_image_url",
            field=models.URLField(
                blank=True,
                default="",
                max_length=1024,
                verbose_name="URL obrázku (vzdálené úložiště)",
            ),
        ),
        migrations.AlterField(
            model_name="eventphoto",
            name="photo",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="event_photos/",
                verbose_name="Fotka",
            ),
        ),
    ]
