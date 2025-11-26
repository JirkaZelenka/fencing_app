# Generated manually to add is_internal field to Event

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fencers', '0008_rename_calendarevent_to_event'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE fencers_event ADD COLUMN is_internal BOOLEAN NOT NULL DEFAULT 0;",
            reverse_sql="ALTER TABLE fencers_event DROP COLUMN is_internal;",
        ),
    ]
