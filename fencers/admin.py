from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django import forms
from .models import (
    User, Club, FencerProfile, Event, EventParticipation,
    TrainingNote, CircuitTraining, CircuitSong, EventPhoto,
    EventReaction, PaymentStatus, GlossaryTerm,
    GuideVideo, RulesDocument, EquipmentItem, UserEquipment,
    PhotoAlbum, SubAlbum, PhotoLike, News, NewsRead, Badge
)

# Ensure User model is loaded before admin tries to reference it
# This fixes the 'fencers.user' vs 'fencers.User' issue
_ = get_user_model()


class IsPairedFilter(admin.SimpleListFilter):
    """Custom filter for is_paired status"""
    title = 'Přiřazeno'
    parameter_name = 'is_paired'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Ano'),
            ('no', 'Ne'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(user__isnull=False)
        if self.value() == 'no':
            return queryset.filter(user__isnull=True)


class FencerProfileInline(admin.StackedInline):
    model = FencerProfile
    can_delete = False
    verbose_name_plural = 'Profil šermíře'
    fields = ('club', 'phone', 'gender')


class UserChangeForm(forms.ModelForm):
    """Custom form for changing user"""
    class Meta:
        model = User
        fields = '__all__'


class UserCreationForm(forms.ModelForm):
    """Custom form for creating user"""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.first_name = user.first_name or ""
        user.last_name = user.last_name or ""
        if commit:
            user.save()
        return user


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    inlines = (FencerProfileInline,)
    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email')
    
    # Only show username, email, and admin-related fields
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login',)}),
    )
    readonly_fields = ('date_joined', 'last_login')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )


# Register custom User model
# Since we're using AUTH_USER_MODEL, Django won't auto-register the default User model
# So we just register our custom User model directly
admin.site.register(User, UserAdmin)


@admin.register(FencerProfile)
class FencerProfileAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'user', 'club', 'gender', 'birth_year', 'phone', 'get_user_email', 'is_paired']
    list_filter = ['club', 'gender', 'badges', IsPairedFilter]
    search_fields = ['user__username', 'user__email', 'first_name', 'last_name', 'phone']
    autocomplete_fields = ['user']
    filter_horizontal = ('badges',)
    fields = ('user', 'club', 'phone', 'gender', 'birth_year', 'first_name', 'last_name', 'profile_photo', 'badges')
    actions = ['unpair_selected_profiles']
    
    def unpair_selected_profiles(self, request, queryset):
        """Admin action to unpair selected profiles from their users"""
        count = 0
        for profile in queryset:
            if profile.user:
                profile.user = None
                profile.save()
                count += 1
        self.message_user(request, f'{count} profilů bylo odpojeno od uživatelů.')
    unpair_selected_profiles.short_description = 'Odpojit vybrané profily od uživatelů'
    
    def get_user_email(self, obj):
        if obj.user:
            return obj.user.email
        return '-'
    get_user_email.short_description = 'Email'
    
    def is_paired(self, obj):
        return obj.is_paired
    is_paired.short_description = 'Přiřazeno'
    is_paired.boolean = True


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_member_count']
    search_fields = ['name']
    
    def get_member_count(self, obj):
        return obj.fencerprofile_set.count()
    get_member_count.short_description = 'Počet členů'


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon_class', 'color', 'tooltip']
    search_fields = ['name', 'tooltip', 'icon_class']
    fields = ('name', 'icon_class', 'color', 'tooltip')


@admin.register(EventParticipation)
class EventParticipationAdmin(admin.ModelAdmin):
    list_display = ['get_fencer_name', 'event', 'position', 'wins', 'losses', 'points', 'is_hall_of_fame']
    list_filter = ['event', 'event__date', 'is_hall_of_fame']
    search_fields = ['fencer__user__username', 'fencer__user__email', 'fencer__first_name', 'fencer__last_name', 'event__title']
    autocomplete_fields = ['fencer']
    
    def get_fencer_name(self, obj):
        if obj.fencer.user:
            return obj.fencer.user.username
        return f"{obj.fencer.first_name} {obj.fencer.last_name}".strip() or f"Profil #{obj.fencer.id}"
    get_fencer_name.short_description = 'Šermíř'


