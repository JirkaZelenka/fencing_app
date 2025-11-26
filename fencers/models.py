from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Club(models.Model):
    name = models.CharField(max_length=200, verbose_name="Název klubu")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Klub"
        verbose_name_plural = "Kluby"


class FencerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='fencer_profile')
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Klub")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.club})"
    
    class Meta:
        verbose_name = "Profil šermíře"
        verbose_name_plural = "Profily šermířů"


class Event(models.Model):
    class EventType(models.TextChoices):
        TOURNAMENT = 'tournament', "Turnaj"
        HUMANITARIAN = 'humanitarian', "Hum. turnaj"
        OTHER = 'other', "Ostatní akce"

    title = models.CharField(max_length=200, verbose_name="Název")
    description = models.TextField(blank=True, verbose_name="Popis")
    start_date = models.DateTimeField(verbose_name="Začátek")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Konec")
    location = models.CharField(max_length=200, blank=True, verbose_name="Místo")
    external_link = models.URLField(blank=True, verbose_name="Externí odkaz (czechfencing)")
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.OTHER,
        verbose_name="Typ akce",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Akce"
        verbose_name_plural = "Akce"
        ordering = ['start_date']

    def __str__(self):
        return f"{self.title} ({self.start_date:%d.%m.%Y})"


class EventParticipation(models.Model):
    fencer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_participations', verbose_name="Šermíř")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participations', verbose_name="Akce")
    position = models.IntegerField(null=True, blank=True, verbose_name="Umístění")
    wins = models.IntegerField(default=0, verbose_name="Výhry")
    losses = models.IntegerField(default=0, verbose_name="Prohry")
    touches_scored = models.IntegerField(default=0, verbose_name="Zasazené zásahy")
    touches_received = models.IntegerField(default=0, verbose_name="Obdržené zásahy")
    
    class Meta:
        verbose_name = "Účast na akci"
        verbose_name_plural = "Účasti na akcích"
        unique_together = ['fencer', 'event']
        ordering = ['-event__start_date']


class TrainingNote(models.Model):
    fencer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='training_notes', verbose_name="Šermíř")
    date = models.DateField(verbose_name="Datum")
    notes = models.TextField(verbose_name="Poznámky")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Poznámka z tréninku"
        verbose_name_plural = "Poznámky z tréninků"
        ordering = ['-date']


class CircuitTraining(models.Model):
    name = models.CharField(max_length=200, verbose_name="Název sestavy")
    description = models.TextField(blank=True, verbose_name="Popis")
    exercises = models.TextField(verbose_name="Cvičení (každé na nový řádek)")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='circuit_trainings', verbose_name="Vytvořil")
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False, verbose_name="Veřejné")
    
    class Meta:
        verbose_name = "Masíčko"
        verbose_name_plural = "Masíčka"
        ordering = ['-created_at']


class CircuitSong(models.Model):
    circuit = models.ForeignKey(CircuitTraining, on_delete=models.CASCADE, related_name='songs', verbose_name="Masíčko")
    name = models.CharField(max_length=200, verbose_name="Název skladby")
    audio_file = models.FileField(upload_to='circuit_songs/', verbose_name="Audio soubor")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Skladba pro masíčko"
        verbose_name_plural = "Skladby pro masíčka"


class PhotoAlbum(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='photo_album', verbose_name="Akce")
    cover_photo = models.ImageField(upload_to='album_covers/', null=True, blank=True, verbose_name="Obalová fotka")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Fotoalbum"
        verbose_name_plural = "Fotoalba"
        ordering = ['-event__start_date']
    
    def __str__(self):
        return f"Album: {self.event.title}"
    
    @property
    def date(self):
        return self.event.start_date.date()


class SubAlbum(models.Model):
    album = models.ForeignKey(PhotoAlbum, on_delete=models.CASCADE, related_name='subalbums', verbose_name="Album")
    name = models.CharField(max_length=200, verbose_name="Název")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Vytvořil")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Subalbum"
        verbose_name_plural = "Subalba"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.album.event.title})"


