from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'academics'

urlpatterns = [
    # Student routes
    path('dashboard/', views.student_academics_dashboard, name='student_dashboard'),
    path('notes/', views.note_list, name='note_list'),
    path('notes/<int:pk>/', views.note_detail, name='note_detail'),
    path('notes/<int:pk>/download/', views.download_note, name='download_note'),
    path('study-materials/', views.study_material_list, name='study_material_list'),
    
    # Staff/Admin routes
    path('staff/dashboard/', views.staff_academics_dashboard, name='staff_dashboard'),
    path('staff/upload-note/', views.upload_note, name='upload_note'),
    path('staff/upload-material/', views.upload_study_material, name='upload_study_material'),
    path('staff/manage-notes/', views.manage_notes, name='manage_notes'),
    path('staff/manage-materials/', views.manage_study_materials, name='manage_study_materials'),
    path('staff/notes/<int:pk>/toggle-approval/', views.toggle_note_approval, name='toggle_note_approval'),
    path('staff/notes/<int:pk>/delete/', views.delete_note, name='delete_note'),
    path('staff/courses/', views.manage_courses, name='manage_courses'),
    path('staff/subjects/', views.manage_subjects, name='manage_subjects'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)