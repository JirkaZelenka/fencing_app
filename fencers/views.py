import re
import random
import string
from datetime import date, timedelta, datetime
from urllib.parse import urlencode

from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db.models import Q, Count, Avg, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import (
    FencerProfile, Event, EventParticipation, TrainingNote,
    CircuitTraining, CircuitSong, EventPhoto, EventReaction,
    PaymentStatus, GlossaryTerm, GuideVideo, RulesDocument, EquipmentItem,
    UserEquipment, Club, PhotoAlbum, SubAlbum, PhotoLike
)
from .forms import TrainingNoteForm, CircuitTrainingForm, EventReactionForm, RegistrationForm


# Slots shown around the figurine in the equipment view.
# Keywords are used to automatically map the slot to a concrete EquipmentItem.

#? "icon_class": "bi-mask", -> was working for previous bootstrap library with BI prefix
#? now it is "icon": "icon" with Tabler prefix = "ti" skipped
#? "https://tabler.io/icons/icon/shoe"

EQUIPMENT_LOADOUT_SLOTS = [
    {
        "id": "mask",
        "label": "Maska",
        "icon": "helmet",
        "keywords": ["mask", "maska"],
        "position": "top",
        "fallback_description": "Maska musí splňovat X-N a další ochranné parametry.",
    },
    {
        "id": "jacket",
        "label": "Vesta",
        "icon": "jacket",
        "keywords": ["vesta", "jacket"],
        "position": "left",
        "fallback_description": "Standardní X-N vesta pro kordisty.",
    },
    {
        "id": "plastron",
        "label": "Podvesta",
        "icon": "shield-down",
        "keywords": ["podvesta", "plastron"],
        "position": "left",
        "fallback_description": "Vnitřní ochrana paže a trupu, povinná na soutěžích.",
    },
    {
        "id": "breeches",
        "label": "Kalhoty",
        "icon": "hanger-2",
        "keywords": ["kalhoty", "breeches"],
        "position": "left",
        "fallback_description": "Kalhoty pod kolena s vysokou odolností proti průrazu, standard X-N.",
    },
    {
        "id": "glove",
        "label": "Rukavice",
        "icon": "hand-three-fingers",
        "keywords": ["rukavice", "glove"],
        "position": "right",
        "fallback_description": "Rukavice s prodlouženou manžetou pro kord.",
    },
    {
        "id": "socks_shoes",
        "label": "Ponožky & boty",
        "icon": "shoe",
        "keywords": ["boty", "obuv", "socks", "ponožky", "shoes"],
        "position": "bottom",
        "fallback_description": "Vysoké podkolenky a šermířské boty s boční výztuží pro výpady.",
    },
    {
        "id": "tools",
        "label": "Nářadí",
        "icon": "tool",
        "keywords": ["nářadí", "tools", "tool"],
        "position": "bottom",
        "fallback_description": "Nářadí pro údržbu a opravy zbraně.",
    },
    {
        "id": "weapon",
        "label": "Kord",
        "icon": "sword",
        "keywords": ["kord", "epee", "zbraň", "weapon"],
        "position": "right",
        "fallback_description": "Vyvážený závodní kord s elektrickým hrotem.",
    },
    {
        "id": "body_cord",
        "label": "Šňůra",
        "icon": "plug-connected",
        "keywords": ["cord", "kabel", "šňůra"],
        "position": "right",
        "fallback_description": "Třívodičový kabel spojující zbraň s aparátem.",
    },
    {
        "id": "chest_guard",
        "label": "Chránič hrudi",
        "icon": "shield-chevron",
        "keywords": ["hruď", "chránič", "prsa", "chest", "guard"],
        "position": "top",
        "fallback_description": "Plastový chránič hrudi, povinný pro ženy, volitelný pro muže.",
    },
]


EVENT_TYPE_ORDER = [
    Event.EventType.TOURNAMENT,
    Event.EventType.HUMANITARIAN,
    Event.EventType.OTHER,
]

EVENT_TYPE_META = {
    Event.EventType.TOURNAMENT: {
        'label': "Turnaj",
        'class_suffix': 'tournament',
    },
    Event.EventType.HUMANITARIAN: {
        'label': "Hum. turnaj",
        'class_suffix': 'humanitarian',
    },
    Event.EventType.OTHER: {
        'label': "Ostatní",
        'class_suffix': 'other',
    },
}


