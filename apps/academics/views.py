from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, FileResponse
from django.db.models import Q
import os
from .models import Course, Subject, Note, StudyMaterial
from .forms import CourseForm, SubjectForm, NoteForm, StudyMaterialForm

# ===== STUDENT VIEWS =====
@login_required
def student_academics_dashboard(request):
    """Student view - See available notes and materials"""
    # Get student's courses based on their profile
    try:
        student_profile = request.user.student_profile
        student_courses = Course.objects.filter(
            department=student_profile.department,
            semester=student_profile.semester
        )
        subjects = Subject.objects.filter(course__in=student_courses)
    except:
        # If no student profile, show all approved materials
        student_courses = Course.objects.all()
        subjects = Subject.objects.all()
    
    # Get approved notes and materials
    notes = Note.objects.filter(is_approved=True, subject__in=subjects)
    study_materials = StudyMaterial.objects.filter(subject__in=subjects)
    
    context = {
        'courses': student_courses,
        'subjects': subjects,
        'notes': notes[:10],  # Recent 10 notes
        'study_materials': study_materials[:10],  # Recent 10 materials
        'user_role': request.user.role,
    }
    return render(request, 'academics/student_dashboard.html', context)

@login_required
def note_list(request):
    """Student view - List all approved notes"""
    if request.user.role == 'student':
        try:
            student_profile = request.user.student_profile
            subjects = Subject.objects.filter(course__department=student_profile.department)
            notes = Note.objects.filter(is_approved=True, subject__in=subjects)
        except:
            notes = Note.objects.filter(is_approved=True)
    else:
        notes = Note.objects.filter(is_approved=True)
    
    # Filter by subject if provided
    subject_filter = request.GET.get('subject', '')
    if subject_filter:
        notes = notes.filter(subject_id=subject_filter)
    
    # Filter by file type if provided
    file_type_filter = request.GET.get('file_type', '')
    if file_type_filter:
        notes = notes.filter(file_type=file_type_filter)
    
    subjects = Subject.objects.all()
    
    context = {
        'notes': notes.order_by('-uploaded_at'),
        'subjects': subjects,
        'subject_filter': subject_filter,
        'file_type_filter': file_type_filter,
    }
    return render(request, 'academics/note_list.html', context)

@login_required
def note_detail(request, pk):
    """Student view - View note details"""
    note = get_object_or_404(Note, pk=pk)
    
    # Check if note is approved or user is staff/admin
    if not note.is_approved and request.user.role == 'student':
        return HttpResponseForbidden("This note is not approved yet.")
    
    context = {
        'note': note,
    }
    return render(request, 'academics/note_detail.html', context)

