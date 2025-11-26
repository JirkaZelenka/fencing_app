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
    UserEquipment, Club
)
from .forms import TrainingNoteForm, CircuitTrainingForm, EventReactionForm


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
            return redirect('home')
        else:
            messages.error(request, 'Neplatné přihlašovací údaje.')
    
    return render(request, 'fencers/login.html')


@login_required
def home(request):
    return redirect('about_me')


@login_required
def about_me(request):
    user = request.user
    profile = getattr(user, 'fencer_profile', None)
    tournament_participations = EventParticipation.objects.filter(
        fencer=user,
        event__event_type=Event.EventType.TOURNAMENT
    ).select_related('event')
    
    # Basic statistics (only tournament-type events count here)
    total_tournaments = tournament_participations.count()
    total_wins = tournament_participations.aggregate(Sum('wins'))['wins__sum'] or 0
    total_losses = tournament_participations.aggregate(Sum('losses'))['losses__sum'] or 0
    total_touches_scored = tournament_participations.aggregate(Sum('touches_scored'))['touches_scored__sum'] or 0
    total_touches_received = tournament_participations.aggregate(Sum('touches_received'))['touches_received__sum'] or 0
    win_rate = (total_wins / (total_wins + total_losses) * 100) if (total_wins + total_losses) > 0 else 0
    
    all_events = Event.objects.all().order_by('-start_date')
    participation_lookup = {
        p.event_id: p for p in EventParticipation.objects.filter(fencer=user).select_related('event')
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
    }
    return render(request, 'fencers/about_me.html', context)


@login_required
def statistics_individual(request):
    user = request.user
    
    individual_participations = EventParticipation.objects.filter(fencer=user).select_related('event')
    
    # Get user's participations in humanitarian tournaments
    humanitarian_participations = EventParticipation.objects.filter(
        fencer=user,
        event__event_type=Event.EventType.HUMANITARIAN
    ).select_related('event').order_by('-event__start_date')
    
    profile = getattr(user, 'fencer_profile', None)
    club = None
    club_fencers = None
    club_participations = None
    internal_events = None
    
    if profile and profile.club:
        club = profile.club
        club_fencers = FencerProfile.objects.filter(club=profile.club).select_related('user')
        fencer_ids = [fp.user.id for fp in club_fencers]
        club_participations = EventParticipation.objects.filter(
            fencer_id__in=fencer_ids
        ).select_related('fencer', 'event')
        internal_events = Event.objects.filter(
            event_type=Event.EventType.HUMANITARIAN
        ).order_by('-start_date')
    
    context = {
        'participations': individual_participations,
        'humanitarian_participations': humanitarian_participations,
        'club': club,
        'club_fencers': club_fencers,
        'club_participations': club_participations,
        'internal_tournaments': internal_events,
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
    fencer_ids = [fp.user.id for fp in club_fencers]
    
    participations = EventParticipation.objects.filter(
        fencer_id__in=fencer_ids
    ).select_related('fencer', 'event')
    
    internal_events = Event.objects.filter(
        event_type=Event.EventType.TOURNAMENT
    ).order_by('-start_date')
    
    context = {
        'club': profile.club,
        'club_fencers': club_fencers,
        'participations': participations,
        'internal_tournaments': internal_events,
    }
    return render(request, 'fencers/statistics_club.html', context)


@login_required
def training_notes(request):
    user = request.user
    notes = TrainingNote.objects.filter(fencer=user).order_by('-date')
    
    if request.method == 'POST':
        form = TrainingNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.fencer = user
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
    photos = EventPhoto.objects.filter(is_featured=True).order_by('-event_date', '-uploaded_at')
    context = {
        'photos': photos,
    }
    return render(request, 'fencers/event_photos.html', context)


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
    
    filter_query = urlencode({'types': selected_types}, doseq=True)
    
    # Get all events in this month
    month_events = Event.objects.filter(
        start_date__gte=first_day,
        start_date__lte=last_day,
        event_type__in=selected_types_set,
    ).order_by('start_date')
    
    # Create a dictionary of events by date
    events_by_date = {}
    
    for event in month_events:
        serialized = serialize_event(event)
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
    
    # Get upcoming events for the list view
    now = timezone.now()
    
    upcoming_events_qs = Event.objects.filter(
        start_date__gte=now,
        event_type__in=selected_types_set,
    ).order_by('start_date')
    past_events_qs = Event.objects.filter(
        start_date__lt=now,
        event_type__in=selected_types_set,
    ).order_by('-start_date')[:30]
    
    # Get user reactions and attach to events
    reaction_dict = {}
    if request.user.is_authenticated and upcoming_events_qs:
        reactions = EventReaction.objects.filter(user=request.user, event__in=upcoming_events_qs)
        reaction_dict = {r.event_id: r for r in reactions}
    
    serialized_upcoming = [
        serialize_event(event, reaction_dict.get(event.id))
        for event in upcoming_events_qs
    ]
    serialized_upcoming.sort(key=lambda item: item['start'])
    
    serialized_past = [
        serialize_event(event)
        for event in past_events_qs
    ]
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


def process_payment_simulation(user, amount, reference):
    """Simulate payment processing (random success/failure for demo)"""
    # Random simulation - 80% success rate
    success = random.random() > 0.2
    
    if success:
        payment_status_obj, created = PaymentStatus.objects.get_or_create(fencer=user)
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
    payment_status_obj, created = PaymentStatus.objects.get_or_create(fencer=request.user)
    
    # Generate random payment reference if not paid
    payment_reference = None
    if not payment_status_obj.is_paid:
        payment_reference = generate_payment_reference(request.user.id)
    
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
    equipment_items = list(EquipmentItem.objects.all().order_by('category', 'name'))
    
    # Get user's equipment status and attach to items
    user_equipment = {ue.equipment_id: ue for ue in UserEquipment.objects.filter(user=user)}
    for item in equipment_items:
        item.user_equipment = user_equipment.get(item.id)
    
    if request.method == 'POST':
        equipment_id = request.POST.get('equipment_id')
        is_owned = request.POST.get('is_owned') == 'true'
        
        equipment_item = get_object_or_404(EquipmentItem, id=equipment_id)
        user_eq, created = UserEquipment.objects.get_or_create(
            user=user,
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

