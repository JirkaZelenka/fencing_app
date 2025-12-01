# Generated manually to change User references to FencerProfile for photos, albums, likes, reactions, circuits, and news

from django.db import migrations, models
import django.db.models.deletion


def migrate_user_to_fencerprofile(apps, schema_editor):
    """Migrate all User references to FencerProfile references using raw SQL"""
    db_alias = schema_editor.connection.alias
    
    with schema_editor.connection.cursor() as cursor:
        # Migrate CircuitTraining using JOIN
        cursor.execute("""
            UPDATE fencers_circuittraining 
            SET created_by_fencer_id = (
                SELECT fp.id 
                FROM fencers_fencerprofile fp 
                WHERE fp.user_id = fencers_circuittraining.created_by_id
            )
            WHERE created_by_id IS NOT NULL
        """)
        
        # Migrate SubAlbum using JOIN
        cursor.execute("""
            UPDATE fencers_subalbum 
            SET created_by_fencer_id = (
                SELECT fp.id 
                FROM fencers_fencerprofile fp 
                WHERE fp.user_id = fencers_subalbum.created_by_id
            )
            WHERE created_by_id IS NOT NULL
        """)
        
        # Migrate EventPhoto using JOIN
        cursor.execute("""
            UPDATE fencers_eventphoto 
            SET uploaded_by_fencer_id = (
                SELECT fp.id 
                FROM fencers_fencerprofile fp 
                WHERE fp.user_id = fencers_eventphoto.uploaded_by_id
            )
            WHERE uploaded_by_id IS NOT NULL
        """)
        
        # Migrate PhotoLike using JOIN
        cursor.execute("""
            UPDATE fencers_photolike 
            SET fencer_id = (
                SELECT fp.id 
                FROM fencers_fencerprofile fp 
                WHERE fp.user_id = fencers_photolike.user_id
            )
            WHERE user_id IS NOT NULL
        """)
        
        # Migrate EventReaction using JOIN
        cursor.execute("""
            UPDATE fencers_eventreaction 
            SET fencer_id = (
                SELECT fp.id 
                FROM fencers_fencerprofile fp 
                WHERE fp.user_id = fencers_eventreaction.user_id
            )
            WHERE user_id IS NOT NULL
        """)
        
        # Migrate News using JOIN
        cursor.execute("""
            UPDATE fencers_news 
            SET created_by_fencer_id = (
                SELECT fp.id 
                FROM fencers_fencerprofile fp 
                WHERE fp.user_id = fencers_news.created_by_id
            )
            WHERE created_by_id IS NOT NULL
        """)
        
        # Migrate NewsRead using JOIN
        cursor.execute("""
            UPDATE fencers_newsread 
            SET fencer_id = (
                SELECT fp.id 
                FROM fencers_fencerprofile fp 
                WHERE fp.user_id = fencers_newsread.user_id
            )
            WHERE user_id IS NOT NULL
        """)


def reverse_migration(apps, schema_editor):
    """Reverse migration - not implemented"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('fencers', '0024_add_birth_year_and_points'),
    ]

    operations = [
        # Step 1: Add new fencer fields as nullable
        migrations.AddField(
            model_name='circuittraining',
            name='created_by_fencer',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='circuit_trainings_temp', to='fencers.fencerprofile', verbose_name='Vytvořil'),
        ),
        migrations.AddField(
            model_name='subalbum',
            name='created_by_fencer',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subalbums_temp', to='fencers.fencerprofile', verbose_name='Vytvořil'),
        ),
        migrations.AddField(
            model_name='eventphoto',
            name='uploaded_by_fencer',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='event_photos_temp', to='fencers.fencerprofile', verbose_name='Nahrál'),
        ),
        migrations.AddField(
            model_name='photolike',
            name='fencer',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='photo_likes', to='fencers.fencerprofile', verbose_name='Šermíř'),
        ),
        migrations.AddField(
            model_name='eventreaction',
            name='fencer',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_reactions', to='fencers.fencerprofile', verbose_name='Šermíř'),
        ),
        migrations.AddField(
            model_name='news',
            name='created_by_fencer',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='news_created_temp', to='fencers.fencerprofile', verbose_name='Vytvořil'),
        ),
        migrations.AddField(
            model_name='newsread',
            name='fencer',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='news_reads', to='fencers.fencerprofile', verbose_name='Šermíř'),
        ),
        # Step 1.5: Temporarily remove unique_together constraints that reference 'user'
        migrations.AlterUniqueTogether(
            name='photolike',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='eventreaction',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='newsread',
            unique_together=set(),
        ),
        # Step 2: Migrate data
        migrations.RunPython(migrate_user_to_fencerprofile, reverse_migration),
        # Step 3: Remove old user fields and rename new fields
        migrations.RemoveField(
            model_name='circuittraining',
            name='created_by',
        ),
        migrations.RenameField(
            model_name='circuittraining',
            old_name='created_by_fencer',
            new_name='created_by',
        ),
        migrations.RemoveField(
            model_name='subalbum',
            name='created_by',
        ),
        migrations.RenameField(
            model_name='subalbum',
            old_name='created_by_fencer',
            new_name='created_by',
        ),
        migrations.RemoveField(
            model_name='eventphoto',
            name='uploaded_by',
        ),
        migrations.RenameField(
            model_name='eventphoto',
            old_name='uploaded_by_fencer',
            new_name='uploaded_by',
        ),
        migrations.RemoveField(
            model_name='photolike',
            name='user',
        ),
        migrations.RemoveField(
            model_name='eventreaction',
            name='user',
        ),
        migrations.RemoveField(
            model_name='news',
            name='created_by',
        ),
        migrations.RenameField(
            model_name='news',
            old_name='created_by_fencer',
            new_name='created_by',
        ),
        migrations.RemoveField(
            model_name='newsread',
            name='user',
        ),
        # Step 4: Add back unique_together constraints with new field names
        migrations.AlterUniqueTogether(
            name='photolike',
            unique_together={('photo', 'fencer')},
        ),
        migrations.AlterUniqueTogether(
            name='eventreaction',
            unique_together={('event', 'fencer')},
        ),
        migrations.AlterUniqueTogether(
            name='newsread',
            unique_together={('news', 'fencer')},
        ),
        # Step 5: Make fields non-nullable where needed
        migrations.AlterField(
            model_name='circuittraining',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='circuit_trainings', to='fencers.fencerprofile', verbose_name='Vytvořil'),
        ),
        migrations.AlterField(
            model_name='photolike',
            name='fencer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photo_likes', to='fencers.fencerprofile', verbose_name='Šermíř'),
        ),
        migrations.AlterField(
            model_name='eventreaction',
            name='fencer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_reactions', to='fencers.fencerprofile', verbose_name='Šermíř'),
        ),
        migrations.AlterField(
            model_name='newsread',
            name='fencer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='news_reads', to='fencers.fencerprofile', verbose_name='Šermíř'),
        ),
    ]

