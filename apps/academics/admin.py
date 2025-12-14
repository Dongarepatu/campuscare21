from django.contrib import admin
from .models import Course, Subject, Note, StudyMaterial

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'semester', 'credits', 'created_at']
    list_filter = ['department', 'semester', 'created_at']
    search_fields = ['code', 'name', 'department']
    ordering = ['semester', 'code']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'course', 'created_at']
    list_filter = ['course', 'created_at']
    search_fields = ['code', 'name', 'course__name']
    ordering = ['course', 'name']

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'file_type', 'uploaded_by', 'uploaded_at', 'is_approved']
    list_filter = ['file_type', 'is_approved', 'uploaded_at', 'subject']
    search_fields = ['title', 'description', 'subject__name']
    readonly_fields = ['uploaded_at', 'updated_at']
    list_editable = ['is_approved']

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'material_type', 'subject', 'uploaded_by', 'uploaded_at', 'academic_year']
    list_filter = ['material_type', 'academic_year', 'uploaded_at', 'subject']
    search_fields = ['title', 'description', 'subject__name']
    readonly_fields = ['uploaded_at']