from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from .models import StudentProfile, Attendance, Grade
from .forms import StudentProfileForm

@login_required
def student_dashboard(request):
    """Student Dashboard - Different views based on role"""
    if request.user.role == 'student':
        # Student sees their own dashboard
        try:
            student_profile = request.user.student_profile
        except StudentProfile.DoesNotExist:
            messages.warning(request, 'Please complete your student profile first.')
            return redirect('student_info:create_profile')
        
        # Get recent attendance
        recent_attendance = Attendance.objects.filter(student=student_profile).order_by('-date')[:10]
        grades = Grade.objects.filter(student=student_profile).order_by('-semester', 'subject')[:10]
        
        # Calculate attendance percentage
        total_classes = Attendance.objects.filter(student=student_profile).count()
        present_classes = Attendance.objects.filter(student=student_profile, status='present').count()
        attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
        
        context = {
            'student_profile': student_profile,
            'recent_attendance': recent_attendance,
            'grades': grades,
            'attendance_percentage': round(attendance_percentage, 2),
            'total_classes': total_classes,
            'present_classes': present_classes,
        }
        return render(request, 'student_info/dashboard.html', context)
    
    else:
        # Staff/Admin sees student management dashboard
        all_students = StudentProfile.objects.all()
        total_students = all_students.count()
        recent_attendance = Attendance.objects.all().order_by('-date')[:10]
        
        context = {
            'all_students': all_students,
            'total_students': total_students,
            'recent_attendance': recent_attendance,
            'user_role': request.user.role,
        }
        return render(request, 'student_info/staff_dashboard.html', context)

@login_required
def create_profile(request):
    """Create student profile"""
    if hasattr(request.user, 'student_profile'):
        messages.info(request, 'You already have a student profile.')
        return redirect('student_info:student_dashboard')
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST)
        if form.is_valid():
            student_profile = form.save(commit=False)
            student_profile.user = request.user
            student_profile.save()
            messages.success(request, 'Student profile created successfully!')
            return redirect('student_info:student_dashboard')
    else:
        form = StudentProfileForm()
    
    return render(request, 'student_info/create_profile.html', {'form': form})

@login_required
def edit_profile(request):
    """Edit student profile"""
    try:
        student_profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.warning(request, 'Please create your student profile first.')
        return redirect('student_info:create_profile')
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=student_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('student_info:student_dashboard')
    else:
        form = StudentProfileForm(instance=student_profile)
    
    return render(request, 'student_info/edit_profile.html', {'form': form})

@login_required
def attendance_report(request):
    """Student's attendance report"""
    try:
        student_profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.warning(request, 'Please complete your student profile first.')
        return redirect('student_info:create_profile')
    
    # Filter parameters
    subject_filter = request.GET.get('subject', '')
    month_filter = request.GET.get('month', '')
    
    attendance_records = Attendance.objects.filter(student=student_profile)
    
    if subject_filter:
        attendance_records = attendance_records.filter(subject__icontains=subject_filter)
    
    if month_filter:
        attendance_records = attendance_records.filter(date__month=month_filter)
    
    # Calculate statistics
    total_classes = attendance_records.count()
    present_count = attendance_records.filter(status='present').count()
    absent_count = attendance_records.filter(status='absent').count()
    late_count = attendance_records.filter(status='late').count()
    
    attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0
    
    context = {
        'student_profile': student_profile,
        'attendance_records': attendance_records.order_by('-date'),
        'total_classes': total_classes,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'attendance_percentage': round(attendance_percentage, 2),
        'subject_filter': subject_filter,
        'month_filter': month_filter,
    }
    
    return render(request, 'student_info/attendance_report.html', context)

@login_required
def grade_report(request):
    """Student's grade report"""
    try:
        student_profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.warning(request, 'Please complete your student profile first.')
        return redirect('student_info:create_profile')
    
    semester_filter = request.GET.get('semester', '')
    
    grades = Grade.objects.filter(student=student_profile)
    
    if semester_filter:
        grades = grades.filter(semester=semester_filter)
    
    # Calculate CGPA
    if grades.exists():
        cgpa = grades.aggregate(avg_gpa=Avg('grade_point'))['avg_gpa'] or 0
    else:
        cgpa = 0
    
    # Group by semester
    grades_by_semester = {}
    for grade in grades:
        if grade.semester not in grades_by_semester:
            grades_by_semester[grade.semester] = []
        grades_by_semester[grade.semester].append(grade)
    
    context = {
        'student_profile': student_profile,
        'grades_by_semester': dict(sorted(grades_by_semester.items())),
        'cgpa': round(cgpa, 2),
        'semester_filter': semester_filter,
    }
    
    return render(request, 'student_info/grade_report.html', context)

@login_required
def student_detail(request, student_id):
    """Staff/Admin view of student details"""
    if not request.user.is_staff and request.user.role != 'admin':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('user_management:dashboard')
    
    student_profile = get_object_or_404(StudentProfile, student_id=student_id)
    
    # Get recent attendance records
    attendance_records = Attendance.objects.filter(student=student_profile).order_by('-date')[:20]
    
    # Get all grades
    grades = Grade.objects.filter(student=student_profile).order_by('semester', 'subject')
    
    context = {
        'student_profile': student_profile,
        'attendance_records': attendance_records,
        'grades': grades,
    }
    
    return render(request, 'student_info/student_detail.html', context)

# NEW FUNCTIONS ADDED HERE:
@login_required
def all_students(request):
    """View all students - For Staff/Admin"""
    if request.user.role not in ['staff', 'admin']:
        messages.error(request, 'Access denied. Staff and Admin only.')
        return redirect('student_info:student_dashboard')
    
    students = StudentProfile.objects.all()
    
    context = {
        'students': students,
        'user_role': request.user.role,
    }
    return render(request, 'student_info/all_students.html', context)

@login_required
def manage_attendance(request):
    """Manage attendance - For Staff/Admin"""
    if request.user.role not in ['staff', 'admin']:
        messages.error(request, 'Access denied. Staff and Admin only.')
        return redirect('student_info:student_dashboard')
    
    attendance_records = Attendance.objects.all().order_by('-date')
    
    context = {
        'attendance_records': attendance_records,
        'user_role': request.user.role,
    }
    return render(request, 'student_info/manage_attendance.html', context)

@login_required
def manage_grades(request):
    """Manage grades - For Staff/Admin"""
    if request.user.role not in ['staff', 'admin']:
        messages.error(request, 'Access denied. Staff and Admin only.')
        return redirect('student_info:student_dashboard')
    
    grades = Grade.objects.all().order_by('-semester', 'student')
    
    context = {
        'grades': grades,
        'user_role': request.user.role,
    }
    return render(request, 'student_info/manage_grades.html', context)

@login_required
def student_reports(request):
    """Student reports - For Staff/Admin"""
    if request.user.role not in ['staff', 'admin']:
        messages.error(request, 'Access denied. Staff and Admin only.')
        return redirect('student_info:student_dashboard')
    
    # Statistics for reports
    total_students = StudentProfile.objects.count()
    total_attendance = Attendance.objects.count()
    present_count = Attendance.objects.filter(status='present').count()
    avg_attendance = (present_count / total_attendance * 100) if total_attendance > 0 else 0
    
    context = {
        'total_students': total_students,
        'total_attendance': total_attendance,
        'avg_attendance': round(avg_attendance, 2),
        'user_role': request.user.role,
    }
    return render(request, 'student_info/student_reports.html', context)