from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .forms import UserProfileForm
from .models import User
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Optionally redirect based on type again here

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            if user.user_type == 'teacher':
                return redirect('teacher_dashboard')
            elif user.user_type == 'student':
                return redirect('student_dashboard')
            else:
                return redirect('dashboard')  # fallback
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'classroom/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_type = request.POST.get('user_type')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type
        )
        messages.success(request, "Registration successful! Please login.")
        return redirect('login')
    
    return render(request, 'classroom/register.html')

@login_required

@login_required
def dashboard_view(request):
    if request.user.user_type == 'teacher':
        return redirect('teacher_dashboard')
    elif request.user.user_type == 'student':
        return redirect('student_dashboard')
    else:
        return render(request, 'classroom/dashboard.html')

@login_required
def teacher_dashboard(request):
    return render(request, 'classroom/teacher/teacher_dashboard.html')

@login_required
def student_dashboard(request):
    return render(request, 'classroom/student/student_dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    """Display user profile page"""
    context = {
        'user': request.user,
        'user_type': getattr(request.user, 'user_type', 'student'),
    }

    return render(request, 'classroom/profile.html', context)

@login_required
def profile_edit(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)

            # Save avatar separately if provided
            if 'avatar' in request.FILES:
                avatar = request.FILES['avatar']
                user.avatar_url = f"/media/avatars/{avatar.name}"
                with open(f"media/avatars/{avatar.name}", 'wb+') as destination:
                    for chunk in avatar.chunks():
                        destination.write(chunk)

            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserForm(instance=request.user)

    return render(request, 'classroom/profile_edit.html', {'form': form, 'user': request.user})

@login_required
@require_http_methods(["POST"])
def upload_avatar(request):
    """Handle avatar upload via AJAX"""
    try:
        if 'avatar' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No file provided'})

        avatar = request.FILES['avatar']

        if not avatar.content_type.startswith('image/'):
            return JsonResponse({'success': False, 'error': 'File must be an image'})

        if avatar.size > 5 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': 'File size must be < 5MB'})

        # Save avatar file manually
        path = f"media/avatars/{avatar.name}"
        with open(path, 'wb+') as f:
            for chunk in avatar.chunks():
                f.write(chunk)

        # Save avatar URL to user
        request.user.avatar_url = f"/media/avatars/{avatar.name}"
        request.user.save()

        return JsonResponse({
            'success': True,
            'avatar_url': request.user.avatar_url,
            'message': 'Avatar updated successfully!'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def remove_avatar(request):
    """Remove user avatar"""
    try:
        if request.user.avatar_url:
            # Optional: delete actual file from storage
            import os
            avatar_path = request.user.avatar_url.replace("/media/", "media/")
            if os.path.exists(avatar_path):
                os.remove(avatar_path)

            request.user.avatar_url = None
            request.user.save()

        return JsonResponse({
            'success': True,
            'message': 'Avatar removed successfully!'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# @login_required
# def settings_view(request):
#     """Display user settings page"""
#     try:
#         settings = request.user.usersettings
#     except UserSettings.DoesNotExist:
#         settings = UserSettings.objects.create(user=request.user)
    
#     context = {
#         'user': request.user,
#         'settings': settings,
#         'user_type': getattr(request.user, 'user_type', 'student'),
#     }
    
#     return render(request, 'classroom/settings.html', context)

# @login_required
# def settings_update(request):
#     """Update user settings"""
#     try:
#         settings = request.user.usersettings
#     except UserSettings.DoesNotExist:
#         settings = UserSettings.objects.create(user=request.user)
    
#     if request.method == 'POST':
#         form = UserSettingsForm(request.POST, instance=settings)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Settings updated successfully!')
#             return redirect('settings')
#         else:
#             messages.error(request, 'Please correct the errors below.')
#     else:
#         form = UserSettingsForm(instance=settings)
    
#     context = {
#         'form': form,
#         'user': request.user,
#         'settings': settings,
#     }
    
#     return render(request, 'classroom/settings_edit.html', context)

@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('settings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'user': request.user,
    }
    
    return render(request, 'classroom/change_password.html', context)

@login_required
@require_http_methods(["POST"])
def delete_account(request):
    """Delete user account"""
    if request.method == 'POST':
        password = request.POST.get('password')
        if request.user.check_password(password):
            request.user.delete()
            messages.success(request, 'Account deleted successfully.')
            return redirect('login')
        else:
            messages.error(request, 'Incorrect password.')
            return redirect('settings')
    
    return redirect('settings')