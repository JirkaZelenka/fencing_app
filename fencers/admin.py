from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Club, FencerProfile, Tournament, TournamentParticipation,
    TrainingNote, CircuitTraining, CircuitSong, EventPhoto,
    CalendarEvent, EventReaction, PaymentStatus, GlossaryTerm,
    GuideVideo, RulesDocument, EquipmentItem, UserEquipment
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
    list_display = ['user', 'club', 'phone', 'get_user_email']
    list_filter = ['club']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone']
    autocomplete_fields = ['user']
    fields = ('user', 'club', 'phone')
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_member_count']
    search_fields = ['name']
    
    def get_member_count(self, obj):
        return obj.fencerprofile_set.count()
    get_member_count.short_description = 'Počet členů'


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'location', 'is_internal']
    list_filter = ['is_internal', 'date']
    search_fields = ['name', 'location']
    date_hierarchy = 'date'


@admin.register(TournamentParticipation)
class TournamentParticipationAdmin(admin.ModelAdmin):
    list_display = ['fencer', 'tournament', 'position', 'wins', 'losses']
    list_filter = ['tournament', 'tournament__date']
    search_fields = ['fencer__username', 'fencer__first_name', 'fencer__last_name', 'tournament__name']


@admin.register(TrainingNote)
class TrainingNoteAdmin(admin.ModelAdmin):
    list_display = ['fencer', 'date', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['fencer__username', 'notes']


@admin.register(CircuitTraining)
class CircuitTrainingAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']


@admin.register(CircuitSong)
class CircuitSongAdmin(admin.ModelAdmin):
    list_display = ['name', 'circuit', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['name']


@admin.register(EventPhoto)
class EventPhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_date', 'uploaded_by', 'is_featured']
    list_filter = ['is_featured', 'event_date', 'uploaded_at']
    search_fields = ['title', 'description']


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'location']
    list_filter = ['start_date']
    search_fields = ['title', 'description', 'location']


@admin.register(EventReaction)
class EventReactionAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'will_attend', 'created_at']
    list_filter = ['will_attend', 'created_at']
    search_fields = ['event__title', 'user__username']


@admin.register(PaymentStatus)
class PaymentStatusAdmin(admin.ModelAdmin):
    list_display = ['fencer', 'is_paid', 'payment_date', 'amount']
    list_filter = ['is_paid', 'payment_date']
    search_fields = ['fencer__username']


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
    list_display = ['user', 'equipment', 'is_owned', 'purchase_date']
    list_filter = ['is_owned', 'purchase_date']
    search_fields = ['user__username', 'equipment__name']