@login_required
def download_note(request, pk):
    """Download note file"""
    note = get_object_or_404(Note, pk=pk)
    
    # Check if note is approved or user is staff/admin
    if not note.is_approved and request.user.role == 'student':
        return HttpResponseForbidden("This note is not approved yet.")
    
    if note.file:
        response = FileResponse(note.file.open(), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{note.file.name}"'
        return response
    else:
        messages.error(request, 'File not found.')
        return redirect('academics:note_detail', pk=pk)

@login_required
def study_material_list(request):
    """Student view - List all study materials"""
    if request.user.role == 'student':
        try:
            student_profile = request.user.student_profile
            subjects = Subject.objects.filter(course__department=student_profile.department)
            materials = StudyMaterial.objects.filter(subject__in=subjects)
        except:
            materials = StudyMaterial.objects.all()
    else:
        materials = StudyMaterial.objects.all()
    
    # Filter by material type if provided
    material_type_filter = request.GET.get('material_type', '')
    if material_type_filter:
        materials = materials.filter(material_type=material_type_filter)
    
    context = {
        'materials': materials.order_by('-uploaded_at'),
        'material_type_filter': material_type_filter,
    }
    return render(request, 'academics/study_material_list.html', context)

# ===== STAFF/ADMIN VIEWS =====
@login_required
def staff_academics_dashboard(request):
    """Staff/Admin view - Manage academic content"""
    if request.user.role not in ['staff', 'admin']:
        return HttpResponseForbidden("Access denied.")
    
    total_notes = Note.objects.count()
    total_materials = StudyMaterial.objects.count()
    pending_notes = Note.objects.filter(is_approved=False).count()
    
    context = {
        'total_notes': total_notes,
        'total_materials': total_materials,
        'pending_notes': pending_notes,
        'user_role': request.user.role,
    }
    return render(request, 'academics/staff_dashboard.html', context)

@login_required
def upload_note(request):
    """Staff/Admin view - Upload new note"""
    if request.user.role not in ['staff', 'admin']:
        return HttpResponseForbidden("Access denied.")
    
    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.uploaded_by = request.user
            note.save()
            messages.success(request, 'Note uploaded successfully!')
            return redirect('academics:manage_notes')
    else:
        form = NoteForm()
    
    context = {
        'form': form,
        'user_role': request.user.role,
    }
    return render(request, 'academics/upload_note.html', context)

@login_required
def upload_study_material(request):
    """Staff/Admin view - Upload study material"""
    if request.user.role not in ['staff', 'admin']:
        return HttpResponseForbidden("Access denied.")
    
    if request.method == 'POST':
        form = StudyMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = request.user
            material.save()
            messages.success(request, 'Study material uploaded successfully!')
            return redirect('academics:manage_study_materials')
    else:
        form = StudyMaterialForm()
    
    context = {
        'form': form,
        'user_role': request.user.role,
    }
    return render(request, 'academics/upload_study_material.html', context)

@login_required
def manage_notes(request):
    """Staff/Admin view - Manage all notes"""
    if request.user.role not in ['staff', 'admin']:
        return HttpResponseForbidden("Access denied.")
    
    notes = Note.objects.all().order_by('-uploaded_at')
    
    # Filter by approval status
    status_filter = request.GET.get('status', '')
    if status_filter == 'pending':
        notes = notes.filter(is_approved=False)
    elif status_filter == 'approved':
        notes = notes.filter(is_approved=True)
    
    context = {
        'notes': notes,
        'status_filter': status_filter,
    }
    return render(request, 'academics/manage_notes.html', context)

@login_required
def manage_study_materials(request):
    """Staff/Admin view - Manage study materials"""
    if request.user.role not in ['staff', 'admin']:
        return HttpResponseForbidden("Access denied.")
    
    materials = StudyMaterial.objects.all().order_by('-uploaded_at')
    
    context = {
        'materials': materials,
    }
    return render(request, 'academics/manage_study_materials.html', context)

@login_required
def toggle_note_approval(request, pk):
    """Staff/Admin view - Approve/Disapprove note"""
    if request.user.role not in ['staff', 'admin']:
        return HttpResponseForbidden("Access denied.")
    
    note = get_object_or_404(Note, pk=pk)
    note.is_approved = not note.is_approved
    note.save()
    
    status = "approved" if note.is_approved else "disapproved"
    messages.success(request, f'Note {status} successfully!')
    
    return redirect('academics:manage_notes')

@login_required
def delete_note(request, pk):
    """Staff/Admin view - Delete note"""
    if request.user.role not in ['staff', 'admin']:
        return HttpResponseForbidden("Access denied.")
    
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted successfully!')
        return redirect('academics:manage_notes')
    
    return render(request, 'academics/confirm_delete.html', {'object': note})

# ===== COURSE MANAGEMENT =====
@login_required
def manage_courses(request):
    """Staff/Admin view - Manage courses"""
    if request.user.role not in ['staff', 'admin']:
        return HttpResponseForbidden("Access denied.")
    
    courses = Course.objects.all().order_by('semester', 'code')
    
    context = {
        'courses': courses,
    }
    return render(request, 'academics/manage_courses.html', context)

@login_required
def manage_subjects(request):
    """Staff/Admin view - Manage subjects"""
    if request.user.role not in ['staff', 'admin']:
        return HttpResponseForbidden("Access denied.")
    
    subjects = Subject.objects.all().order_by('course', 'name')
    
    context = {
        'subjects': subjects,
    }
    return render(request, 'academics/manage_subjects.html', context)