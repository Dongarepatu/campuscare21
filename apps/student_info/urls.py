from django.urls import path
from . import views

app_name = 'student_info'

urlpatterns = [
    # Student routes
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('profile/create/', views.create_profile, name='create_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('attendance/', views.attendance_report, name='attendance_report'),
    path('grades/', views.grade_report, name='grade_report'),
    
    # Staff/Admin routes
    path('student/<str:student_id>/', views.student_detail, name='student_detail'),
    path('all-students/', views.all_students, name='all_students'),
    path('manage-attendance/', views.manage_attendance, name='manage_attendance'),
    path('manage-grades/', views.manage_grades, name='manage_grades'),
    path('student-reports/', views.student_reports, name='student_reports'),
]