class EventPhoto(models.Model):
    title = models.CharField(max_length=200, verbose_name="Název")
    description = models.TextField(blank=True, verbose_name="Popis")
    photo = models.ImageField(upload_to='event_photos/', verbose_name="Fotka")
    event_date = models.DateField(null=True, blank=True, verbose_name="Datum akce")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Nahrál")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False, verbose_name="Doporučená")
    subalbum = models.ForeignKey(SubAlbum, on_delete=models.CASCADE, related_name='photos', null=True, blank=True, verbose_name="Subalbum")
    
    class Meta:
        verbose_name = "Fotka z akce"
        verbose_name_plural = "Fotky z akcí"
        ordering = ['-event_date', '-uploaded_at']
    
    def get_like_count(self):
        """Get the number of likes for this photo"""
        return self.likes.count()
    
    def is_liked_by_user(self, user):
        """Check if a user has liked this photo"""
        if not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()


class PhotoLike(models.Model):
    photo = models.ForeignKey(EventPhoto, on_delete=models.CASCADE, related_name='likes', verbose_name="Fotka")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photo_likes', verbose_name="Uživatel")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Líbí se mi"
        verbose_name_plural = "Líbí se mi"
        unique_together = ['photo', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} likes {self.photo.title}"


class EventReaction(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reactions', verbose_name="Akce")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_reactions', verbose_name="Uživatel")
    will_attend = models.BooleanField(default=False, verbose_name="Zúčastním se")
    comment = models.TextField(blank=True, verbose_name="Komentář")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Reakce na akci"
        verbose_name_plural = "Reakce na akce"
        unique_together = ['event', 'user']


class PaymentStatus(models.Model):
    fencer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='payment_status', verbose_name="Šermíř")
    is_paid = models.BooleanField(default=False, verbose_name="Zaplaceno")
    payment_date = models.DateField(null=True, blank=True, verbose_name="Datum platby")
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Částka")
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True, verbose_name="QR kód")
    payment_info = models.TextField(blank=True, verbose_name="Informace k platbě")
    
    class Meta:
        verbose_name = "Stav platby"
        verbose_name_plural = "Stavy plateb"


class GlossaryTerm(models.Model):
    term = models.CharField(max_length=200, verbose_name="Pojem")
    definition = models.TextField(verbose_name="Definice")
    
    class Meta:
        verbose_name = "Pojem ve slovníčku"
        verbose_name_plural = "Slovníček pojmů"
        ordering = ['term']


class GuideVideo(models.Model):
    title = models.CharField(max_length=200, verbose_name="Název")
    youtube_url = models.URLField(verbose_name="YouTube URL")
    description = models.TextField(blank=True, verbose_name="Popis")
    category = models.CharField(max_length=100, blank=True, verbose_name="Kategorie")
    
    class Meta:
        verbose_name = "Návodové video"
        verbose_name_plural = "Návodová videa"
        ordering = ['title']


class RulesDocument(models.Model):
    title = models.CharField(max_length=200, verbose_name="Název")
    content = models.TextField(verbose_name="Obsah")
    file = models.FileField(upload_to='rules/', null=True, blank=True, verbose_name="Soubor")
    
    class Meta:
        verbose_name = "Pravidla"
        verbose_name_plural = "Pravidla"


class EquipmentItem(models.Model):
    name = models.CharField(max_length=200, verbose_name="Název")
    category = models.CharField(max_length=100, verbose_name="Kategorie")
    description = models.TextField(blank=True, verbose_name="Popis")
    approximate_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Orientační cena")
    purchase_link = models.URLField(blank=True, verbose_name="Odkaz na nákup")
    image = models.ImageField(upload_to='equipment/', null=True, blank=True, verbose_name="Obrázek")
    
    class Meta:
        verbose_name = "Vybavení"
        verbose_name_plural = "Vybavení"
        ordering = ['category', 'name']


class UserEquipment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='equipment', verbose_name="Uživatel")
    equipment = models.ForeignKey(EquipmentItem, on_delete=models.CASCADE, verbose_name="Vybavení")
    is_owned = models.BooleanField(default=False, verbose_name="Vlastním")
    purchase_date = models.DateField(null=True, blank=True, verbose_name="Datum nákupu")
    
    class Meta:
        verbose_name = "Vybavení uživatele"
        verbose_name_plural = "Vybavení uživatelů"
        unique_together = ['user', 'equipment']