def get_event_meta(event_type):
    return EVENT_TYPE_META.get(event_type, EVENT_TYPE_META[Event.EventType.OTHER])


def ensure_aware(dt: datetime) -> datetime:
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def serialize_event(event, reaction=None):
    meta = get_event_meta(event.event_type)
    has_time = event.start_date.time() != datetime.min.time()
    return {
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'start': event.start_date,
        'end': event.end_date,
        'location': event.location,
        'external_link': event.external_link,
        'event_type': event.event_type,
        'type_label': meta['label'],
        'class_suffix': meta['class_suffix'],
        'source': 'event',
        'allows_reaction': True,
        'user_reaction': reaction,
        'has_time': has_time,
    }


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # Check if user needs to match a profile
            if not hasattr(user, 'fencer_profile') or user.fencer_profile is None:
                return redirect('match_profile')
            return redirect('home')
        else:
            messages.error(request, 'Neplatné přihlašovací údaje.')
    
    return render(request, 'fencers/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Účet byl úspěšně vytvořen! Nyní se prosím přiřaďte k jednomu z předpřipravených profilů.')
            return redirect('match_profile')
    else:
        form = RegistrationForm()
    
    return render(request, 'fencers/register.html', {'form': form})


@login_required
def match_profile(request):
    """Allow user to match themselves to a predefined FencerProfile"""
    # Check if user already has a profile
    if hasattr(request.user, 'fencer_profile') and request.user.fencer_profile:
        messages.info(request, 'Již máte přiřazený profil.')
        return redirect('home')
    
    # Get all unmatched profiles (profiles without a user)
    unmatched_profiles = FencerProfile.objects.filter(user__isnull=True).select_related('club').order_by('last_name', 'first_name')
    
    if request.method == 'POST':
        profile_id = request.POST.get('profile_id')
        try:
            profile = FencerProfile.objects.get(id=profile_id, user__isnull=True)
            # Link the user to this profile
            profile.user = request.user
            profile.save()
            
            # Update user's name if profile has name info
            if profile.first_name and not request.user.first_name:
                request.user.first_name = profile.first_name
            if profile.last_name and not request.user.last_name:
                request.user.last_name = profile.last_name
            if profile.email and not request.user.email:
                request.user.email = profile.email
            request.user.save()
            
            messages.success(request, f'Profil byl úspěšně přiřazen! Vítejte, {request.user.get_full_name() or request.user.username}.')
            return redirect('home')
        except FencerProfile.DoesNotExist:
            messages.error(request, 'Vybraný profil neexistuje nebo již byl přiřazen.')
    
    context = {
        'unmatched_profiles': unmatched_profiles,
    }
    return render(request, 'fencers/match_profile.html', context)


@login_required
@require_POST
def unpair_profile(request):
    """Allow user to unpair themselves from their FencerProfile"""
    if not hasattr(request.user, 'fencer_profile') or request.user.fencer_profile is None:
        messages.error(request, 'Nemáte přiřazený profil.')
        return redirect('home')
    
    profile = request.user.fencer_profile
    profile.user = None
    profile.save()
    
    messages.success(request, 'Profil byl úspěšně odpojen. Můžete se znovu přiřadit k jinému profilu.')
    return redirect('match_profile')


@login_required
def home(request):
    # Redirect to profile matching if user doesn't have a profile
    if not hasattr(request.user, 'fencer_profile') or request.user.fencer_profile is None:
        return redirect('match_profile')
    return redirect('about_me')


