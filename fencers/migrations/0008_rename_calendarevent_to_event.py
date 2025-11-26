# Generated manually to rename fencers_calendarevent to fencers_event

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fencers', '0005_tournament_calendar_event'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE fencers_calendarevent RENAME TO fencers_event;",
            reverse_sql="ALTER TABLE fencers_event RENAME TO fencers_calendarevent;",
        ),
    ]

