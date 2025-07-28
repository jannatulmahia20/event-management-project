from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),  # root URL

    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('categories/', views.category_list, name='category_list'),
    path('events/', views.event_list, name='event_list'),
    path('participants/', views.participant_list, name='participant_list'),

    path('events/search/', views.search_events, name='event_search'),

    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/edit/', views.event_update, name='event_update'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),

    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    path('participants/create/', views.participant_create, name='participant_create'),
    path('participants/<int:pk>/edit/', views.participant_update, name='participant_update'),
    path('participants/<int:pk>/delete/', views.participant_delete, name='participant_delete'),
]
