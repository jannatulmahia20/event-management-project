from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime, date

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login

from .models import Category, Event, Participant, RSVP
from .forms import EventForm, CategoryForm, ParticipantForm, SignupForm, RSVPForm
from .decorators import group_required


@login_required
def dashboard_view(request):
    total_events = Event.objects.count()
    total_participants = Participant.objects.count()
    upcoming_events = Event.objects.filter(date__gt=date.today()).count()
    past_events = Event.objects.filter(date__lt=date.today()).count()
    today_events = Event.objects.filter(date=date.today())

    filter_type = request.GET.get('filter', 'all')

    if filter_type == 'upcoming':
        events_list = Event.objects.filter(date__gt=date.today()).order_by('date')
    elif filter_type == 'past':
        events_list = Event.objects.filter(date__lt=date.today()).order_by('-date')
    else:
        events_list = Event.objects.all().order_by('date')

    events_list = events_list.annotate(participant_count=Count('participants')).select_related('category')

    context = {
        'total_events': total_events,
        'total_participants': total_participants,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'today_events': today_events,
        'events_list': events_list,
        'filter_type': filter_type,
        'now': datetime.now(),
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def category_list(request):
    categories = Category.objects.prefetch_related('events')
    return render(request, 'core/category_list.html', {'categories': categories})


@login_required
def event_list(request):
    events = Event.objects.select_related('category').prefetch_related('participants').annotate(participant_count=Count('participants'))

    category_id = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if category_id:
        events = events.filter(category_id=category_id)
    if start_date and end_date:
        events = events.filter(date__range=[start_date, end_date])

    categories = Category.objects.all()

    context = {
        'events': events,
        'categories': categories,
        'selected_category': category_id,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'core/event_list.html', context)


@login_required
def participant_list(request):
    participants = Participant.objects.prefetch_related('events')
    return render(request, 'core/participant_list.html', {'participants': participants})


@login_required
def search_events(request):
    query = request.GET.get('q')
    events = Event.objects.all()
    if query:
        events = events.filter(
            Q(name__icontains=query) |
            Q(location__icontains=query)
        ).select_related('category')
    return render(request, 'core/search_results.html', {'events': events, 'query': query})


# Event CRUD
@login_required
@group_required('Admin', 'Organizer')
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Event created successfully.")
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'core/event_form.html', {'form': form})


@login_required
@group_required('Admin', 'Organizer')
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully.")
            return redirect('event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'core/event_form.html', {'form': form})


@login_required
@group_required('Admin', 'Organizer')
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event deleted successfully.")
        return redirect('event_list')
    return render(request, 'core/event_confirm_delete.html', {'event': event})


# Category CRUD
@login_required
@group_required('Admin')
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'core/category_form.html', {'form': form})


@login_required
@group_required('Admin')
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'core/category_form.html', {'form': form})


@login_required
@group_required('Admin')
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted successfully.")
        return redirect('category_list')
    return render(request, 'core/category_confirm_delete.html', {'category': category})


# Participant CRUD
@login_required
@group_required('Admin', 'Organizer')
def participant_create(request):
    if request.method == 'POST':
        form = ParticipantForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Participant created successfully.")
            return redirect('participant_list')
    else:
        form = ParticipantForm()
    return render(request, 'core/participant_form.html', {'form': form})


@login_required
def participant_update(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    if request.method == 'POST':
        form = ParticipantForm(request.POST, instance=participant)
        if form.is_valid():
            form.save()
            messages.success(request, "Participant updated successfully.")
            return redirect('participant_list')
    else:
        form = ParticipantForm(instance=participant)
    return render(request, 'core/participant_form.html', {'form': form})


@login_required
def participant_delete(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    if request.method == 'POST':
        participant.delete()
        messages.success(request, "Participant deleted successfully.")
        return redirect('participant_list')
    return render(request, 'core/participant_confirm_delete.html', {'participant': participant})


# Auth Views
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Manual activation for now
            user.save()
            messages.success(request, 'Account created! Please check your email to activate your account.')
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'core/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid credentials or inactive account.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


# RSVP
@login_required
def rsvp_create_or_update(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    participant = get_object_or_404(Participant, user=request.user)

    rsvp, created = RSVP.objects.get_or_create(event=event, participant=participant)

    if request.method == 'POST':
        form = RSVPForm(request.POST, instance=rsvp)
        if form.is_valid():
            form.save()
            messages.success(request, "Your RSVP has been submitted.")
            return redirect('event_list')
    else:
        form = RSVPForm(instance=rsvp)

    context = {
        'form': form,
        'event': event,
    }
    return render(request, 'core/rsvp_form.html', context)
