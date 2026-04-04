# Generated manually to add birth_year to FencerProfile and points to EventParticipation

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fencers', '0023_add_participants_count_to_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='fencerprofile',
            name='birth_year',
            field=models.IntegerField(blank=True, null=True, verbose_name='Rok narození'),
        ),
        migrations.AddField(
            model_name='eventparticipation',
            name='points',
            field=models.FloatField(blank=True, null=True, verbose_name='Body'),
        ),
    ]







