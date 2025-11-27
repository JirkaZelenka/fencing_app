# Generated manually to change User references to FencerProfile using raw SQL

from django.db import migrations, models
import django.db.models.deletion


def migrate_to_fencerprofile(apps, schema_editor):
    """Migrate all User references to FencerProfile references using raw SQL"""
    FencerProfile = apps.get_model('fencers', 'FencerProfile')
    User = apps.get_model('auth', 'User')
    
    db_alias = schema_editor.connection.alias
    
    with schema_editor.connection.cursor() as cursor:
        # Step 1: Ensure all users have FencerProfiles
        cursor.execute("SELECT id FROM auth_user WHERE id NOT IN (SELECT user_id FROM fencers_fencerprofile WHERE user_id IS NOT NULL)")
        users_without_profiles = [row[0] for row in cursor.fetchall()]
        for user_id in users_without_profiles:
            user = User.objects.using(db_alias).get(id=user_id)
            FencerProfile.objects.using(db_alias).create(user=user)
        
        # Step 2: Create mapping of user_id to profile_id
        cursor.execute("SELECT user_id, id FROM fencers_fencerprofile WHERE user_id IS NOT NULL")
        user_to_profile = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Step 3: Migrate EventParticipation
        cursor.execute("""
            CREATE TABLE fencers_eventparticipation_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL REFERENCES fencers_event(id) ON DELETE CASCADE,
                position INTEGER NULL,
                wins INTEGER NOT NULL DEFAULT 0,
                losses INTEGER NOT NULL DEFAULT 0,
                touches_scored INTEGER NOT NULL DEFAULT 0,
                touches_received INTEGER NOT NULL DEFAULT 0,
                fencer_id INTEGER NOT NULL REFERENCES fencers_fencerprofile(id) ON DELETE CASCADE,
                UNIQUE(fencer_id, event_id)
            )
        """)
        cursor.execute("""
            INSERT INTO fencers_eventparticipation_new (id, event_id, position, wins, losses, touches_scored, touches_received, fencer_id)
            SELECT ep.id, ep.event_id, ep.position, ep.wins, ep.losses, ep.touches_scored, ep.touches_received, fp.id
            FROM fencers_eventparticipation ep
            JOIN fencers_fencerprofile fp ON ep.fencer_id = fp.user_id
        """)
        cursor.execute("DROP TABLE fencers_eventparticipation")
        cursor.execute("ALTER TABLE fencers_eventparticipation_new RENAME TO fencers_eventparticipation")
        cursor.execute("CREATE INDEX fencers_eventparticipation_event_id ON fencers_eventparticipation(event_id)")
        cursor.execute("CREATE INDEX fencers_eventparticipation_fencer_id ON fencers_eventparticipation(fencer_id)")
        
        # Step 4: Migrate TrainingNote
        cursor.execute("""
            CREATE TABLE fencers_trainingnote_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fencer_id INTEGER NOT NULL REFERENCES fencers_fencerprofile(id) ON DELETE CASCADE,
                date DATE NOT NULL,
                notes TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
        """)
        cursor.execute("""
            INSERT INTO fencers_trainingnote_new (id, fencer_id, date, notes, created_at, updated_at)
            SELECT tn.id, fp.id, tn.date, tn.notes, tn.created_at, tn.updated_at
            FROM fencers_trainingnote tn
            JOIN fencers_fencerprofile fp ON tn.fencer_id = fp.user_id
        """)
        cursor.execute("DROP TABLE fencers_trainingnote")
        cursor.execute("ALTER TABLE fencers_trainingnote_new RENAME TO fencers_trainingnote")
        cursor.execute("CREATE INDEX fencers_trainingnote_fencer_id ON fencers_trainingnote(fencer_id)")
        
        # Step 5: Migrate PaymentStatus
        cursor.execute("""
            CREATE TABLE fencers_paymentstatus_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fencer_id INTEGER NOT NULL UNIQUE REFERENCES fencers_fencerprofile(id) ON DELETE CASCADE,
                is_paid BOOLEAN NOT NULL DEFAULT 0,
                payment_date DATE NULL,
                amount DECIMAL(10,2) NULL,
                qr_code VARCHAR(100) NULL,
                payment_info TEXT NOT NULL
            )
        """)
        cursor.execute("""
            INSERT INTO fencers_paymentstatus_new (id, fencer_id, is_paid, payment_date, amount, qr_code, payment_info)
            SELECT ps.id, fp.id, ps.is_paid, ps.payment_date, ps.amount, ps.qr_code, ps.payment_info
            FROM fencers_paymentstatus ps
            JOIN fencers_fencerprofile fp ON ps.fencer_id = fp.user_id
        """)
        cursor.execute("DROP TABLE fencers_paymentstatus")
        cursor.execute("ALTER TABLE fencers_paymentstatus_new RENAME TO fencers_paymentstatus")
        
        # Step 6: Migrate UserEquipment
        cursor.execute("""
            CREATE TABLE fencers_userequipment_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fencer_id INTEGER NOT NULL REFERENCES fencers_fencerprofile(id) ON DELETE CASCADE,
                equipment_id INTEGER NOT NULL REFERENCES fencers_equipmentitem(id) ON DELETE CASCADE,
                is_owned BOOLEAN NOT NULL DEFAULT 0,
                purchase_date DATE NULL,
                UNIQUE(fencer_id, equipment_id)
            )
        """)
        cursor.execute("""
            INSERT INTO fencers_userequipment_new (id, fencer_id, equipment_id, is_owned, purchase_date)
            SELECT ue.id, fp.id, ue.equipment_id, ue.is_owned, ue.purchase_date
            FROM fencers_userequipment ue
            JOIN fencers_fencerprofile fp ON ue.user_id = fp.user_id
        """)
        cursor.execute("DROP TABLE fencers_userequipment")
        cursor.execute("ALTER TABLE fencers_userequipment_new RENAME TO fencers_userequipment")
        cursor.execute("CREATE INDEX fencers_userequipment_fencer_id ON fencers_userequipment(fencer_id)")


def reverse_migration(apps, schema_editor):
    """Reverse migration - not implemented"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('fencers', '0016_sync_tournament_deletion_state'),
    ]

    operations = [
        migrations.RunPython(migrate_to_fencerprofile, reverse_migration),
        # Update Django's state to match the database
        migrations.SeparateDatabaseAndState(
            database_operations=[],  # Database already updated
            state_operations=[
                migrations.AlterField(
                    model_name='eventparticipation',
                    name='fencer',
                    field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_participations', to='fencers.fencerprofile', verbose_name='Šermíř'),
                ),
                migrations.AlterField(
                    model_name='trainingnote',
                    name='fencer',
                    field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='training_notes', to='fencers.fencerprofile', verbose_name='Šermíř'),
                ),
                migrations.AlterField(
                    model_name='paymentstatus',
                    name='fencer',
                    field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment_status', to='fencers.fencerprofile', verbose_name='Šermíř'),
                ),
                migrations.RemoveField(
                    model_name='userequipment',
                    name='user',
                ),
                migrations.AddField(
                    model_name='userequipment',
                    name='fencer',
                    field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='equipment', to='fencers.fencerprofile', verbose_name='Šermíř'),
                ),
                migrations.AlterUniqueTogether(
                    name='userequipment',
                    unique_together={('fencer', 'equipment')},
                ),
            ],
        ),
    ]
