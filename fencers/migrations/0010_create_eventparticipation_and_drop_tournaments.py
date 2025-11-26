# Generated manually to create EventParticipation and remove Tournament tables

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fencers', '0009_add_is_internal_to_event'),
    ]

    operations = [
        # Create EventParticipation table using raw SQL
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS fencers_eventparticipation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    position INTEGER NULL,
                    wins INTEGER NOT NULL DEFAULT 0,
                    losses INTEGER NOT NULL DEFAULT 0,
                    touches_scored INTEGER NOT NULL DEFAULT 0,
                    touches_received INTEGER NOT NULL DEFAULT 0,
                    event_id INTEGER NOT NULL REFERENCES fencers_event(id) ON DELETE CASCADE,
                    fencer_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
                    UNIQUE(fencer_id, event_id)
                );
                CREATE INDEX IF NOT EXISTS fencers_eventparticipation_event_id ON fencers_eventparticipation(event_id);
                CREATE INDEX IF NOT EXISTS fencers_eventparticipation_fencer_id ON fencers_eventparticipation(fencer_id);
            """,
            reverse_sql="DROP TABLE IF EXISTS fencers_eventparticipation;",
        ),
        # Drop TournamentParticipation table
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS fencers_tournamentparticipation;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Drop Tournament table
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS fencers_tournament;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
