import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import pytz
from django.core.validators import MinValueValidator, MaxValueValidator
# ---------------------
# Custom User
# ---------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class UserType(models.TextChoices):
        TEACHER = 'teacher', 'Teacher'
        STUDENT = 'student', 'Student'
        ADMIN = 'admin', 'Admin'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20, blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=UserType.choices)
    avatar_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = CustomUserManager()
    
     
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def get_avatar_url(self):
        return self.avatar_url if self.avatar_url else None

# ---------------------
# Academic Structure
# ---------------------


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

# ---------------------
# Class Management
# ---------------------
class Class(models.Model):
    SEMESTER_CHOICES = [
        ('1', '1st Semester'),
        ('2', '2nd Semester'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_name = models.CharField(
        max_length=100,
        default='Introduction to Computer Science',  # Add default value here
        blank=True  # Optional: Allows empty values if needed
    )
    semester = models.CharField(
        max_length=1,
        choices=SEMESTER_CHOICES,
        default='1'
    )
    section = models.CharField(max_length=10)
    teacher = models.ForeignKey(User, on_delete=models.PROTECT, limit_choices_to={'user_type': User.UserType.TEACHER})
    room = models.CharField(max_length=50)
    schedule = models.CharField(max_length=100)  # e.g., "MWF 9:00-10:00"
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Classes"
        unique_together = ('course_name', 'semester', 'section')

    def __str__(self):
        return f"{self.course.code} - {self.section} ({self.semester})"
class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        DROPPED = 'dropped', 'Dropped'
        COMPLETED = 'completed', 'Completed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': User.UserType.STUDENT})
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status_changed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'class_instance')

    def __str__(self):
        return f"{self.student} in {self.class_instance}"
    
# ---------------------
# Session Management
# ---------------------
class ClassSession(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'Scheduled'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    session_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    topic = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['session_date', 'start_time']

    def __str__(self):
        return f"{self.class_instance} on {self.session_date}"
    

# ---------------------
# Attendance Tracking
# ---------------------
class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'
        LATE = 'late', 'Late'
        EXCUSED = 'excused', 'Excused'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': User.UserType.STUDENT})
    status = models.CharField(max_length=10, choices=Status.choices)
    marked_at = models.DateTimeField(auto_now_add=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='marked_attendances')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'student')
        verbose_name_plural = "Attendance Records"

    def __str__(self):
        return f"{self.student} - {self.get_status_display()}"

class QRCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE)
    code = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    scan_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# ---------------------
# Participation Tracking
# ---------------------
class ParticipationCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    default_points = models.IntegerField()
    color = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Participation Categories"

    def __str__(self):
        return f"{self.name} ({self.class_instance})"

class Participation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': User.UserType.STUDENT})
    category = models.ForeignKey(ParticipationCategory, on_delete=models.PROTECT)
    points = models.IntegerField(validators=[MinValueValidator(1)])
    description = models.TextField(blank=True)
    awarded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='awarded_participations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.points} pts for {self.student}"

# ---------------------
# Analytics
# ---------------------


# ---------------------
# Notifications and Alerts
# ---------------------
class Notification(models.Model):
    class NotificationType(models.TextChoices):
        ATTENDANCE = 'attendance', 'Attendance'
        PARTICIPATION = 'participation', 'Participation'
        SYSTEM = 'system', 'System'
        CLASS = 'class', 'Class Update'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    is_read = models.BooleanField(default=False)
    related_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} for {self.user}"

class StudentAnalytics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': User.UserType.STUDENT})
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    calculation_date = models.DateField()
    total_sessions = models.IntegerField()
    attended_sessions = models.IntegerField()
    late_sessions = models.IntegerField()
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    total_points = models.IntegerField()
    average_points = models.DecimalField(max_digits=5, decimal_places=2)
    participation_rank = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Student Analytics"
        unique_together = ('student', 'class_instance', 'calculation_date')

    def __str__(self):
        return f"Analytics for {self.student}"

# ---------------------
# System Settings and Logs
# ---------------------
# class ClassSettings(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
#     attendance_rules = models.JSONField()
#     participation_rules = models.JSONField()
#     notification_preferences = models.JSONField()
#     grading_weights = models.JSONField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

# class SystemLog(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     action = models.CharField(max_length=255)
#     entity_type = models.CharField(max_length=100)
#     entity_id = models.UUIDField()
#     old_values = models.JSONField()
#     new_values = models.JSONField()
#     ip_address = models.GenericIPAddressField()
#     user_agent = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

# ---------------------
# Files & Reports
# ---------------------
# class File(models.Model):
#     FILE_TYPES = [
#         ('profile_image', 'Profile Image'),
#         ('class_document', 'Class Document'),
#         ('report', 'Report'),
#         ('export', 'Export'),
#     ]

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     filename = models.CharField(max_length=255)
#     original_filename = models.CharField(max_length=255)
#     file_path = models.CharField(max_length=500)
#     mime_type = models.CharField(max_length=100)
#     file_size = models.IntegerField()
#     file_type = models.CharField(max_length=30, choices=FILE_TYPES)
#     related_entity_id = models.UUIDField(null=True, blank=True)
#     related_entity_type = models.CharField(max_length=100, null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

# class Report(models.Model):
#     REPORT_TYPES = [
#         ('attendance', 'Attendance'),
#         ('participation', 'Participation'),
#         ('combined', 'Combined'),
#         ('student_profile', 'Student Profile')
#     ]

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
#     class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
#     report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
#     filters = models.JSONField()
#     data = models.JSONField()
#     file_path = models.CharField(max_length=500)
#     generated_at = models.DateTimeField()
#     expires_at = models.DateTimeField()

# class UserSettings(models.Model):
#     THEME_CHOICES = [
#         ('light', 'Light'),
#         ('dark', 'Dark'),
#         ('auto', 'Auto'),
#     ]
    
#     LANGUAGE_CHOICES = [
#         ('en', 'English'),
#         ('es', 'Spanish'),
#         ('fr', 'French'),
#         ('de', 'German'),
#     ]
    
#     PRIVACY_CHOICES = [
#         ('public', 'Public'),
#         ('private', 'Private'),
#         ('institution', 'Institution Only'),
#     ]
    
#     TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.common_timezones]
    
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
    
#     # Notification Settings
#     email_notifications = models.BooleanField(default=True)
#     push_notifications = models.BooleanField(default=True)
#     attendance_reminders = models.BooleanField(default=True)
#     weekly_reports = models.BooleanField(default=True)
    
#     # Appearance Settings
#     theme_preference = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
#     language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
#     timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES, default='UTC')
    
#     # Privacy Settings
#     privacy_profile = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='institution')
#     privacy_attendance = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='private')
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"{self.user.username}'s Settings"