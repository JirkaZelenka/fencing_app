# Generated manually to change Event from DateTimeField to DateField

from django.db import migrations, models


def migrate_datetime_to_date(apps, schema_editor):
    """Migrate start_date DateTimeField to date DateField"""
    Event = apps.get_model('fencers', 'Event')
    
    # Update all events: convert start_date to date
    for event in Event.objects.all():
        if event.start_date:
            event.date = event.start_date.date()
            event.save()


def reverse_migrate_date_to_datetime(apps, schema_editor):
    """Reverse migration: convert date back to start_date (as datetime at midnight)"""
    Event = apps.get_model('fencers', 'Event')
    
    from django.utils import timezone
    for event in Event.objects.all():
        if event.date:
            # Convert date to datetime at midnight
            event.start_date = timezone.make_aware(
                timezone.datetime.combine(event.date, timezone.datetime.min.time())
            )
            event.save()


class Migration(migrations.Migration):

    dependencies = [
        ('fencers', '0020_news_newsread'),
    ]

    operations = [
        # Step 1: Add new date field (nullable first)
        migrations.AddField(
            model_name='event',
            name='date',
            field=models.DateField(null=True, blank=True, verbose_name='Datum'),
        ),
        # Step 2: Migrate data from start_date to date
        migrations.RunPython(migrate_datetime_to_date, reverse_migrate_date_to_datetime),
        # Step 3: Remove end_date field
        migrations.RemoveField(
            model_name='event',
            name='end_date',
        ),
        # Step 4: Remove start_date field
        migrations.RemoveField(
            model_name='event',
            name='start_date',
        ),
        # Step 5: Make date field required (no longer nullable)
        migrations.AlterField(
            model_name='event',
            name='date',
            field=models.DateField(verbose_name='Datum'),
        ),
    ]





