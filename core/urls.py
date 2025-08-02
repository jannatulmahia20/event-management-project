from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from core.views import login_view
from django.contrib.auth.views import LogoutView
from .views import rsvp_create_or_update
from .views import DashboardView
from .views import CategoryListView
from .views import EventListView
from .views import ParticipantListView
from .views import EventSearchView



urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),


    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('events/', EventListView.as_view(), name='event_list'),
    path('participants/', ParticipantListView.as_view(), name='participant_list'),

    path('search/', EventSearchView.as_view(), name='search_events'),
    path('events/<int:event_id>/rsvp/', views.rsvp_create_or_update, name='rsvp_create_or_update'),
    path('events/<int:event_id>/rsvp/', rsvp_create_or_update, name='rsvp'),

    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/edit/', views.event_update, name='event_update'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),

    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    path('participants/create/', views.participant_create, name='participant_create'),
    path('participants/<int:pk>/edit/', views.participant_update, name='participant_update'),
    path('participants/<int:pk>/delete/', views.participant_delete, name='participant_delete'),

    path('signup/', views.signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
]
