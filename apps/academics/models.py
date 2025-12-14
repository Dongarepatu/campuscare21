from django.db import models
from django.conf import settings
from django.urls import reverse

class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    department = models.CharField(max_length=100)
    semester = models.IntegerField()
    credits = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['semester', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Subject(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['course', 'name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Note(models.Model):
    FILE_TYPE_CHOICES = (
        ('pdf', 'PDF'),
        ('doc', 'DOC/DOCX'),
        ('ppt', 'PPT/PPTX'),
        ('txt', 'Text'),
        ('image', 'Image'),
        ('other', 'Other'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='notes')
    file = models.FileField(upload_to='academic_notes/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, default='pdf')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_notes')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.subject.name}"
    
    def get_absolute_url(self):
        return reverse('academics:note_detail', kwargs={'pk': self.pk})
    
    def get_file_extension(self):
        return self.file.name.split('.')[-1].upper()
    
    def get_file_size(self):
        if self.file:
            size_bytes = self.file.size
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        return "0 B"

class StudyMaterial(models.Model):
    MATERIAL_TYPE_CHOICES = (
        ('syllabus', 'Syllabus'),
        ('question_paper', 'Question Paper'),
        ('lab_manual', 'Lab Manual'),
        ('reference', 'Reference Material'),
        ('tutorial', 'Tutorial'),
        ('other', 'Other'),
    )
    
    title = models.CharField(max_length=200)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPE_CHOICES, default='reference')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='study_materials')
    file = models.FileField(upload_to='study_materials/')
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    academic_year = models.CharField(max_length=20, default='2024-25')
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_material_type_display()}"