@login_required
def about_me(request):
    user = request.user
    profile = getattr(user, 'fencer_profile', None)
    if not profile:
        return redirect('match_profile')
    
    view_param = request.GET.get('view', 'me')
    
    tournament_participations = EventParticipation.objects.filter(
        fencer=profile,
        event__event_type=Event.EventType.TOURNAMENT
    ).select_related('event')
    
    # Basic statistics (only tournament-type events count here)
    total_tournaments = tournament_participations.count()
    total_wins = tournament_participations.aggregate(Sum('wins'))['wins__sum'] or 0
    total_losses = tournament_participations.aggregate(Sum('losses'))['losses__sum'] or 0
    total_touches_scored = tournament_participations.aggregate(Sum('touches_scored'))['touches_scored__sum'] or 0
    total_touches_received = tournament_participations.aggregate(Sum('touches_received'))['touches_received__sum'] or 0
    win_rate = (total_wins / (total_wins + total_losses) * 100) if (total_wins + total_losses) > 0 else 0
    
    # Filter events: show events that match user's gender or are "Vše" (All)
    all_events = Event.objects.all().order_by('-start_date')
    if profile.gender:
        # Show events that match user's gender or are "Vše"
        all_events = all_events.filter(
            Q(gender=Event.Gender.ALL) | Q(gender=profile.gender)
        )
    else:
        # If user has no gender set, show all events
        pass
    
    participation_lookup = {
        p.event_id: p for p in EventParticipation.objects.filter(fencer=profile).select_related('event')
    }
    event_reactions = set(
        EventReaction.objects.filter(user=user, will_attend=True).values_list('event_id', flat=True)
    )
    
    combined_items = []
    for event in all_events:
        meta = get_event_meta(event.event_type)
        participation = participation_lookup.get(event.id)
        is_participating = bool(participation or (event.id in event_reactions))
        combined_items.append({
            'event_type': event.event_type,
            'type_label': meta['label'],
            'class_suffix': meta['class_suffix'],
            'name': event.title,
            'date': event.start_date.date(),
            'location': event.location,
            'is_participating': is_participating,
            'position': participation.position if participation else None,
        })
    combined_items.sort(key=lambda x: x['date'], reverse=True)
    
    club_fencers_m = club_fencers_z = club_fencers_undefined = FencerProfile.objects.none()
    if profile.club:
        club_members = FencerProfile.objects.filter(club=profile.club).select_related('user')
        club_fencers_m = club_members.filter(gender=FencerProfile.Gender.MALE).order_by('last_name', 'first_name')
        club_fencers_z = club_members.filter(gender=FencerProfile.Gender.FEMALE).order_by('last_name', 'first_name')
        club_fencers_undefined = club_members.filter(gender__isnull=True).order_by('last_name', 'first_name')
    
    context = {
        'profile': profile,
        'participations': tournament_participations,
        'combined_items': combined_items,
        'total_tournaments': total_tournaments,
        'total_wins': total_wins,
        'total_losses': total_losses,
        'total_touches_scored': total_touches_scored,
        'total_touches_received': total_touches_received,
        'win_rate': round(win_rate, 1),
        'club_fencers_m': club_fencers_m,
        'club_fencers_z': club_fencers_z,
        'club_fencers_undefined': club_fencers_undefined,
        'initial_view': view_param,
    }
    return render(request, 'fencers/about_me.html', context)


@login_required
def statistics_individual(request):
    user = request.user
    
    # Redirect to profile matching if user doesn't have a profile
    if not hasattr(user, 'fencer_profile') or user.fencer_profile is None:
        messages.info(request, 'Nejprve se prosím přiřaďte k profilu.')
        return redirect('match_profile')
    
    profile = user.fencer_profile
    individual_participations = EventParticipation.objects.filter(fencer=profile).select_related('event')
    
    # Get user's participations in humanitarian tournaments
    humanitarian_participations = EventParticipation.objects.filter(
        fencer=profile,
        event__event_type=Event.EventType.HUMANITARIAN
    ).select_related('event').order_by('-event__start_date')
    
    club = None
    club_fencers = None
    club_participations = None
    club_humanitarian_participations = None
    
    # Get URL parameters
    view_param = request.GET.get('view', 'individual')  # 'individual' or 'club'
    tournament_filter = request.GET.get('tournament', '').strip()
    
    if profile.club:
        club = profile.club
        club_fencers = FencerProfile.objects.filter(club=profile.club).select_related('user')
        
        club_participations_qs = EventParticipation.objects.filter(
            fencer__in=club_fencers
        ).select_related('fencer', 'fencer__user', 'event')
        
        # Apply tournament filter if provided
        if tournament_filter:
            club_participations_qs = club_participations_qs.filter(event__title__icontains=tournament_filter)
        
        # Apply gender filter if provided
        gender_filter = request.GET.get('gender', '').strip()
        if gender_filter:
            if gender_filter == 'M':
                club_participations_qs = club_participations_qs.filter(event__gender=Event.Gender.MALE)
            elif gender_filter == 'Z':
                club_participations_qs = club_participations_qs.filter(event__gender=Event.Gender.FEMALE)
            elif gender_filter == 'V':
                club_participations_qs = club_participations_qs.filter(event__gender=Event.Gender.ALL)
            # If gender_filter is empty or invalid, show all
        
        club_participations = club_participations_qs
        club_humanitarian_participations = club_participations_qs.filter(
            event__event_type=Event.EventType.HUMANITARIAN
        )
    else:
        gender_filter = ''
        club_humanitarian_participations = EventParticipation.objects.none()
    
    context = {
        'participations': individual_participations,
        'humanitarian_participations': humanitarian_participations,
        'club': club,
        'club_participations': club_participations,
        'club_humanitarian_participations': club_humanitarian_participations,
        'initial_view': view_param,
        'initial_tournament_filter': tournament_filter,
        'initial_gender_filter': gender_filter if profile.club else '',
    }
    return render(request, 'fencers/statistics_individual.html', context)


