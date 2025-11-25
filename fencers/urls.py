from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Main pages
    path('about-me/', views.about_me, name='about_me'),
    path('statistics/individual/', views.statistics_individual, name='statistics_individual'),
    path('statistics/club/', views.statistics_club, name='statistics_club'),
    path('training/notes/', views.training_notes, name='training_notes'),
    path('training/circuits/', views.circuit_trainings, name='circuit_trainings'),
    path('photos/', views.event_photos, name='event_photos'),
    path('calendar/', views.calendar_events, name='calendar_events'),
    path('calendar/<int:event_id>/reaction/', views.event_reaction, name='event_reaction'),
    path('payment/', views.payment_status, name='payment_status'),
    path('guides/glossary/', views.guides_glossary, name='guides_glossary'),
    path('guides/videos/', views.guides_videos, name='guides_videos'),
    path('guides/rules/', views.guides_rules, name='guides_rules'),
    path('guides/equipment-assembly/', views.guides_equipment_assembly, name='guides_equipment_assembly'),
    path('equipment/', views.equipment, name='equipment'),
]

