from django import forms
from django.contrib.auth.models import User
from .models import User

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
        fields = ['phone', 'avatar_url']
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