from django.contrib import admin
from .models import StaffProfile

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'department', 'designation', 'employee_id')
    search_fields = ('user__username', 'user__first_name', 'department')
    
    # Helper to show username since 'user' is a foreign key
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'