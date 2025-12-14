# library/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import LibrarySeat

@admin.register(LibrarySeat)
class LibrarySeatAdmin(admin.ModelAdmin):
    list_display = (
        'seat_number', 'get_zone_display', 'get_seat_type_display', 
        'status_display', 'occupied_by_display', 'subject_studying',
        'occupied_since_display', 'expected_duration'
    )
    
    list_filter = ('zone', 'seat_type', 'is_available', 'study_purpose')
    search_fields = ('seat_number', 'occupied_by__username', 'subject_studying')
    list_editable = ('expected_duration',)
    
    actions = ['release_selected_seats', 'mark_all_available']
    
    def status_display(self, obj):
        if obj.is_available:
            return format_html('<span class="badge bg-success">Available</span>')
        else:
            return format_html('<span class="badge bg-danger">Occupied</span>')
    status_display.short_description = 'Status'
    
    def occupied_by_display(self, obj):
        if obj.occupied_by:
            return f"{obj.occupied_by.username} ({obj.occupied_by.email})"
        return "—"
    occupied_by_display.short_description = 'Occupied By'
    
    def occupied_since_display(self, obj):
        if obj.occupied_since:
            return obj.occupied_since.strftime("%H:%M")
        return "—"
    occupied_since_display.short_description = 'Since'
    
    def release_selected_seats(self, request, queryset):
        released = 0
        for seat in queryset:
            if not seat.is_available:
                seat.is_available = True
                seat.occupied_by = None
                seat.occupied_since = None
                seat.subject_studying = ""
                seat.study_purpose = ""
                seat.save()
                released += 1
        self.message_user(request, f'{released} seats released.')
    release_selected_seats.short_description = "Release selected seats"
    
    def mark_all_available(self, request, queryset):
        updated = queryset.update(
            is_available=True, 
            occupied_by=None, 
            occupied_since=None,
            subject_studying="",
            study_purpose=""
        )
        self.message_user(request, f'{updated} seats marked as available.')
    mark_all_available.short_description = "Mark all as available"