import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

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
    USER_TYPES = [('teacher', 'Teacher'), ('student', 'Student'), ('admin', 'Admin')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20, blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    avatar_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = CustomUserManager()


# ---------------------
# Academic Structure
# ---------------------
class Institution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    credit_hours = models.IntegerField()
    prerequisites = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# ---------------------
# Class Management
# ---------------------
class Class(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    semester = models.CharField(max_length=20)
    year = models.IntegerField()
    section = models.CharField(max_length=20)
    room = models.CharField(max_length=50)
    schedule = models.TextField()
    max_students = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ClassEnrollment(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('dropped', 'Dropped'), ('completed', 'Completed')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    status_changed_at = models.DateTimeField()

# ---------------------
# Session Management
# ---------------------
class ClassSession(models.Model):
    STATUS_CHOICES = [('scheduled', 'Scheduled'), ('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    session_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# ---------------------
# Attendance Tracking
# ---------------------
class AttendanceRecord(models.Model):
    STATUS_CHOICES = [('present', 'Present'), ('absent', 'Absent'), ('late', 'Late'), ('excused', 'Excused')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    marked_at = models.DateTimeField(auto_now_add=True)
    marked_by_method = models.CharField(max_length=20)
    marked_by_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='marked_attendance')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class QRCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE)
    code = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    scan_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class QRScan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qr_code = models.ForeignKey(QRCode, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    scanned_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)

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

class ParticipationRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(ParticipationCategory, on_delete=models.CASCADE)
    points = models.IntegerField()
    description = models.TextField()
    awarded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='awarded_points')
    awarded_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# ---------------------
# Analytics
# ---------------------
class AttendanceAnalytics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    calculation_date = models.DateField()
    total_sessions = models.IntegerField()
    attended_sessions = models.IntegerField()
    late_sessions = models.IntegerField()
    excused_sessions = models.IntegerField()
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    calculated_at = models.DateTimeField()

class ParticipationAnalytics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    calculation_date = models.DateField()
    total_points = models.IntegerField()
    possible_points = models.IntegerField()
    participation_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    rank_in_class = models.IntegerField()
    calculated_at = models.DateTimeField()

# ---------------------
# Notifications and Alerts
# ---------------------
class Notification(models.Model):
    NOTIF_TYPES = [
        ('attendance_reminder', 'Attendance Reminder'),
        ('low_attendance_alert', 'Low Attendance'),
        ('participation_milestone', 'Participation Milestone'),
        ('system_notification', 'System')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=30, choices=NOTIF_TYPES)
    is_read = models.BooleanField(default=False)
    action_url = models.URLField(blank=True, null=True)
    sent_at = models.DateTimeField()
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AttendanceAlert(models.Model):
    ALERT_TYPES = [
        ('low_attendance', 'Low Attendance'),
        ('consecutive_absences', 'Consecutive Absences'),
        ('improvement_needed', 'Improvement Needed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    threshold_value = models.DecimalField(max_digits=5, decimal_places=2)
    current_value = models.DecimalField(max_digits=5, decimal_places=2)
    is_resolved = models.BooleanField(default=False)
    triggered_at = models.DateTimeField()
    resolved_at = models.DateTimeField(blank=True, null=True)

# ---------------------
# System Settings and Logs
# ---------------------
class ClassSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    attendance_rules = models.JSONField()
    participation_rules = models.JSONField()
    notification_preferences = models.JSONField()
    grading_weights = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SystemLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=100)
    entity_id = models.UUIDField()
    old_values = models.JSONField()
    new_values = models.JSONField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# ---------------------
# Files & Reports
# ---------------------
class File(models.Model):
    FILE_TYPES = [
        ('profile_image', 'Profile Image'),
        ('class_document', 'Class Document'),
        ('report', 'Report'),
        ('export', 'Export'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    filename = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    mime_type = models.CharField(max_length=100)
    file_size = models.IntegerField()
    file_type = models.CharField(max_length=30, choices=FILE_TYPES)
    related_entity_id = models.UUIDField(null=True, blank=True)
    related_entity_type = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Report(models.Model):
    REPORT_TYPES = [
        ('attendance', 'Attendance'),
        ('participation', 'Participation'),
        ('combined', 'Combined'),
        ('student_profile', 'Student Profile')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    filters = models.JSONField()
    data = models.JSONField()
    file_path = models.CharField(max_length=500)
    generated_at = models.DateTimeField()
    expires_at = models.DateTimeField()
