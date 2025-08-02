from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from .views import (
    login_view,
    rsvp_create_or_update,
    DashboardView,
    CategoryListView,
    EventListView,
    ParticipantListView,
    EventSearchView,
    EventCreateView,
    EventUpdateView,
    EventDeleteView,
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    path('events/', EventListView.as_view(), name='event_list'),
    path('events/add/', EventCreateView.as_view(), name='event-add'),
    path('events/<int:pk>/edit/', EventUpdateView.as_view(), name='event-edit'),
    path('events/<int:pk>/delete/', EventDeleteView.as_view(), name='event-delete'),

    path('events/<int:event_id>/rsvp/', rsvp_create_or_update, name='rsvp'),

    path('participants/', ParticipantListView.as_view(), name='participant_list'),
    path('participants/create/', views.participant_create, name='participant_create'),
    path('participants/<int:pk>/edit/', views.participant_update, name='participant_update'),
    path('participants/<int:pk>/delete/', views.participant_delete, name='participant_delete'),

    path('search/', EventSearchView.as_view(), name='search_events'),

    path('signup/', views.signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
]
