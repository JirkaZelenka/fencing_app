# Generated manually to add participants_count field to Event

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fencers', '0022_alter_event_options_alter_eventparticipation_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='participants_count',
            field=models.IntegerField(
                blank=True,
                help_text='Povinné pro Turnaj a Hum. turnaj',
                null=True,
                verbose_name='Počet účastníků'
            ),
        ),
    ]

