# library/urls.py
from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    # Home page
    path('', views.library_home, name='home'),
    
    # Main views
    path('seat-map/', views.library_seat_map, name='seat_map'),
    path('dashboard/', views.library_dashboard, name='dashboard'),
    path('info/', views.library_info, name='library_info'),
    
    # Seat operations
    path('seat/<int:seat_id>/occupy/', views.occupy_seat, name='occupy_seat'),
    path('seat/<int:seat_id>/release/', views.release_seat, name='release_seat'),
    path('seat/<int:seat_id>/extend/', views.extend_study_time, name='extend_study_time'),
    path('seat/<int:seat_id>/detail/', views.seat_detail, name='seat_detail'),
    
    # Quick actions
    path('release-my-seat/', views.release_my_seat, name='release_my_seat'),
    path('my-history/', views.my_study_history, name='my_study_history'),
    
    # Student information
    path('current-students/', views.current_students, name='current_students'),
    
    # Admin views
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/release-seat/<int:seat_id>/', views.admin_release_seat, name='admin_release_seat'),
    
    # API endpoints
    path('api/seat-status/', views.seat_status_api, name='seat_status_api'),
    
    # Error handlers
    path('404/', views.handler404),
    path('500/', views.handler500),
]