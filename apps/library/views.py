# library/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import LibrarySeat
from .forms import OccupySeatForm, SeatFilterForm
from collections import Counter
import json

# ==================== HELPER FUNCTIONS ====================

def auto_release_expired_seats():
    """Auto-release seats where time has expired"""
    expired_seats = LibrarySeat.objects.filter(is_available=False)
    released_count = 0
    
    for seat in expired_seats:
        if seat.occupied_since:
            current_time = timezone.now()
            duration = current_time - seat.occupied_since
            minutes_passed = duration.total_seconds() / 60
            
            if minutes_passed > seat.expected_duration:
                seat.is_available = True
                seat.occupied_by = None
                seat.occupied_since = None
                seat.subject_studying = ""
                seat.study_purpose = ""
                seat.save()
                released_count += 1
    
    return released_count

def get_library_stats():
    """Get library statistics"""
    total_seats = 50  # Fixed 50 ground floor seats
    available_seats = LibrarySeat.objects.filter(is_available=True).count()
    occupied_seats = total_seats - available_seats
    
    return {
        'total_seats': total_seats,
        'available_seats': available_seats,
        'occupied_seats': occupied_seats,
        'occupancy_rate': (occupied_seats / total_seats * 100) if total_seats > 0 else 0,
    }

# ==================== MAIN VIEWS ====================

@login_required
def library_seat_map(request):
    """
    Main view showing ground floor library with 50 seats
    Only accessible to logged-in users (students, staff, admin)
    """
    # Auto-release expired seats
    auto_release_expired_seats()
    
    # Get filter parameters
    form = SeatFilterForm(request.GET or None)
    seats = LibrarySeat.objects.all().select_related('occupied_by')
    
    # Apply filters if provided
    if form.is_valid():
        seat_type = form.cleaned_data.get('seat_type')
        zone = form.cleaned_data.get('zone')
        availability = form.cleaned_data.get('availability')
        
        if seat_type:
            seats = seats.filter(seat_type=seat_type)
        if zone:
            seats = seats.filter(zone=zone)
        if availability == 'available':
            seats = seats.filter(is_available=True)
        elif availability == 'occupied':
            seats = seats.filter(is_available=False)
    
    # Get user's current seat
    user_seat = None
    if request.user.is_authenticated:
        user_seat = LibrarySeat.objects.filter(
            occupied_by=request.user, 
            is_available=False
        ).first()
    
    # Get all currently studying students
    studying_students = LibrarySeat.objects.filter(
        is_available=False
    ).select_related('occupied_by').order_by('occupied_since')
    
    # Get statistics
    stats = get_library_stats()
    
    # Group seats by zone for display
    zones = {}
    for seat in seats:
        zone_name = seat.get_zone_display()
        if zone_name not in zones:
            zones[zone_name] = []
        zones[zone_name].append(seat)
    
    # Prepare context
    context = {
        'seats': seats,
        'zones': zones,
        'form': form,
        'user_seat': user_seat,
        'studying_students': studying_students,
        **stats,  # Unpack statistics
    }
    
    return render(request, 'library/seat_map.html', context)