@login_required
def statistics_club(request):
    user = request.user
    profile = getattr(user, 'fencer_profile', None)
    
    if not profile or not profile.club:
        messages.info(request, 'Nemáte přiřazený klub.')
        return redirect('about_me')
    
    club_fencers = FencerProfile.objects.filter(club=profile.club).select_related('user')
    
    participations = EventParticipation.objects.filter(
        fencer__in=club_fencers
    ).select_related('fencer', 'fencer__user', 'event')
    
    # Filter by tournament name if provided
    tournament_filter = request.GET.get('tournament', '').strip()
    if tournament_filter:
        participations = participations.filter(event__title__icontains=tournament_filter)
    
    internal_participations = EventParticipation.objects.filter(
        fencer__in=club_fencers,
        event__event_type=Event.EventType.HUMANITARIAN
    ).select_related('fencer', 'fencer__user', 'event').order_by('-event__start_date')
    
    context = {
        'club': profile.club,
        'club_fencers': club_fencers,
        'participations': participations,
        'internal_participations': internal_participations,
        'tournament_filter': tournament_filter,
    }
    return render(request, 'fencers/statistics_club.html', context)


@login_required
def training_notes(request):
    user = request.user
    profile = getattr(user, 'fencer_profile', None)
    if not profile:
        messages.info(request, 'Nejprve se prosím přiřaďte k profilu.')
        return redirect('match_profile')
    
    notes = TrainingNote.objects.filter(fencer=profile).order_by('-date')
    
    if request.method == 'POST':
        form = TrainingNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.fencer = profile
            note.save()
            messages.success(request, 'Poznámka byla uložena.')
            return redirect('training_notes')
    else:
        form = TrainingNoteForm()
    
    context = {
        'notes': notes,
        'form': form,
    }
    return render(request, 'fencers/training_notes.html', context)


@login_required
def circuit_trainings(request):
    user = request.user
    # Get user's own circuits and public circuits from others
    circuits = CircuitTraining.objects.filter(
        Q(created_by=user) | Q(is_public=True)
    ).prefetch_related('songs').order_by('-created_at')
    
    if request.method == 'POST':
        form = CircuitTrainingForm(request.POST)
        if form.is_valid():
            circuit = form.save(commit=False)
            circuit.created_by = user
            circuit.save()
            messages.success(request, 'Masíčko bylo vytvořeno.')
            return redirect('circuit_trainings')
    else:
        form = CircuitTrainingForm()
    
    context = {
        'circuits': circuits,
        'form': form,
        'user': user,
    }
    return render(request, 'fencers/circuit_trainings.html', context)


@login_required
def event_photos(request):
    # Get all albums
    all_albums = PhotoAlbum.objects.all().select_related('event').order_by('-event__start_date')
    
    # Extract unique years from albums
    years = sorted(set(
        album.event.start_date.year for album in all_albums
    ), reverse=True)
    
    # Get filter year from request
    filter_year = request.GET.get('year')
    if filter_year:
        try:
            filter_year = int(filter_year)
            albums = all_albums.filter(event__start_date__year=filter_year)
        except (ValueError, TypeError):
            albums = all_albums
            filter_year = None
    else:
        albums = all_albums
        filter_year = None
    
    context = {
        'albums': albums,
        'available_years': years,
        'selected_year': filter_year,
    }
    return render(request, 'fencers/event_photos.html', context)


