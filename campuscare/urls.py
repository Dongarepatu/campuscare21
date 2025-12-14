from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Main site routes
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('features/', views.features_view, name='features'),
    
    # App routes
    path('auth/', include('user_management.urls')),
    path('student/', include('student_info.urls')), 
    # path('admissions/', include('admissions.urls')),
    path('library/', include('library.urls')),
    path('academics/', include('academics.urls')),
    # path('student/', include('student_info.urls')),
    # path('staff/', include('staff_management.urls')),
]

# Add media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'campuscare.views.handler404'
handler500 = 'campuscare.views.handler500'
handler403 = 'campuscare.views.handler403'
handler400 = 'campuscare.views.handler400'