@login_required
def library_dashboard(request):
    """
    Library dashboard with comprehensive statistics and analytics
    """
    # Auto-release expired seats
    auto_release_expired_seats()
    
    # Get basic statistics
    stats = get_library_stats()
    
    # Get currently studying students (limit to 10 for dashboard)
    studying_students = LibrarySeat.objects.filter(
        is_available=False
    ).select_related('occupied_by').order_by('-occupied_since')[:10]
    
    # Get subject distribution
    subjects = []
    for seat in LibrarySeat.objects.filter(is_available=False):
        subject = seat.subject_studying.strip() if seat.subject_studying else "General Study"
        subjects.append(subject)
    
    subject_distribution = dict(Counter(subjects))
    
    # Get zone-wise statistics
    zones_data = {}
    for zone_code, zone_name in LibrarySeat._meta.get_field('zone').choices:
        zone_seats = LibrarySeat.objects.filter(zone=zone_code)
        if zone_seats.exists():
            zones_data[zone_name] = {
                'total': zone_seats.count(),
                'available': zone_seats.filter(is_available=True).count(),
                'percentage': (zone_seats.filter(is_available=True).count() / zone_seats.count() * 100)
            }
    
    # Get purpose distribution
    purposes = []
    for seat in LibrarySeat.objects.filter(is_available=False):
        purpose = seat.get_study_purpose_display() if seat.study_purpose else "General Study"
        purposes.append(purpose)
    
    purpose_distribution = dict(Counter(purposes))
    
    # Get user's seat if any
    user_seat = None
    if request.user.is_authenticated:
        user_seat = LibrarySeat.objects.filter(
            occupied_by=request.user, 
            is_available=False
        ).first()
    
    # Get recent activities (last 10 seat changes)
    recent_activities = []
    occupied_seats = LibrarySeat.objects.filter(is_available=False).order_by('-occupied_since')
    for seat in occupied_seats[:10]:
        recent_activities.append({
            'student': seat.occupied_by.username,
            'seat': seat.seat_number,
            'subject': seat.subject_studying or "General Study",
            'time': seat.occupied_since,
            'duration': seat.get_occupation_time_display(),
        })
    
    # Get peak hours data (mock data for now)
    peak_hours = [
        {'hour': '8-9 AM', 'occupancy': 15},
        {'hour': '9-10 AM', 'occupancy': 25},
        {'hour': '10-11 AM', 'occupancy': 35},
        {'hour': '11-12 PM', 'occupancy': 40},
        {'hour': '12-1 PM', 'occupancy': 45},
        {'hour': '1-2 PM', 'occupancy': 50},
        {'hour': '2-3 PM', 'occupancy': 48},
        {'hour': '3-4 PM', 'occupancy': 42},
        {'hour': '4-5 PM', 'occupancy': 38},
        {'hour': '5-6 PM', 'occupancy': 30},
    ]
    
    # Prepare context
    context = {
        **stats,
        'studying_students': studying_students,
        'subject_distribution': subject_distribution,
        'purpose_distribution': purpose_distribution,
        'zones': zones_data,
        'user_seat': user_seat,
        'recent_activities': recent_activities,
        'peak_hours': peak_hours,
        'current_time': timezone.now(),
    }
    
    return render(request, 'library/dashboard.html', context)

@login_required
def occupy_seat(request, seat_id):
    """
    Student occupies a seat with study details
    """
    seat = get_object_or_404(LibrarySeat, id=seat_id)
    
    if request.method == 'POST':
        form = OccupySeatForm(request.POST)
        
        if form.is_valid():
            # Check if seat is available
            if not seat.is_available:
                messages.error(request, f"Seat {seat.seat_number} is already occupied!")
                return redirect('library:seat_map')
            
            # Check if user already has a seat
            user_seat = LibrarySeat.objects.filter(
                occupied_by=request.user, 
                is_available=False
            ).first()
            
            if user_seat:
                messages.warning(request, 
                    f"You are already occupying Seat {user_seat.seat_number}. "
                    f"Release it first to occupy another seat.")
                return redirect('library:seat_map')
            
            # Validate expected duration
            expected_duration = form.cleaned_data['expected_duration']
            if expected_duration < 30 or expected_duration > 240:
                messages.error(request, "Study duration must be between 30 minutes and 4 hours.")
                return render(request, 'library/occupy_seat.html', {
                    'seat': seat,
                    'form': form
                })
            
            # Occupy the seat with study details
            seat.is_available = False
            seat.occupied_by = request.user
            seat.occupied_since = timezone.now()
            seat.expected_duration = expected_duration
            seat.subject_studying = form.cleaned_data['subject_studying']
            seat.study_purpose = form.cleaned_data['study_purpose']
            seat.save()
            
            messages.success(request, 
                f"✅ You have occupied Seat {seat.seat_number} "
                f"for {seat.expected_duration} minutes.\n"
                f"📚 Subject: {seat.subject_studying or 'General Study'}")
            
            return redirect('library:seat_map')
        else:
            messages.error(request, "Please correct the errors below.")
    
    else:
        # GET request - show empty form
        form = OccupySeatForm()
    
    # Show occupation form
    return render(request, 'library/occupy_seat.html', {
        'seat': seat,
        'form': form
    })