@login_required
def album_detail(request, album_id):
    album = get_object_or_404(PhotoAlbum.objects.select_related('event'), id=album_id)
    subalbums = album.subalbums.all().prefetch_related('photos').order_by('-created_at')
    
    # Get all photos from all subalbums for browsing
    all_photos = EventPhoto.objects.filter(subalbum__album=album).select_related('subalbum', 'subalbum__album', 'subalbum__album__event', 'uploaded_by').prefetch_related('likes').order_by('-uploaded_at')
    
    # Get user's liked photos for this album
    user_liked_photo_ids = set(
        PhotoLike.objects.filter(user=request.user, photo__in=all_photos).values_list('photo_id', flat=True)
    )
    
    context = {
        'album': album,
        'subalbums': subalbums,
        'all_photos': all_photos,
        'user_liked_photo_ids': user_liked_photo_ids,
    }
    return render(request, 'fencers/album_detail.html', context)


@login_required
@require_POST
def create_subalbum(request, album_id):
    album = get_object_or_404(PhotoAlbum, id=album_id)
    name = request.POST.get('name', '').strip()
    
    if not name:
        messages.error(request, 'Název subalba je povinný.')
        return redirect('album_detail', album_id=album_id)
    
    subalbum = SubAlbum.objects.create(
        album=album,
        name=name,
        created_by=request.user
    )
    messages.success(request, f'Subalbum "{name}" byl vytvořen.')
    return redirect('album_detail', album_id=album_id)


@login_required
@require_POST
def upload_photo(request, subalbum_id):
    subalbum = get_object_or_404(SubAlbum.objects.select_related('album'), id=subalbum_id)
    
    if 'photo' not in request.FILES:
        messages.error(request, 'Musíte vybrat fotku.')
        return redirect('album_detail', album_id=subalbum.album.id)
    
    photo_file = request.FILES['photo']
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    
    EventPhoto.objects.create(
        title=title,
        description=description,
        photo=photo_file,
        event_date=subalbum.album.event.start_date.date(),
        uploaded_by=request.user,
        subalbum=subalbum
    )
    
    messages.success(request, 'Fotka byla nahrána.')
    return redirect('album_detail', album_id=subalbum.album.id)


@login_required
@require_POST
def update_album_cover(request, album_id):
    album = get_object_or_404(PhotoAlbum, id=album_id)
    
    if 'cover_photo' not in request.FILES:
        messages.error(request, 'Musíte vybrat fotku.')
        return redirect('album_detail', album_id=album_id)
    
    album.cover_photo = request.FILES['cover_photo']
    album.save()
    
    messages.success(request, 'Obalová fotka byla aktualizována.')
    return redirect('album_detail', album_id=album_id)


