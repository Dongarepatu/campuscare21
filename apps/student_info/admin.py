from django.contrib import admin
from .models import StudentProfile, Attendance, Grade

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user', 'department', 'course', 'semester', 'enrollment_date']
    list_filter = ['department', 'course', 'semester', 'enrollment_date']
    search_fields = ['student_id', 'user__username', 'user__first_name', 'user__last_name']
    raw_id_fields = ['user']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'subject', 'status']
    list_filter = ['date', 'subject', 'status']
    search_fields = ['student__user__username', 'student__student_id', 'subject']
    date_hierarchy = 'date'

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'semester', 'final_marks', 'grade', 'grade_point']
    list_filter = ['semester', 'subject', 'grade']
    search_fields = ['student__user__username', 'student__student_id', 'subject']
    readonly_fields = ['grade', 'grade_point']