# library/forms.py
from django import forms
from django.utils import timezone
from .models import LibrarySeat

class OccupySeatForm(forms.ModelForm):
    """Form for occupying a seat with study details"""
    expected_duration = forms.IntegerField(
        min_value=30,
        max_value=240,
        initial=60,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Duration in minutes',
            'min': '30',
            'max': '240',
            'step': '15'
        }),
        help_text="How long do you plan to study? (30 minutes to 4 hours)",
        label="Study Duration (minutes)"
    )
    
    subject_studying = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Mathematics, Computer Science, Physics'
        }),
        help_text="Optional: What subject are you studying?",
        label="Subject"
    )
    
    study_purpose = forms.ChoiceField(
        choices=[
            ('', 'Select purpose'),
            ('assignment', '📝 Assignment'),
            ('exam_prep', '📚 Exam Preparation'),
            ('project', '💼 Project Work'),
            ('research', '🔬 Research'),
            ('general', '📖 General Study'),
            ('group_discussion', '👥 Group Discussion'),
            ('thesis', '🎓 Thesis/Dissertation'),
            ('coding', '💻 Coding Practice'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label="Study Purpose"
    )
    
    class Meta:
        model = LibrarySeat
        fields = ['expected_duration', 'subject_studying', 'study_purpose']
    
    def clean_expected_duration(self):
        duration = self.cleaned_data.get('expected_duration')
        if duration and (duration < 30 or duration > 240):
            raise forms.ValidationError("Study duration must be between 30 minutes and 4 hours.")
        return duration

class SeatFilterForm(forms.Form):
    """Form for filtering seats"""
    seat_type = forms.ChoiceField(
        choices=[('', 'All Seat Types')] + LibrarySeat._meta.get_field('seat_type').choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'this.form.submit()'
        }),
        label="Seat Type"
    )
    
    zone = forms.ChoiceField(
        choices=[('', 'All Zones')] + LibrarySeat._meta.get_field('zone').choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'this.form.submit()'
        }),
        label="Zone"
    )
    
    availability = forms.ChoiceField(
        choices=[
            ('', 'All Seats'),
            ('available', 'Available Only'),
            ('occupied', 'Occupied Only')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'this.form.submit()'
        }),
        label="Availability"
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('seat_number', 'Seat Number'),
            ('zone', 'Zone'),
            ('seat_type', 'Seat Type'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'this.form.submit()'
        }),
        label="Sort By"
    )

class ExtendTimeForm(forms.Form):
    """Form for extending study time"""
    additional_minutes = forms.IntegerField(
        min_value=15,
        max_value=120,
        initial=30,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Additional minutes',
            'min': '15',
            'max': '120',
            'step': '15'
        }),
        help_text="Additional study time (15 minutes to 2 hours)",
        label="Extend By (minutes)"
    )