@login_required
def calendar_events(request):
    import calendar
    
    # Get month and year from request, default to current month
    current_dt = timezone.now()
    try:
        year = int(request.GET.get('year', current_dt.year))
        month = int(request.GET.get('month', current_dt.month))
    except (ValueError, TypeError):
        year = current_dt.year
        month = current_dt.month
    
    # Calculate previous and next month
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    # Get first and last day of the month
    first_day = ensure_aware(datetime(year, month, 1))
    last_day_num = calendar.monthrange(year, month)[1]
    last_day = ensure_aware(datetime(year, month, last_day_num, 23, 59, 59))
    
    # Get filter year from request (for events list, not calendar month)
    filter_year = request.GET.get('filter_year')
    if filter_year:
        try:
            filter_year = int(filter_year)
        except (ValueError, TypeError):
            filter_year = None
    else:
        filter_year = None
    
    # Event type filters
    selected_types = [t for t in request.GET.getlist('types') if t in EVENT_TYPE_META]
    if not selected_types:
        selected_types = EVENT_TYPE_ORDER.copy()
    selected_types_set = set(selected_types)
    
    event_type_filters = [
        {
            'value': event_type,
            'label': EVENT_TYPE_META[event_type]['label'],
            'class_suffix': EVENT_TYPE_META[event_type]['class_suffix'],
            'checked': event_type in selected_types_set,
        }
        for event_type in EVENT_TYPE_ORDER
    ]
    
    # Build filter query for URL parameters (only event types, not year filter)
    filter_query = urlencode({'types': selected_types}, doseq=True)
    
    # Get all events in this month
    month_events = Event.objects.filter(
        start_date__gte=first_day,
        start_date__lte=last_day,
        event_type__in=selected_types_set,
    ).prefetch_related('photo_album').order_by('start_date')
    
    # Create a dictionary of events by date
    events_by_date = {}
    
    for event in month_events:
        serialized = serialize_event(event)
        # Add album info if it exists
        try:
            album = event.photo_album
            serialized['has_album'] = True
            serialized['album_id'] = album.id
        except PhotoAlbum.DoesNotExist:
            serialized['has_album'] = False
        event_date = serialized['start'].date()
        events_by_date.setdefault(event_date, []).append(serialized)
    
    for event_list in events_by_date.values():
        event_list.sort(key=lambda item: item['start'])
    
    # Generate calendar grid
    cal = calendar.monthcalendar(year, month)
    calendar_data = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(None)  # Day outside current month
            else:
                day_date = date(year, month, day)
                is_today = day_date == date.today()
                has_events = day_date in events_by_date
                day_events = events_by_date.get(day_date, [])
                week_data.append({
                    'day': day,
                    'date': day_date,
                    'is_today': is_today,
                    'has_events': has_events,
                    'events': day_events,
                })
        calendar_data.append(week_data)
    
    # Extract unique years from all events for filter buttons
    all_events_years = sorted(set(
        Event.objects.values_list('start_date__year', flat=True).distinct()
    ), reverse=True)
    
    # Get upcoming events for the list view
    now = timezone.now()
    
    upcoming_events_qs = Event.objects.filter(
        start_date__gte=now,
        event_type__in=selected_types_set,
    )
    if filter_year:
        upcoming_events_qs = upcoming_events_qs.filter(start_date__year=filter_year)
    upcoming_events_qs = upcoming_events_qs.prefetch_related('photo_album').order_by('start_date')
    
    past_events_qs = Event.objects.filter(
        start_date__lt=now,
        event_type__in=selected_types_set,
    )
    if filter_year:
        past_events_qs = past_events_qs.filter(start_date__year=filter_year)
    past_events_qs = past_events_qs.prefetch_related('photo_album').order_by('-start_date')[:30]
    
    # Get user reactions and attach to events
    reaction_dict = {}
    if request.user.is_authenticated and upcoming_events_qs:
        reactions = EventReaction.objects.filter(user=request.user, event__in=upcoming_events_qs)
        reaction_dict = {r.event_id: r for r in reactions}
    
    serialized_upcoming = []
    for event in upcoming_events_qs:
        serialized = serialize_event(event, reaction_dict.get(event.id))
        try:
            album = event.photo_album
            serialized['has_album'] = True
            serialized['album_id'] = album.id
        except PhotoAlbum.DoesNotExist:
            serialized['has_album'] = False
        serialized_upcoming.append(serialized)
    serialized_upcoming.sort(key=lambda item: item['start'])
    
    serialized_past = []
    for event in past_events_qs:
        serialized = serialize_event(event)
        try:
            album = event.photo_album
            serialized['has_album'] = True
            serialized['album_id'] = album.id
        except PhotoAlbum.DoesNotExist:
            serialized['has_album'] = False
        serialized_past.append(serialized)
    serialized_past.sort(key=lambda item: item['start'], reverse=True)
    serialized_past = serialized_past[:10]
    
    # Month names in Czech
    month_names = ['', 'Leden', 'Únor', 'Březen', 'Duben', 'Květen', 'Červen',
                   'Červenec', 'Srpen', 'Září', 'Říjen', 'Listopad', 'Prosinec']
    day_names = ['Po', 'Út', 'St', 'Čt', 'Pá', 'So', 'Ne']
    
    context = {
        'calendar_data': calendar_data,
        'year': year,
        'month': month,
        'month_name': month_names[month],
        'day_names': day_names,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'upcoming_events': serialized_upcoming,
        'past_events': serialized_past,
        'event_type_filters': event_type_filters,
        'selected_types': selected_types,
        'filter_query': filter_query,
        'available_years': all_events_years,
        'selected_filter_year': filter_year,
    }
    return render(request, 'fencers/calendar_events.html', context)


