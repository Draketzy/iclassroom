from django import forms
from django.contrib.auth.models import User
from .models import User
from .models import Class, ClassSession, Attendance
class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your last name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email address'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'avatar_url']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your phone number'
            }),
            'avatar_url': forms.FileInput(attrs={
                'class': 'form-file-input',
                'accept': 'image/*'
            }),
            
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
       
class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['course_name', 'semester', 'section', 'room', 'schedule']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course_name'].widget.attrs.update({
            'class': 'form-control modern-input',
            'placeholder': 'e.g., Introduction to Computer Science'
        })
        self.fields['semester'].widget.attrs.update({
            'class': 'form-select modern-select'
        })
        self.fields['section'].widget.attrs.update({
            'class': 'form-control modern-input',
            'placeholder': 'e.g., A, B, 01'
        })
        self.fields['room'].widget.attrs.update({
            'class': 'form-control modern-input',
            'placeholder': 'e.g., Room 101, Online'
        })
        self.fields['schedule'].widget.attrs.update({
            'class': 'form-control modern-input',
            'placeholder': 'e.g., MWF 9:00-10:00'
        })


class SessionForm(forms.ModelForm):
    class Meta:
        model = ClassSession
        fields = ['session_date', 'start_time', 'end_time', 'topic', 'notes']
        widgets = {
            'session_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'topic': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
        }

# class UserSettingsForm(forms.ModelForm):
#     class Meta:
#         model = UserSettings
#         fields = [
#             'email_notifications',
#             'push_notifications',
#             'attendance_reminders',
#             'weekly_reports',
#             'theme_preference',
#             'language',
#             'timezone',
#             'privacy_profile',
#             'privacy_attendance'
#         ]
#         widgets = {
#             'email_notifications': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
#             'push_notifications': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
#             'attendance_reminders': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
#             'weekly_reports': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
#             'theme_preference': forms.Select(attrs={'class': 'form-select'}),
#             'language': forms.Select(attrs={'class': 'form-select'}),
#             'timezone': forms.Select(attrs={'class': 'form-select'}),
#             'privacy_profile': forms.Select(attrs={'class': 'form-select'}),
#             'privacy_attendance': forms.Select(attrs={'class': 'form-select'}),
#         }