@login_required
def release_seat(request, seat_id):
    """
    Student releases their occupied seat
    """
    seat = get_object_or_404(LibrarySeat, id=seat_id)
    
    # Check if seat is already available
    if seat.is_available:
        messages.error(request, "This seat is already available!")
        return redirect('library:seat_map')
    
    # Check if user is the one occupying this seat
    if seat.occupied_by != request.user:
        messages.error(request, "You can only release your own seat!")
        return redirect('library:seat_map')
    
    # Calculate study duration
    duration = seat.get_occupation_time_minutes()
    
    # Release the seat
    seat.is_available = True
    seat.occupied_by = None
    seat.occupied_since = None
    seat.subject_studying = ""
    seat.study_purpose = ""
    seat.save()
    
    # Show success message with duration
    if duration < 60:
        duration_msg = f"{duration} minutes"
    else:
        hours = duration // 60
        minutes = duration % 60
        duration_msg = f"{hours} hour{'s' if hours > 1 else ''} and {minutes} minute{'s' if minutes > 1 else ''}"
    
    messages.success(request, 
        f"✅ You have released Seat {seat.seat_number}.\n"
        f"⏱️ Study duration: {duration_msg}")
    
    return redirect('library:seat_map')

@login_required
def release_my_seat(request):
    """
    Quick release of user's currently occupied seat
    """
    seat = LibrarySeat.objects.filter(
        occupied_by=request.user, 
        is_available=False
    ).first()
    
    if seat:
        duration = seat.get_occupation_time_minutes()
        
        # Release the seat
        seat.is_available = True
        seat.occupied_by = None
        seat.occupied_since = None
        seat.subject_studying = ""
        seat.study_purpose = ""
        seat.save()
        
        # Show success message
        if duration < 60:
            duration_msg = f"{duration} minutes"
        else:
            hours = duration // 60
            minutes = duration % 60
            duration_msg = f"{hours} hour{'s' if hours > 1 else ''} and {minutes} minute{'s' if minutes > 1 else ''}"
        
        messages.success(request, 
            f"✅ Released Seat {seat.seat_number}.\n"
            f"⏱️ Study duration: {duration_msg}")
    else:
        messages.info(request, "ℹ️ You don't have any seat occupied.")
    
    return redirect('library:seat_map')

@login_required
def seat_detail(request, seat_id):
    """
    View detailed seat information with occupation history
    """
    seat = get_object_or_404(LibrarySeat, id=seat_id)
    
    # Get user's current seat
    user_seat = None
    if request.user.is_authenticated:
        user_seat = LibrarySeat.objects.filter(
            occupied_by=request.user, 
            is_available=False
        ).first()
    
    # Get similar seats (same zone)
    similar_seats = LibrarySeat.objects.filter(
        zone=seat.zone
    ).exclude(id=seat.id)[:4]
    
    # Get expected end time
    expected_end_time = None
    if not seat.is_available and seat.occupied_since:
        expected_end_time = seat.occupied_since + timezone.timedelta(minutes=seat.expected_duration)
    
    # Check if seat is overstaying
    is_overstaying = False
    if not seat.is_available and seat.occupied_since:
        current_duration = seat.get_occupation_time_minutes()
        is_overstaying = current_duration > seat.expected_duration
    
    # Prepare context
    context = {
        'seat': seat,
        'user_seat': user_seat,
        'similar_seats': similar_seats,
        'expected_end_time': expected_end_time,
        'is_overstaying': is_overstaying,
        'can_occupy': seat.is_available and not user_seat,
        'can_release': not seat.is_available and seat.occupied_by == request.user,
        'can_extend': not seat.is_available and seat.occupied_by == request.user and not is_overstaying,
    }
    
    return render(request, 'library/seat_detail.html', context)