@login_required
@require_POST
def event_reaction(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    reaction, created = EventReaction.objects.get_or_create(
        event=event,
        user=request.user,
        defaults={'will_attend': False}
    )
    
    form = EventReactionForm(request.POST, instance=reaction)
    if form.is_valid():
        form.save()
        messages.success(request, 'Vaše reakce byla uložena.')
    else:
        messages.error(request, 'Chyba při ukládání reakce.')
    
    return redirect('calendar_events')


# Payment utility functions
def generate_payment_reference(user_id):
    """Generate a random payment reference number"""
    prefix = "PLATBA"
    random_part = ''.join(random.choices(string.digits, k=8))
    return f"{prefix}-{user_id}-{random_part}"


def calculate_payment_amount(base_amount=500, discount=0):
    """Calculate final payment amount with optional discount"""
    if discount > 0:
        return max(0, base_amount - (base_amount * discount / 100))
    return base_amount


def generate_payment_qr_data(amount, reference, account_number="1234567890/2010"):
    """Generate payment QR code data string"""
    return f"SPD*1.0*ACC:{account_number}*AM:{amount}*CC:CZK*MSG:{reference}*X-VS:{reference}"


def validate_payment_reference(reference):
    """Validate payment reference format"""
    pattern = r'^PLATBA-\d+-\d{8}$'
    return bool(re.match(pattern, reference))


def process_payment_simulation(profile, amount, reference):
    """Simulate payment processing (random success/failure for demo)"""
    # Random simulation - 80% success rate
    success = random.random() > 0.2
    
    if success:
        payment_status_obj, created = PaymentStatus.objects.get_or_create(fencer=profile)
        payment_status_obj.is_paid = True
        payment_status_obj.payment_date = date.today()
        payment_status_obj.amount = amount
        payment_status_obj.save()
        return {"success": True, "message": "Platba byla úspěšně zpracována", "reference": reference}
    else:
        return {"success": False, "message": "Platba selhala, zkuste to prosím znovu", "reference": reference}


def get_payment_deadline():
    """Get payment deadline (30 days from today)"""
    return date.today() + timedelta(days=30)


@login_required
def payment_status(request):
    user = request.user
    profile = getattr(user, 'fencer_profile', None)
    if not profile:
        messages.info(request, 'Nejprve se prosím přiřaďte k profilu.')
        return redirect('match_profile')
    
    payment_status_obj, created = PaymentStatus.objects.get_or_create(fencer=profile)
    
    # Generate random payment reference if not paid
    payment_reference = None
    if not payment_status_obj.is_paid:
        payment_reference = generate_payment_reference(profile.id)
    
    # Calculate amount if not set
    if not payment_status_obj.amount:
        payment_status_obj.amount = calculate_payment_amount()
        payment_status_obj.save()
    
    context = {
        'payment_status': payment_status_obj,
        'payment_reference': payment_reference,
        'payment_deadline': get_payment_deadline(),
    }
    return render(request, 'fencers/payment_status.html', context)


@login_required
def guides_glossary(request):
    terms = GlossaryTerm.objects.all().order_by('term')
    context = {
        'terms': terms,
    }
    return render(request, 'fencers/guides_glossary.html', context)


@login_required
def guides_videos(request):
    videos = GuideVideo.objects.all().order_by('category', 'title')
    context = {
        'videos': videos,
    }
    return render(request, 'fencers/guides_videos.html', context)


@login_required
def guides_rules(request):
    rules = RulesDocument.objects.all()
    context = {
        'rules': rules,
    }
    return render(request, 'fencers/guides_rules.html', context)


@login_required
def guides_equipment_assembly(request):
    context = {}
    return render(request, 'fencers/guides_equipment_assembly.html', context)


@login_required
def equipment(request):
    user = request.user
    profile = getattr(user, 'fencer_profile', None)
    if not profile:
        messages.info(request, 'Nejprve se prosím přiřaďte k profilu.')
        return redirect('match_profile')
    
    equipment_items = list(EquipmentItem.objects.all().order_by('category', 'name'))
    
    # Get user's equipment status and attach to items
    user_equipment = {ue.equipment_id: ue for ue in UserEquipment.objects.filter(fencer=profile)}
    for item in equipment_items:
        item.user_equipment = user_equipment.get(item.id)
    
    if request.method == 'POST':
        equipment_id = request.POST.get('equipment_id')
        is_owned = request.POST.get('is_owned') == 'true'
        
        equipment_item = get_object_or_404(EquipmentItem, id=equipment_id)
        user_eq, created = UserEquipment.objects.get_or_create(
            fencer=profile,
            equipment=equipment_item
        )
        user_eq.is_owned = is_owned
        user_eq.save()
        
        return JsonResponse({'success': True})
    
    # Build RPG-like loadout slots around the figurine.
    def find_matching_item(slot):
        keywords = [kw.casefold() for kw in slot.get('keywords', [])]
        for item in equipment_items:
            name_cf = item.name.casefold()
            # Try exact match first
            if name_cf in keywords:
                return item
            # Then try matching - allow keyword at start of name or as whole word
            # This handles "mask" -> "Maska" but prevents "vesta" -> "Podvesta"
            for keyword in keywords:
                # Match if keyword is at the start of the name (e.g., "mask" matches "Maska")
                if name_cf.startswith(keyword):
                    return item
                # Or match if keyword is a whole word (word boundaries)
                # This ensures "vesta" matches "Vesta" but not "Podvesta"
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, name_cf):
                    return item
        return None
    
    loadout_slots = []
    for slot in EQUIPMENT_LOADOUT_SLOTS:
        slot_data = slot.copy()
        matched_item = find_matching_item(slot)
        slot_data['equipment_id'] = matched_item.id if matched_item else None
        slot_data['is_owned'] = (
            bool(matched_item and matched_item.user_equipment and matched_item.user_equipment.is_owned)
        )
        slot_data['description'] = (
            matched_item.description if matched_item and matched_item.description else slot.get('fallback_description', '')
        )
        slot_data['purchase_link'] = matched_item.purchase_link if matched_item else ''
        slot_data['is_disabled'] = matched_item is None
        loadout_slots.append(slot_data)
    
    positions = {'top': [], 'left': [], 'right': [], 'bottom': []}
    for slot in loadout_slots:
        pos = slot.get('position', 'left')
        if pos not in positions:
            positions[pos] = []
        positions[pos].append(slot)
    
    context = {
        'equipment_items': equipment_items,
        'loadout_slots_top': positions.get('top', []),
        'loadout_slots_left': positions.get('left', []),
        'loadout_slots_right': positions.get('right', []),
        'loadout_slots_bottom': positions.get('bottom', []),
    }
    return render(request, 'fencers/equipment.html', context)


