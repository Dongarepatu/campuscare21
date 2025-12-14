from django.db import models
from django.conf import settings

class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    student_id = models.CharField(max_length=20, unique=True)
    enrollment_date = models.DateField()
    department = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    semester = models.IntegerField(default=1)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    
    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.student_id}"

class Attendance(models.Model):
    student = models.ForeignKey(
        StudentProfile, 
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField()
    subject = models.CharField(max_length=100)
    status_choices = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
    )
    status = models.CharField(max_length=10, choices=status_choices, default='present')
    remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Attendance Records"
        unique_together = ['student', 'date', 'subject']
    
    def __str__(self):
        return f"{self.student.user.username} - {self.date} - {self.subject}"

class Grade(models.Model):
    student = models.ForeignKey(
        StudentProfile, 
        on_delete=models.CASCADE,
        related_name='grades'
    )
    subject = models.CharField(max_length=100)
    semester = models.IntegerField()
    assignment_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    internal_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    final_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grade = models.CharField(max_length=2, blank=True, null=True)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    class Meta:
        verbose_name_plural = "Grades"
        unique_together = ['student', 'subject', 'semester']
    
    def calculate_grade(self):
        total_marks = self.assignment_marks + self.internal_marks + self.final_marks
        if total_marks >= 90:
            return 'A+', 4.0
        elif total_marks >= 80:
            return 'A', 3.7
        elif total_marks >= 70:
            return 'B+', 3.3
        elif total_marks >= 60:
            return 'B', 3.0
        elif total_marks >= 50:
            return 'C+', 2.7
        elif total_marks >= 40:
            return 'C', 2.3
        else:
            return 'F', 0.0
    
    def save(self, *args, **kwargs):
        if self.final_marks > 0:  # Only calculate if marks are entered
            self.grade, self.grade_point = self.calculate_grade()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.user.username} - {self.subject} - {self.grade}"