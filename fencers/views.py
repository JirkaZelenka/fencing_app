import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db.models import Q, Count, Avg, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import (
    FencerProfile, Tournament, TournamentParticipation, TrainingNote,
    CircuitTraining, CircuitSong, EventPhoto, CalendarEvent, EventReaction,
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
    participations = TournamentParticipation.objects.filter(fencer=user).select_related('tournament')[:10]
    
    # Basic statistics
    total_tournaments = participations.count()
    total_wins = participations.aggregate(Sum('wins'))['wins__sum'] or 0
    total_losses = participations.aggregate(Sum('losses'))['losses__sum'] or 0
    total_touches_scored = participations.aggregate(Sum('touches_scored'))['touches_scored__sum'] or 0
    total_touches_received = participations.aggregate(Sum('touches_received'))['touches_received__sum'] or 0
    
    win_rate = (total_wins / (total_wins + total_losses) * 100) if (total_wins + total_losses) > 0 else 0
    
    context = {
        'profile': profile,
        'participations': participations,
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
    participations = TournamentParticipation.objects.filter(fencer=user).select_related('tournament')
    
    context = {
        'participations': participations,
    }
    return render(request, 'fencers/statistics_individual.html', context)


@login_required
def statistics_club(request):
    user = request.user
    profile = getattr(user, 'fencer_profile', None)
    
    if not profile or not profile.club:
        messages.info(request, 'Nemáte přiřazený klub.')
        return redirect('about_me')
    
    # Get all fencers from the same club
    club_fencers = FencerProfile.objects.filter(club=profile.club).select_related('user')
    fencer_ids = [fp.user.id for fp in club_fencers]
    
    # Get all participations for club members
    participations = TournamentParticipation.objects.filter(fencer_id__in=fencer_ids).select_related('fencer', 'tournament')
    
    # Get internal tournaments
    internal_tournaments = Tournament.objects.filter(is_internal=True).order_by('-date')
    
    context = {
        'club': profile.club,
        'club_fencers': club_fencers,
        'participations': participations,
        'internal_tournaments': internal_tournaments,
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
    from datetime import datetime, timedelta
    
    now = datetime.now()
    upcoming_events = CalendarEvent.objects.filter(start_date__gte=now).order_by('start_date')
    past_events = CalendarEvent.objects.filter(start_date__lt=now).order_by('-start_date')[:10]
    
    # Get user reactions and attach to events
    if request.user.is_authenticated:
        reactions = EventReaction.objects.filter(user=request.user, event__in=upcoming_events)
        reaction_dict = {r.event_id: r for r in reactions}
        for event in upcoming_events:
            event.user_reaction = reaction_dict.get(event.id)
    
    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    }
    return render(request, 'fencers/calendar_events.html', context)


@login_required
@require_POST
def event_reaction(request, event_id):
    event = get_object_or_404(CalendarEvent, id=event_id)
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


@login_required
def payment_status(request):
    payment_status_obj, created = PaymentStatus.objects.get_or_create(fencer=request.user)
    
    context = {
        'payment_status': payment_status_obj,
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

