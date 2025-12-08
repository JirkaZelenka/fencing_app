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
    
    # Password reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='fencers/password_reset.html',
             email_template_name='fencers/password_reset_email.html',
             subject_template_name='fencers/password_reset_subject.txt',
             success_url='/password-reset/done/',
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='fencers/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='fencers/password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='fencers/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # Password change for logged-in users
    path('password-change/', 
         auth_views.PasswordChangeView.as_view(
             template_name='fencers/password_change.html',
             success_url='/password-change-done/'
         ), 
         name='password_change'),
    path('password-change-done/', 
         auth_views.PasswordChangeDoneView.as_view(
             template_name='fencers/password_change_done.html'
         ), 
         name='password_change_done'),
    
    # Main pages
    path('about-me/', views.about_me, name='about_me'),
    path('api/member-detail/<int:profile_id>/', views.member_detail_api, name='member_detail_api'),
    path('statistics/individual/', views.statistics_individual, name='statistics_individual'),
    path('statistics/club/', views.statistics_club, name='statistics_club'),
    path('training/notes/', views.training_notes, name='training_notes'),
    path('training/circuits/', views.circuit_trainings, name='circuit_trainings'),
    path('training/circuits/<int:circuit_id>/edit/', views.edit_circuit_training, name='edit_circuit_training'),
    path('training/circuits/<int:circuit_id>/delete/', views.delete_circuit_training, name='delete_circuit_training'),
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
    path('payment/notify/', views.notify_payment, name='notify_payment'),
    path('guides/glossary/', views.guides_glossary, name='guides_glossary'),
    path('guides/videos/', views.guides_videos, name='guides_videos'),
    path('guides/rules/', views.guides_rules, name='guides_rules'),
    path('guides/equipment-assembly/', views.guides_equipment_assembly, name='guides_equipment_assembly'),
    path('equipment/', views.equipment, name='equipment'),
    
    # News endpoints
    path('news/list/', views.news_list, name='news_list'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('news/<int:news_id>/mark-read/', views.mark_news_read, name='mark_news_read'),
]

