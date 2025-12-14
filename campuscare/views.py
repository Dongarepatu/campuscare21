from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home_view(request):
    """Public landing page"""
    context = {
        'title': 'Welcome to CampusCare',
        'description': 'Comprehensive Campus Management System'
    }
    return render(request, 'home.html', context)

def about_view(request):
    """About page"""
    return render(request, 'about.html')

def contact_view(request):
    """Contact page"""
    return render(request, 'contact.html')

def features_view(request):
    """Features page"""
    features = [
        {
            'title': 'Student Management',
            'description': 'Manage student records, attendance, and academic progress.',
            'icon': 'fas fa-user-graduate'
        },
        {
            'title': 'Library System',
            'description': 'Digital library with seat booking and book management.',
            'icon': 'fas fa-book'
        },
        {
            'title': 'Online Admissions',
            'description': 'Streamlined admission process with online applications.',
            'icon': 'fas fa-file-alt'
        },
        {
            'title': 'Study Materials',
            'description': 'Access to course materials and study resources.',
            'icon': 'fas fa-file-pdf'
        },
        {
            'title': 'Staff Management',
            'description': 'Comprehensive faculty and staff management system.',
            'icon': 'fas fa-chalkboard-teacher'
        },
        {
            'title': 'Role-based Access',
            'description': 'Secure access control for admin, staff, and students.',
            'icon': 'fas fa-shield-alt'
        }
    ]
    return render(request, 'features.html', {'features': features})

# Error handlers
def handler404(request, exception):
    """Custom 404 error page"""
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    """Custom 500 error page"""
    return render(request, 'errors/500.html', status=500)

def handler403(request, exception):
    """Custom 403 error page"""
    return render(request, 'errors/403.html', status=403)

def handler400(request, exception):
    """Custom 400 error page"""
    return render(request, 'errors/400.html', status=400)