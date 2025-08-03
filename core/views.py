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

from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from .forms import UserUpdateForm, ParticipantUpdateForm

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()

from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


# Dashboard View
@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    def get(self, request):
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


# Category Views
@method_decorator(login_required, name='dispatch')
class CategoryListView(ListView):
    model = Category
    template_name = 'core/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Category
    fields = ['name']
    template_name = 'core/category_form.html'
    success_url = reverse_lazy('category_list')

    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()

class CategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Category
    fields = ['name']
    template_name = 'core/category_form.html'
    success_url = reverse_lazy('category_list')

    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()

class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Category
    template_name = 'core/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')

    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()


# Participant Views
@method_decorator(login_required, name='dispatch')
class ParticipantListView(ListView):
    model = Participant
    template_name = 'core/participant_list.html'
    context_object_name = 'participants'

class ParticipantCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Participant
    fields = '__all__'
    template_name = 'core/participant_form.html'
    success_url = reverse_lazy('participant_list')

    def test_func(self):
        return self.request.user.groups.filter(name__in=['Admin', 'Organizer']).exists()

class ParticipantUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Participant
    fields = '__all__'
    template_name = 'core/participant_form.html'
    success_url = reverse_lazy('participant_list')

    def test_func(self):
        return self.request.user.groups.filter(name__in=['Admin', 'Organizer']).exists()

class ParticipantDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Participant
    template_name = 'core/participant_confirm_delete.html'
    success_url = reverse_lazy('participant_list')

    def test_func(self):
        return self.request.user.groups.filter(name__in=['Admin', 'Organizer']).exists()


# Event Views
@method_decorator(login_required, name='dispatch')
class EventListView(ListView):
    model = Event
    template_name = 'core/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        events = Event.objects.all()
        category_id = self.request.GET.get('category')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if category_id:
            events = events.filter(category_id=category_id)
        if start_date:
            events = events.filter(date__gte=start_date)
        if end_date:
            events = events.filter(date__lte=end_date)

        if self.request.user.groups.filter(name='Organizer').exists():
            events = events.filter(created_by=self.request.user)

        return events

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category')
        context['start_date'] = self.request.GET.get('start_date')
        context['end_date'] = self.request.GET.get('end_date')
        return context

class EventCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'core/event_form.html'
    success_url = reverse_lazy('event_list')

    def form_valid(self, form):
        if self.request.user.groups.filter(name='Organizer').exists():
            form.instance.created_by = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.groups.filter(name__in=['Admin', 'Organizer']).exists()

class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'core/event_form.html'
    success_url = reverse_lazy('event_list')

    def test_func(self):
        event = self.get_object()
        return (self.request.user == event.created_by or self.request.user.is_superuser) and \
               self.request.user.groups.filter(name__in=['Admin', 'Organizer']).exists()

class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    template_name = 'core/event_confirm_delete.html'
    success_url = reverse_lazy('event_list')

    def test_func(self):
        event = self.get_object()
        return (self.request.user == event.created_by or self.request.user.is_superuser) and \
               self.request.user.groups.filter(name__in=['Admin', 'Organizer']).exists()


# Event Search View
@method_decorator(login_required, name='dispatch')
class EventSearchView(ListView):
    model = Event
    template_name = 'core/search_results.html'
    context_object_name = 'events'

    def get_queryset(self):
        query = self.request.GET.get('q')
        qs = Event.objects.all()
        if query:
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(location__icontains=query)
            ).select_related('category')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


# RSVP Create or Update
@login_required
def rsvp_create_or_update(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    try:
        participant = Participant.objects.get(user=request.user)
    except Participant.DoesNotExist:
        messages.error(request, "You are not registered as a participant.")
        return redirect('event_list')

    rsvp, created = RSVP.objects.get_or_create(event=event, participant=participant)

    if request.method == 'POST':
        form = RSVPForm(request.POST, instance=rsvp)
        if form.is_valid():
            form.save()
            messages.success(request, "Your RSVP has been submitted.")
            return redirect('event_list')
    else:
        form = RSVPForm(instance=rsvp)

    return render(request, 'core/rsvp_form.html', {'form': form, 'event': event})


# Auth Views
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            messages.success(request, 'Account created! Please check your email to activate your account.')
            return redirect('login')
        else:
            messages.error(request, 'Please provide correct info.')
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


# Profile Views
@login_required
def profile_view(request):
    participant = get_object_or_404(Participant, user=request.user)
    return render(request, 'core/profile.html', {'participant': participant})

@login_required
def profile_edit(request):
    participant = get_object_or_404(Participant, user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        participant_form = ParticipantUpdateForm(request.POST, instance=participant)
        if user_form.is_valid() and participant_form.is_valid():
            user_form.save()
            participant_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        participant_form = ParticipantUpdateForm(instance=participant)

    return render(request, 'core/profile_edit.html', {
        'user_form': user_form,
        'participant_form': participant_form,
    })


# Account Activation
def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account activated! You can now log in.")
        return redirect('login')
    else:
        return render(request, 'core/account_activation_invalid.html')
