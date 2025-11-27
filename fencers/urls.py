from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('match-profile/', views.match_profile, name='match_profile'),
    path('unpair-profile/', views.unpair_profile, name='unpair_profile'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Main pages
    path('about-me/', views.about_me, name='about_me'),
    path('statistics/individual/', views.statistics_individual, name='statistics_individual'),
    path('statistics/club/', views.statistics_club, name='statistics_club'),
    path('training/notes/', views.training_notes, name='training_notes'),
    path('training/circuits/', views.circuit_trainings, name='circuit_trainings'),
    path('photos/', views.event_photos, name='event_photos'),
    path('photos/my-favorites/', views.my_favorite_photos, name='my_favorite_photos'),
    path('photos/most-liked/', views.most_liked_photos, name='most_liked_photos'),
    path('photos/album/<int:album_id>/', views.album_detail, name='album_detail'),
    path('photos/album/<int:album_id>/cover/', views.update_album_cover, name='update_album_cover'),
    path('photos/album/<int:album_id>/subalbum/create/', views.create_subalbum, name='create_subalbum'),
    path('photos/subalbum/<int:subalbum_id>/upload/', views.upload_photo, name='upload_photo'),
    path('photos/photo/<int:photo_id>/like/', views.toggle_photo_like, name='toggle_photo_like'),
    path('calendar/', views.calendar_events, name='calendar_events'),
    path('calendar/<int:event_id>/reaction/', views.event_reaction, name='event_reaction'),
    path('payment/', views.payment_status, name='payment_status'),
    path('guides/glossary/', views.guides_glossary, name='guides_glossary'),
    path('guides/videos/', views.guides_videos, name='guides_videos'),
    path('guides/rules/', views.guides_rules, name='guides_rules'),
    path('guides/equipment-assembly/', views.guides_equipment_assembly, name='guides_equipment_assembly'),
    path('equipment/', views.equipment, name='equipment'),
]