@login_required
def current_students(request):
    """
    View all currently studying students with detailed information
    """
    # Get all studying students
    studying_students = LibrarySeat.objects.filter(
        is_available=False
    ).select_related('occupied_by').order_by('-occupied_since')
    
    # Get statistics
    stats = get_library_stats()
    
    # Get subject distribution
    subjects = []
    for seat in studying_students:
        subject = seat.subject_studying.strip() if seat.subject_studying else "General Study"
        subjects.append(subject)
    
    subject_distribution = dict(Counter(subjects))
    
    # Get purpose distribution
    purposes = []
    for seat in studying_students:
        purpose = seat.get_study_purpose_display() if seat.study_purpose else "General Study"
        purposes.append(purpose)
    
    purpose_distribution = dict(Counter(purposes))
    
    # Get zone distribution
    zones = {}
    for seat in studying_students:
        zone_name = seat.get_zone_display()
        zones[zone_name] = zones.get(zone_name, 0) + 1
    
    # Pagination
    paginator = Paginator(studying_students, 20)  # 20 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get user's seat if any
    user_seat = None
    if request.user.is_authenticated:
        user_seat = LibrarySeat.objects.filter(
            occupied_by=request.user, 
            is_available=False
        ).first()
    
    # Prepare context
    context = {
        'page_obj': page_obj,
        'studying_students': page_obj.object_list,
        'total_students': studying_students.count(),
        'subject_distribution': subject_distribution,
        'purpose_distribution': purpose_distribution,
        'zone_distribution': zones,
        'user_seat': user_seat,
        **stats,
    }
    
    return render(request, 'library/current_students.html', context)

@login_required
def extend_study_time(request, seat_id):
    """
    Extend study duration for occupied seat
    """
    if request.method == 'POST':
        seat = get_object_or_404(LibrarySeat, id=seat_id)
        
        # Check if user is the occupant
        if seat.occupied_by != request.user:
            messages.error(request, "You can only extend your own seat time!")
            return redirect('library:seat_map')
        
        try:
            additional_minutes = int(request.POST.get('additional_minutes', 30))
            
            # Validate additional time
            if additional_minutes < 15:
                messages.error(request, "Minimum extension is 15 minutes.")
            elif additional_minutes > 120:
                messages.error(request, "Maximum extension is 2 hours.")
            else:
                # Calculate new total duration
                current_duration = seat.get_occupation_time_minutes()
                new_total = seat.expected_duration + additional_minutes
                
                # Check if exceeds maximum (4 hours)
                if new_total > 240:
                    messages.error(request, "Maximum total study time is 4 hours!")
                else:
                    # Extend the duration
                    seat.expected_duration = new_total
                    seat.save()
                    
                    messages.success(request, 
                        f"✅ Study time extended by {additional_minutes} minutes.\n"
                        f"⏱️ New expected duration: {new_total} minutes")
        
        except ValueError:
            messages.error(request, "Please enter a valid number of minutes.")
    
    return redirect('library:seat_detail', seat_id=seat_id)

# ==================== API VIEWS ====================

@login_required
def seat_status_api(request):
    """
    API endpoint for real-time seat status (AJAX)
    """
    # Get all seats with minimal data
    seats = LibrarySeat.objects.all().values(
        'id', 'seat_number', 'is_available', 
        'occupied_by__username', 'occupied_by__email',
        'occupied_since', 'expected_duration',
        'subject_studying', 'study_purpose',
        'zone', 'seat_type'
    )
    
    # Get user's seat if any
    user_seat = None
    if request.user.is_authenticated:
        user_seat_obj = LibrarySeat.objects.filter(
            occupied_by=request.user, 
            is_available=False
        ).first()
        
        if user_seat_obj:
            user_seat = {
                'seat_number': user_seat_obj.seat_number,
                'occupied_since': user_seat_obj.occupied_since.isoformat() if user_seat_obj.occupied_since else None,
                'expected_duration': user_seat_obj.expected_duration,
                'subject_studying': user_seat_obj.subject_studying,
            }
    
    # Get statistics
    stats = get_library_stats()
    
    # Prepare response data
    data = {
        'seats': list(seats),
        'user_seat': user_seat,
        'stats': stats,
        'timestamp': timezone.now().isoformat(),
        'total_seats': 50,
    }
    
    return JsonResponse(data)

@login_required
def my_study_history(request):
    """
    View user's study history
    """
    # In a real app, you would have a StudyHistory model
    # For now, we'll show currently occupied seat
    
    user_seat = None
    if request.user.is_authenticated:
        user_seat = LibrarySeat.objects.filter(
            occupied_by=request.user, 
            is_available=False
        ).first()
    
    # Get stats about user's library usage
    total_study_sessions = LibrarySeat.objects.filter(
        occupied_by=request.user
    ).count()
    
    # Calculate average study time (mock data for now)
    average_study_time = 75  # minutes
    
    context = {
        'user_seat': user_seat,
        'total_study_sessions': total_study_sessions,
        'average_study_time': average_study_time,
        'preferred_subject': "Computer Science",  # Mock data
        'most_common_zone': "Computer Section",  # Mock data
    }
    
    return render(request, 'library/my_study_history.html', context)

