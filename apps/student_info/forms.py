from django import forms
from .models import StudentProfile, Attendance, Grade

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'student_id', 'enrollment_date', 'department', 'course', 
            'semester', 'father_name', 'mother_name', 'emergency_contact'
        ]
        widgets = {
            'enrollment_date': forms.DateInput(attrs={'type': 'date'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.TextInput(attrs={'class': 'form-control'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 8}),
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'subject', 'status', 'remarks']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['student', 'subject', 'semester', 'assignment_marks', 'internal_marks', 'final_marks']
        widgets = {
            'assignment_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'max': '100'}),
            'internal_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'max': '100'}),
            'final_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'max': '100'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 8}),
        }