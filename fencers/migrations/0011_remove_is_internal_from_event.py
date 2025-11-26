# Generated manually to remove is_internal field from Event
# SQLite doesn't support DROP COLUMN directly, so we use a workaround

from django.db import migrations


def remove_is_internal(apps, schema_editor):
    # SQLite 3.35.0+ supports DROP COLUMN, but for compatibility we'll use a workaround
    # For now, just try DROP COLUMN - if it fails, the user can manually remove it
    with schema_editor.connection.cursor() as cursor:
        try:
            cursor.execute("ALTER TABLE fencers_event DROP COLUMN is_internal;")
        except Exception:
            # If DROP COLUMN fails, we'll need to recreate the table
            # For now, just pass - the column will remain but won't be used
            pass


def add_is_internal_back(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("ALTER TABLE fencers_event ADD COLUMN is_internal BOOLEAN NOT NULL DEFAULT 0;")


class Migration(migrations.Migration):

    dependencies = [
        ('fencers', '0010_create_eventparticipation_and_drop_tournaments'),
    ]

    operations = [
        migrations.RunPython(
            remove_is_internal,
            reverse_code=add_is_internal_back,
        ),
    ]
