from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import SessionListView, SessionCreateView, start_session, complete_session
urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/class/<uuid:class_id>/', views.class_detail, name='class_detail'),

    # student urls
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('enroll/', views.enroll_in_class, name='enroll_in_class'),
    path('student/progress/', views.student_progress, name='student_progress'),

    # Forgot password URLs
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),

    # Email verification URLs
    path('registration-complete/', views.registration_complete, name='registration_complete'),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),

    # Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
     path('upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('remove-avatar/', views.remove_avatar, name='remove_avatar'),

    # ... other URLs ...
    path('classes/<uuid:class_id>/sessions/', SessionListView.as_view(), name='session_list'),
    path('classes/<uuid:class_id>/sessions/new/', SessionCreateView.as_view(), name='create_session'),
    path('sessions/<uuid:session_id>/start/', start_session, name='start_session'),
    path('sessions/<uuid:session_id>/complete/', complete_session, name='complete_session'),
    path('sessions/<uuid:session_id>/attendance/', views.take_attendance, name='take_attendance'),
    # For participation reports (add this if you haven't)
    path('class/<uuid:class_id>/student/<uuid:student_id>/participation-report/',
     views.student_participation_report,
     name='student_participation_report'),
    path('class/<uuid:class_id>/student/<uuid:student_id>/attendance-report/',
         views.student_attendance_report,
         name='student_attendance_report'),
    
    path('class/<uuid:class_id>/generate-report/', views.generate_excel_report, name='generate_report'),
    # Settings URLs
    # path('settings/', views.settings_view, name='settings'),
    # path('settings/update/', views.settings_update, name='settings_update'),
    # path('settings/change-password/', views.change_password, name='change_password'),
    # path('settings/delete-account/', views.delete_account, name='delete_account'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)