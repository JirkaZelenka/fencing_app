from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Club, FencerProfile, Event, EventParticipation,
    TrainingNote, CircuitTraining, CircuitSong, EventPhoto,
    EventReaction, PaymentStatus, GlossaryTerm,
    GuideVideo, RulesDocument, EquipmentItem, UserEquipment,
    PhotoAlbum, SubAlbum, PhotoLike
)


class FencerProfileInline(admin.StackedInline):
    model = FencerProfile
    can_delete = False
    verbose_name_plural = 'Profil šermíře'
    fields = ('club', 'phone')


class UserAdmin(BaseUserAdmin):
    inlines = (FencerProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_club', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    def get_club(self, obj):
        if hasattr(obj, 'fencer_profile') and obj.fencer_profile.club:
            return obj.fencer_profile.club.name
        return '-'
    get_club.short_description = 'Klub'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(FencerProfile)
class FencerProfileAdmin(admin.ModelAdmin):
    list_display = ['get_display_name', 'user', 'club', 'phone', 'get_user_email', 'is_matched']
    list_filter = ['club', 'user']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email', 'first_name', 'last_name', 'email', 'phone']
    autocomplete_fields = ['user']
    fields = ('user', 'club', 'phone', 'first_name', 'last_name', 'email')
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
    
    def get_display_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name or f"Profil #{obj.id}"
    get_display_name.short_description = 'Jméno'
    
    def get_user_email(self, obj):
        if obj.user:
            return obj.user.email
        return obj.email or '-'
    get_user_email.short_description = 'Email'
    
    def is_matched(self, obj):
        return bool(obj.user)
    is_matched.short_description = 'Přiřazeno'
    is_matched.boolean = True


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_member_count']
    search_fields = ['name']
    
    def get_member_count(self, obj):
        return obj.fencerprofile_set.count()
    get_member_count.short_description = 'Počet členů'


@admin.register(EventParticipation)
class EventParticipationAdmin(admin.ModelAdmin):
    list_display = ['get_fencer_name', 'event', 'position', 'wins', 'losses']
    list_filter = ['event', 'event__start_date']
    search_fields = ['fencer__user__username', 'fencer__user__first_name', 'fencer__user__last_name', 'fencer__first_name', 'fencer__last_name', 'event__title']
    autocomplete_fields = ['fencer']
    
    def get_fencer_name(self, obj):
        if obj.fencer.user:
            return obj.fencer.user.get_full_name() or obj.fencer.user.username
        return f"{obj.fencer.first_name} {obj.fencer.last_name}".strip() or f"Profil #{obj.fencer.id}"
    get_fencer_name.short_description = 'Šermíř'


@admin.register(TrainingNote)
class TrainingNoteAdmin(admin.ModelAdmin):
    list_display = ['get_fencer_name', 'date', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['fencer__user__username', 'fencer__first_name', 'fencer__last_name', 'notes']
    autocomplete_fields = ['fencer']
    
    def get_fencer_name(self, obj):
        if obj.fencer.user:
            return obj.fencer.user.get_full_name() or obj.fencer.user.username
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
    list_filter = ['created_at', 'event__start_date']
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
    list_display = ['photo', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['photo__title', 'user__username']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'location', 'event_type']
    list_filter = ['event_type', 'start_date']
    search_fields = ['title', 'description', 'location']


@admin.register(EventReaction)
class EventReactionAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'will_attend', 'created_at']
    list_filter = ['will_attend', 'created_at']
    search_fields = ['event__title', 'user__username']


@admin.register(PaymentStatus)
class PaymentStatusAdmin(admin.ModelAdmin):
    list_display = ['get_fencer_name', 'is_paid', 'payment_date', 'amount']
    list_filter = ['is_paid', 'payment_date']
    search_fields = ['fencer__user__username', 'fencer__first_name', 'fencer__last_name']
    autocomplete_fields = ['fencer']
    
    def get_fencer_name(self, obj):
        if obj.fencer.user:
            return obj.fencer.user.get_full_name() or obj.fencer.user.username
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


@admin.register(UserEquipment)
class UserEquipmentAdmin(admin.ModelAdmin):
    list_display = ['get_fencer_name', 'equipment', 'is_owned', 'purchase_date']
    list_filter = ['is_owned', 'purchase_date']
    search_fields = ['fencer__user__username', 'fencer__first_name', 'fencer__last_name', 'equipment__name']
    autocomplete_fields = ['fencer', 'equipment']
    
    def get_fencer_name(self, obj):
        if obj.fencer.user:
            return obj.fencer.user.get_full_name() or obj.fencer.user.username
        return f"{obj.fencer.first_name} {obj.fencer.last_name}".strip() or f"Profil #{obj.fencer.id}"
    get_fencer_name.short_description = 'Šermíř'