@login_required
@require_POST
def toggle_photo_like(request, photo_id):
    """Toggle like/unlike for a photo"""
    photo = get_object_or_404(EventPhoto, id=photo_id)
    
    like, created = PhotoLike.objects.get_or_create(
        photo=photo,
        user=request.user
    )
    
    if not created:
        # Unlike - delete the like
        like.delete()
        is_liked = False
    else:
        # Like - keep it
        is_liked = True
    
    like_count = photo.get_like_count()
    
    return JsonResponse({
        'success': True,
        'is_liked': is_liked,
        'like_count': like_count
    })


@login_required
def my_favorite_photos(request):
    """View for 'Moje oblíbené' - user's liked photos"""
    # Get all photos liked by the current user
    liked_photos = EventPhoto.objects.filter(
        likes__user=request.user
    ).select_related('subalbum', 'subalbum__album', 'subalbum__album__event', 'uploaded_by').prefetch_related('likes').distinct().order_by('-likes__created_at')
    
    user_liked_photo_ids = set([photo.id for photo in liked_photos])
    
    context = {
        'all_photos': liked_photos,
        'user_liked_photo_ids': user_liked_photo_ids,
        'is_special_album': True,
        'album_title': 'Moje oblíbené',
    }
    return render(request, 'fencers/album_detail.html', context)


@login_required
def most_liked_photos(request):
    """View for 'Nejoblíbenější fotky' - most liked photos (at least 1 like)"""
    # Get all photos with at least 1 like, ordered by like count
    liked_photos = EventPhoto.objects.annotate(
        like_count=Count('likes')
    ).filter(
        like_count__gte=1
    ).select_related('subalbum', 'subalbum__album', 'subalbum__album__event', 'uploaded_by').prefetch_related('likes').order_by('-like_count', '-uploaded_at')
    
    user_liked_photo_ids = set(
        PhotoLike.objects.filter(user=request.user, photo__in=liked_photos).values_list('photo_id', flat=True)
    )
    
    context = {
        'all_photos': liked_photos,
        'user_liked_photo_ids': user_liked_photo_ids,
        'is_special_album': True,
        'album_title': 'Nejoblíbenější fotky',
    }
    return render(request, 'fencers/album_detail.html', context)

