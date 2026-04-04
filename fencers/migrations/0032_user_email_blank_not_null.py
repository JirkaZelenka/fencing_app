from django.db import migrations, models


def clear_null_emails(apps, _schema_editor):
    User = apps.get_model("fencers", "User")
    User.objects.filter(email__isnull=True).update(email="")


class Migration(migrations.Migration):

    dependencies = [
        ("fencers", "0031_user_legacy_name_fields"),
    ]

    operations = [
        migrations.RunPython(clear_null_emails, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(blank=True, default="", max_length=254, verbose_name="Email"),
        ),
    ]