# ==================== ADMIN VIEWS ====================

@login_required
def admin_dashboard(request):
    """
    Admin dashboard for library management
    Only accessible to staff/admin
    """
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('library:seat_map')
    
    # Auto-release expired seats
    released_count = auto_release_expired_seats()
    
    # Get statistics
    stats = get_library_stats()
    
    # Get all occupied seats
    occupied_seats = LibrarySeat.objects.filter(
        is_available=False
    ).select_related('occupied_by').order_by('occupied_since')
    
    # Get overstaying students
    overstaying_students = []
    for seat in occupied_seats:
        if seat.get_occupation_time_minutes() > seat.expected_duration:
            overstaying_students.append(seat)
    
    # Get zone-wise analysis
    zone_analysis = {}
    for zone_code, zone_name in LibrarySeat._meta.get_field('zone').choices:
        zone_seats = LibrarySeat.objects.filter(zone=zone_code)
        if zone_seats.exists():
            zone_analysis[zone_name] = {
                'total': zone_seats.count(),
                'occupied': zone_seats.filter(is_available=False).count(),
                'occupancy_rate': (zone_seats.filter(is_available=False).count() / zone_seats.count() * 100),
            }
    
    # Get subject popularity
    subjects = []
    for seat in occupied_seats:
        subject = seat.subject_studying.strip() if seat.subject_studying else "General Study"
        subjects.append(subject)
    
    subject_popularity = dict(Counter(subjects))
    
    # Prepare context
    context = {
        **stats,
        'occupied_seats': occupied_seats,
        'overstaying_students': overstaying_students,
        'overstaying_count': len(overstaying_students),
        'zone_analysis': zone_analysis,
        'subject_popularity': subject_popularity,
        'released_count': released_count,
        'total_students_studying': occupied_seats.count(),
    }
    
    return render(request, 'library/admin_dashboard.html', context)

@login_required
def admin_release_seat(request, seat_id):
    """
    Admin forcefully releases a seat
    """
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('library:seat_map')
    
    seat = get_object_or_404(LibrarySeat, id=seat_id)
    
    if seat.is_available:
        messages.warning(request, f"Seat {seat.seat_number} is already available.")
    else:
        student_name = seat.occupied_by.username if seat.occupied_by else "Unknown"
        seat.is_available = True
        seat.occupied_by = None
        seat.occupied_since = None
        seat.subject_studying = ""
        seat.study_purpose = ""
        seat.save()
        
        messages.success(request, 
            f"✅ Seat {seat.seat_number} has been released.\n"
            f"👤 Student: {student_name}")
    
    return redirect('library:admin_dashboard')

# ==================== PUBLIC VIEWS ====================

def library_info(request):
    """
    Public information about the library
    """
    stats = get_library_stats()
    
    # Get library rules and information
    library_info = {
        'name': "Ground Floor Library",
        'total_seats': 50,
        'floors': ["Ground Floor Only"],
        'opening_hours': {
            'weekdays': "8:00 AM - 10:00 PM",
            'saturday': "9:00 AM - 6:00 PM",
            'sunday': "10:00 AM - 4:00 PM",
        },
        'rules': [
            "Maximum study duration: 4 hours per session",
            "One seat per student at a time",
            "Silence must be maintained in Quiet Zone",
            "Food and drinks are not allowed",
            "Please release your seat when done",
            "Respect other students' study space",
        ],
        'amenities': [
            "Wi-Fi throughout the library",
            "Power outlets at every seat",
            "Computer monitors in Computer Section",
            "Group study tables",
            "Printing facilities",
            "Water dispenser",
        ]
    }
    
    context = {
        **stats,
        'library_info': library_info,
    }
    
    return render(request, 'library/library_info.html', context)

# ==================== ERROR VIEWS ====================

def library_home(request):
    """
    Library home page - redirects to seat map if logged in, else to info
    """
    if request.user.is_authenticated:
        return redirect('library:seat_map')
    else:
        return redirect('library:library_info')

def handler404(request, exception):
    """Custom 404 handler for library app"""
    return render(request, 'library/404.html', status=404)

def handler500(request):
    """Custom 500 handler for library app"""
    return render(request, 'library/500.html', status=500)