@admin.register(TrainingNote)
class TrainingNoteAdmin(admin.ModelAdmin):
    list_display = ['get_fencer_name', 'date', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['fencer__user__username', 'fencer__user__email', 'fencer__first_name', 'fencer__last_name', 'notes']
    autocomplete_fields = ['fencer']
    
    def get_fencer_name(self, obj):
        if obj.fencer.user:
            return obj.fencer.user.username
        return f"{obj.fencer.first_name} {obj.fencer.last_name}".strip() or f"Profil #{obj.fencer.id}"
    get_fencer_name.short_description = 'Šermíř'


@admin.register(CircuitTraining)
class CircuitTrainingAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description']


@admin.register(CircuitSong)
class CircuitSongAdmin(admin.ModelAdmin):
    list_display = ['name', 'circuit', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['name']


@admin.register(PhotoAlbum)
class PhotoAlbumAdmin(admin.ModelAdmin):
    list_display = ['event', 'date', 'created_at']
    list_filter = ['created_at', 'event__date']
    search_fields = ['event__title']
    readonly_fields = ['created_at']


@admin.register(SubAlbum)
class SubAlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'album', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'album__event__title']
    readonly_fields = ['created_at']


@admin.register(EventPhoto)
class EventPhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_date', 'uploaded_by', 'is_featured', 'subalbum']
    list_filter = ['is_featured', 'event_date', 'uploaded_at']
    search_fields = ['title', 'description']


@admin.register(PhotoLike)
class PhotoLikeAdmin(admin.ModelAdmin):
    list_display = ['photo', 'fencer', 'created_at']
    list_filter = ['created_at']
    search_fields = ['photo__title', 'fencer__user__username', 'fencer__user__email', 'fencer__first_name', 'fencer__last_name']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'location', 'event_type', 'gender', 'participants_count']
    list_filter = ['event_type', 'date', 'gender']
    search_fields = ['title', 'description', 'location']
    fields = ['title', 'description', 'date', 'location', 'event_type', 'gender', 'participants_count', 'external_link']
    
    def save_model(self, request, obj, form, change):
        # Validate participants_count for tournament and humanitarian events
        if obj.event_type in [Event.EventType.TOURNAMENT, Event.EventType.HUMANITARIAN]:
            if not obj.participants_count or obj.participants_count <= 0:
                from django.contrib import messages
                messages.error(request, 'Počet účastníků je povinný pro Turnaj a UŠL - univerzitní liga a musí být větší než 0.')
                return
        obj.save()


@admin.register(EventReaction)
class EventReactionAdmin(admin.ModelAdmin):
    list_display = ['event', 'fencer', 'will_attend', 'created_at']
    list_filter = ['will_attend', 'created_at']
    search_fields = ['event__title', 'fencer__user__username', 'fencer__user__email', 'fencer__first_name', 'fencer__last_name']


@admin.register(PaymentStatus)
class PaymentStatusAdmin(admin.ModelAdmin):
    list_display = ['get_fencer_name', 'is_paid', 'payment_notified', 'payment_date', 'amount']
    list_filter = ['is_paid', 'payment_notified', 'payment_date']
    search_fields = ['fencer__user__username', 'fencer__user__email', 'fencer__first_name', 'fencer__last_name']
    autocomplete_fields = ['fencer']
    fields = ('fencer', 'is_paid', 'payment_date', 'amount', 'payment_notified', 'qr_code', 'payment_info')
    
    def get_fencer_name(self, obj):
        if obj.fencer.user:
            return obj.fencer.user.username
        return f"{obj.fencer.first_name} {obj.fencer.last_name}".strip() or f"Profil #{obj.fencer.id}"
    get_fencer_name.short_description = 'Šermíř'


@admin.register(GlossaryTerm)
class GlossaryTermAdmin(admin.ModelAdmin):
    list_display = ['term', 'definition']
    search_fields = ['term', 'definition']


@admin.register(GuideVideo)
class GuideVideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'category']
    list_filter = ['category']
    search_fields = ['title', 'description']


@admin.register(RulesDocument)
class RulesDocumentAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title', 'content']


@admin.register(EquipmentItem)
class EquipmentItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'approximate_price']
    list_filter = ['category']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Základní informace', {
            'fields': ('name', 'category', 'description', 'image')
        }),
        ('Ceny', {
            'fields': ('approximate_price', 'purchase_link')
        }),
        ('5MFencing', {
            'fields': ('shop_5mfencing_link', 'shop_5mfencing_price')
        }),
        ('Rubyfencing', {
            'fields': ('shop_rubyfencing_link', 'shop_rubyfencing_price')
        }),
    )


@admin.register(UserEquipment)
class UserEquipmentAdmin(admin.ModelAdmin):
    list_display = ['get_fencer_name', 'equipment', 'is_owned', 'purchase_date']
    list_filter = ['is_owned', 'purchase_date']
    search_fields = ['fencer__user__username', 'fencer__first_name', 'fencer__last_name', 'equipment__name']
    autocomplete_fields = ['fencer', 'equipment']
    
    def get_fencer_name(self, obj):
        if obj.fencer.user:
            return obj.fencer.user.username
        return f"{obj.fencer.first_name} {obj.fencer.last_name}".strip() or f"Profil #{obj.fencer.id}"
    get_fencer_name.short_description = 'Šermíř'


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'created_by', 'created_at', 'get_read_count']
    list_filter = ['date', 'created_at']
    search_fields = ['title', 'text']
    fields = ('title', 'text', 'date', 'created_by')
    readonly_fields = ['created_at']
    
    def get_read_count(self, obj):
        return obj.reads.count()
    get_read_count.short_description = 'Přečteno'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by on creation
            # Get or create fencer profile for the user
            if hasattr(request.user, 'fencer_profile') and request.user.fencer_profile:
                obj.created_by = request.user.fencer_profile
        super().save_model(request, obj, form, change)


@admin.register(NewsRead)
class NewsReadAdmin(admin.ModelAdmin):
    list_display = ['news', 'fencer', 'read_at']
    list_filter = ['read_at']
    search_fields = ['news__title', 'fencer__user__username', 'fencer__user__email', 'fencer__first_name', 'fencer__last_name']
    readonly_fields = ['read_at']
