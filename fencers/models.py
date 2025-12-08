from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.urls import reverse


class UserManager(BaseUserManager):
    """Custom user manager for User model without first_name/last_name"""
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email) if email else None
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with only username, email, and admin fields"""
    username = models.CharField(max_length=150, unique=True, verbose_name="Uživatelské jméno")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    is_staff = models.BooleanField(default=False, verbose_name="Je zaměstnanec")
    is_active = models.BooleanField(default=True, verbose_name="Je aktivní")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Datum registrace")
    last_login = models.DateTimeField(blank=True, null=True, verbose_name="Poslední přihlášení")

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []  # email is optional

    class Meta:
        verbose_name = "Uživatel"
        verbose_name_plural = "Uživatelé"
        db_table = 'auth_user'  # Use same table name for compatibility

    def get_full_name(self):
        """Returns username since we don't have first_name/last_name.
        Use fencer_profile.get_full_name() for actual name."""
        return self.username
    
    def __str__(self):
        return self.username


class Club(models.Model):
    name = models.CharField(max_length=200, verbose_name="Název klubu")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Klub"
        verbose_name_plural = "Kluby"


class FencerProfile(models.Model):
    class Gender(models.TextChoices):
        MALE = 'M', "M"
        FEMALE = 'Z', "Ž"
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fencer_profile', null=True, blank=True, verbose_name="Uživatel")
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Klub")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        blank=True,
        null=True,
        verbose_name="Pohlaví"
    )
    # Optional fields to help identify the profile before user matching
    first_name = models.CharField(max_length=150, blank=True, verbose_name="Jméno")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Příjmení")
    birth_year = models.IntegerField(null=True, blank=True, verbose_name="Rok narození")
    
    def get_full_name(self):
        """Returns full name as 'Jméno Příjmení'"""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_paired(self):
        """Returns True if this fencer profile is paired with a user (1:1 relationship)"""
        return self.user is not None
    
    def __str__(self):
        if self.user:
            # Use profile name if available, otherwise username
            name = f"{self.first_name} {self.last_name}".strip() if (self.first_name or self.last_name) else self.user.username
            return f"{name} ({self.club})"
        name = f"{self.first_name} {self.last_name}".strip() or "Nepřiřazený profil"
        return f"{name} ({self.club})"
    
    class Meta:
        verbose_name = "Profil šermíře"
        verbose_name_plural = "Profily šermířů"


class Event(models.Model):
    class EventType(models.TextChoices):
        TOURNAMENT = 'tournament', "Turnaj"
        HUMANITARIAN = 'humanitarian', "Hum. turnaj"
        OTHER = 'other', "Ostatní akce"
    
    class Gender(models.TextChoices):
        MALE = 'M', "M"
        FEMALE = 'Z', "Ž"
        ALL = 'V', "Vše"

    title = models.CharField(max_length=200, verbose_name="Název")
    description = models.TextField(blank=True, verbose_name="Popis")
    date = models.DateField(verbose_name="Datum")
    location = models.CharField(max_length=200, blank=True, verbose_name="Místo")
    external_link = models.URLField(blank=True, verbose_name="Externí odkaz (czechfencing)")
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.OTHER,
        verbose_name="Typ akce",
    )
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        default=Gender.ALL,
        verbose_name="Pohlaví"
    )
    participants_count = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Počet účastníků",
        help_text="Povinné pro Turnaj a Hum. turnaj"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Require participants_count for tournament and humanitarian events
        if self.event_type in [self.EventType.TOURNAMENT, self.EventType.HUMANITARIAN]:
            if not self.participants_count or self.participants_count <= 0:
                raise ValidationError({
                    'participants_count': 'Počet účastníků je povinný pro Turnaj a Hum. turnaj a musí být větší než 0.'
                })
    
    class Meta:
        verbose_name = "Akce"
        verbose_name_plural = "Akce"
        ordering = ['date']

    def __str__(self):
        return f"{self.title} ({self.date:%d.%m.%Y})"


class EventParticipation(models.Model):
    fencer = models.ForeignKey(FencerProfile, on_delete=models.CASCADE, related_name='event_participations', verbose_name="Šermíř")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participations', verbose_name="Akce")
    position = models.IntegerField(null=True, blank=True, verbose_name="Umístění")
    wins = models.IntegerField(default=0, verbose_name="Výhry")
    losses = models.IntegerField(default=0, verbose_name="Prohry")
    touches_scored = models.IntegerField(default=0, verbose_name="Zasazené zásahy")
    touches_received = models.IntegerField(default=0, verbose_name="Obdržené zásahy")
    points = models.FloatField(null=True, blank=True, verbose_name="Body")
    
    class Meta:
        verbose_name = "Účast na akci"
        verbose_name_plural = "Účasti na akcích"
        unique_together = ['fencer', 'event']
        ordering = ['-event__date']
    
    def get_percentile(self):
        """Calculate percentile: (position / participants_count) * 100"""
        if not self.position or not self.event.participants_count:
            return None
        if self.event.participants_count <= 0:
            return None
        percentile = (self.position / self.event.participants_count) * 100
        return round(percentile, 1)


class TrainingNote(models.Model):
    fencer = models.ForeignKey(FencerProfile, on_delete=models.CASCADE, related_name='training_notes', verbose_name="Šermíř")
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
    created_by = models.ForeignKey(FencerProfile, on_delete=models.CASCADE, related_name='circuit_trainings', verbose_name="Vytvořil")
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
        ordering = ['-event__date']
    
    def __str__(self):
        return f"Album: {self.event.title}"
    
    @property
    def date(self):
        return self.event.date


class SubAlbum(models.Model):
    album = models.ForeignKey(PhotoAlbum, on_delete=models.CASCADE, related_name='subalbums', verbose_name="Album")
    name = models.CharField(max_length=200, verbose_name="Název")
    created_by = models.ForeignKey(FencerProfile, on_delete=models.SET_NULL, null=True, verbose_name="Vytvořil")
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
    uploaded_by = models.ForeignKey(FencerProfile, on_delete=models.SET_NULL, null=True, verbose_name="Nahrál")
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
    
    def is_liked_by_fencer(self, fencer):
        """Check if a fencer has liked this photo"""
        if not fencer:
            return False
        return self.likes.filter(fencer=fencer).exists()


class PhotoLike(models.Model):
    photo = models.ForeignKey(EventPhoto, on_delete=models.CASCADE, related_name='likes', verbose_name="Fotka")
    fencer = models.ForeignKey(FencerProfile, on_delete=models.CASCADE, related_name='photo_likes', verbose_name="Šermíř")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Líbí se mi"
        verbose_name_plural = "Líbí se mi"
        unique_together = ['photo', 'fencer']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.fencer} likes {self.photo.title}"


class EventReaction(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reactions', verbose_name="Akce")
    fencer = models.ForeignKey(FencerProfile, on_delete=models.CASCADE, related_name='event_reactions', verbose_name="Šermíř")
    will_attend = models.BooleanField(default=False, verbose_name="Zúčastním se")
    comment = models.TextField(blank=True, verbose_name="Komentář")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Reakce na akci"
        verbose_name_plural = "Reakce na akce"
        unique_together = ['event', 'fencer']


class PaymentStatus(models.Model):
    fencer = models.OneToOneField(FencerProfile, on_delete=models.CASCADE, related_name='payment_status', verbose_name="Šermíř")
    is_paid = models.BooleanField(default=False, verbose_name="Zaplaceno")
    payment_date = models.DateField(null=True, blank=True, verbose_name="Datum platby")
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Částka")
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True, verbose_name="QR kód")
    payment_info = models.TextField(blank=True, verbose_name="Informace k platbě")
    payment_notified = models.BooleanField(default=False, verbose_name="Upozornění odesláno")
    
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
    shop_5mfencing_link = models.URLField(blank=True, verbose_name="Odkaz 5MFencing")
    shop_5mfencing_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Cena 5MFencing")
    shop_rubyfencing_link = models.URLField(blank=True, verbose_name="Odkaz Rubyfencing")
    shop_rubyfencing_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Cena Rubyfencing")
    
    class Meta:
        verbose_name = "Vybavení"
        verbose_name_plural = "Vybavení"
        ordering = ['category', 'name']


class UserEquipment(models.Model):
    fencer = models.ForeignKey(FencerProfile, on_delete=models.CASCADE, related_name='equipment', verbose_name="Šermíř")
    equipment = models.ForeignKey(EquipmentItem, on_delete=models.CASCADE, verbose_name="Vybavení")
    is_owned = models.BooleanField(default=False, verbose_name="Vlastním")
    purchase_date = models.DateField(null=True, blank=True, verbose_name="Datum nákupu")
    
    class Meta:
        verbose_name = "Vybavení uživatele"
        verbose_name_plural = "Vybavení uživatelů"
        unique_together = ['fencer', 'equipment']


class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Nadpis")
    text = models.TextField(verbose_name="Text")
    date = models.DateField(verbose_name="Datum")
    created_by = models.ForeignKey(FencerProfile, on_delete=models.SET_NULL, null=True, verbose_name="Vytvořil")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Vytvořeno")
    
    class Meta:
        verbose_name = "Novinka"
        verbose_name_plural = "Novinky"
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.date})"


class NewsRead(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='reads', verbose_name="Novinka")
    fencer = models.ForeignKey(FencerProfile, on_delete=models.CASCADE, related_name='news_reads', verbose_name="Šermíř")
    read_at = models.DateTimeField(auto_now_add=True, verbose_name="Přečteno")
    
    class Meta:
        verbose_name = "Přečtená novinka"
        verbose_name_plural = "Přečtené novinky"
        unique_together = ['news', 'fencer']
        ordering = ['-read_at']
    
    def __str__(self):
        return f"{self.fencer} read {self.news.title}"

