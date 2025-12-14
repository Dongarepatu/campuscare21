# library/models.py - COMPLETE AND CORRECTED
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

class LibrarySeat(models.Model):
    """Model for 50 ground floor library seats"""
    
    # Seat type choices
    SEAT_TYPES = [
        ('standard', 'Standard'),
        ('premium', 'Premium (with monitor)'),
        ('quiet', 'Quiet Zone'),
        ('group', 'Group Study'),
    ]
    
    # Zone choices
    ZONE_CHOICES = [
        ('reading_area', 'Reading Area'),
        ('computer_section', 'Computer Section'),
        ('quiet_zone', 'Quiet Zone'),
        ('group_study', 'Group Study Area'),
        ('window_side', 'Window Side'),
        ('entrance_area', 'Entrance Area'),
    ]
    
    # Study purpose choices
    PURPOSE_CHOICES = [
        ('assignment', 'Assignment'),
        ('exam_prep', 'Exam Preparation'),
        ('project', 'Project Work'),
        ('research', 'Research'),
        ('general', 'General Study'),
        ('group_discussion', 'Group Discussion'),
        ('thesis', 'Thesis/Dissertation'),
        ('coding', 'Coding Practice'),
    ]
    
    # ============ BASIC FIELDS ============
    seat_number = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Seat Number"
    )
    
    seat_type = models.CharField(
        max_length=20,
        choices=SEAT_TYPES,
        default='standard'
    )
    
    zone = models.CharField(
        max_length=50,
        choices=ZONE_CHOICES,
        default='reading_area'
    )
    
    # ============ OCCUPATION TRACKING ============
    is_available = models.BooleanField(default=True)
    
    occupied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='occupied_library_seats'
    )
    
    occupied_since = models.DateTimeField(null=True, blank=True)
    
    expected_duration = models.IntegerField(
        default=60,
        validators=[MinValueValidator(30), MaxValueValidator(240)],
        help_text="Expected study duration in minutes (30min - 4hrs)"
    )
    
    # ============ STUDY DETAILS ============
    subject_studying = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Subject Being Studied"
    )
    
    study_purpose = models.CharField(
        max_length=50,
        choices=PURPOSE_CHOICES,
        blank=True
    )
    
    # ============ AMENITIES ============
    has_outlet = models.BooleanField(default=True)
    has_monitor = models.BooleanField(default=False)
    
    # ============ ADDITIONAL FIELDS ============
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # ============ METHODS ============
    def __str__(self):
        return f"Seat {self.seat_number} - {'Available' if self.is_available else 'Occupied'}"
    
    def get_occupation_time_minutes(self):
        """Get occupation duration in minutes"""
        if self.occupied_since and not self.is_available:
            duration = timezone.now() - self.occupied_since
            return int(duration.total_seconds() / 60)
        return 0
    
    def get_occupation_time_display(self):
        """Display occupation time nicely"""
        minutes = self.get_occupation_time_minutes()
        if minutes < 60:
            return f"{minutes} min"
        else:
            hours = minutes // 60
            mins = minutes % 60
            if mins == 0:
                return f"{hours}h"
            return f"{hours}h {mins}m"
    
    def get_expected_end_time(self):
        """Calculate expected departure time"""
        if self.occupied_since and self.expected_duration:
            return self.occupied_since + timezone.timedelta(minutes=self.expected_duration)
        return None
    
    def is_overstaying(self):
        """Check if student has exceeded expected duration"""
        if self.occupied_since and self.expected_duration:
            current_time = self.get_occupation_time_minutes()
            return current_time > self.expected_duration
        return False
    
    def get_zone_display(self):
        """Get human-readable zone name"""
        zone_dict = dict(self.ZONE_CHOICES)
        return zone_dict.get(self.zone, self.zone)
    
    def get_seat_type_display(self):
        """Get human-readable seat type"""
        type_dict = dict(self.SEAT_TYPES)
        return type_dict.get(self.seat_type, self.seat_type)
    
    def get_study_purpose_display(self):
        """Get human-readable study purpose"""
        if self.study_purpose:
            purpose_dict = dict(self.PURPOSE_CHOICES)
            return purpose_dict.get(self.study_purpose, self.study_purpose)
        return "General Study"
    
    # ============ META CLASS ============
    class Meta:
        ordering = ['seat_number']
        verbose_name = "Library Seat"
        verbose_name_plural = "Library Seats"  # THIS LINE WAS MISSING A CLOSING QUOTE