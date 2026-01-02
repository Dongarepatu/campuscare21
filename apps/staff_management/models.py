from django.db import models
from django.conf import settings  # This allows us to link to the User model safely

class StaffProfile(models.Model):
    # Link to the User model in the 'user_management' app
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='staff_profile'
    )
    
    # Staff specific fields
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True)
    joining_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.designation}"