from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Event, PhotoAlbum


@receiver(post_save, sender=Event)
def create_photo_album_for_event(sender, instance, created, **kwargs):
    """Automatically create a PhotoAlbum when an Event is created"""
    if created:
        PhotoAlbum.objects.get_or_create(event=instance)

