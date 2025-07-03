from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .forms import UserProfileForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.safestring import mark_safe  # Add this import
import logging

logger = logging.getLogger(__name__)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if user exists and is inactive
        try:
            user_obj = User.objects.get(email=email)
            if not user_obj.is_active:
                # Use mark_safe to allow HTML in the message
                error_message = mark_safe(
                    'Your account is not yet verified. Please verify your email address by clicking the link sent to your Gmail inbox. '
                    'If you did not receive the email, <a href="{0}?email={1}">click here to resend verification</a>.'
                    .format(reverse('resend_verification'), email)
                )
                messages.error(request, error_message)
                return render(request, 'classroom/login.html')
        except User.DoesNotExist:
            pass  # Continue to normal authentication

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            if user.user_type == 'teacher':
                return redirect('teacher_dashboard')
            elif user.user_type == 'student':
                return redirect('student_dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'classroom/login.html')


def send_verification_email(request, user):
    """Send verification email to user"""
    try:
        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verification_url = request.build_absolute_uri(
            reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
        )
        subject = 'Verify your iClassroom account'
        html_message = render_to_string('classroom/emails/verification_email.html', {
            'user': user,
            'verification_url': verification_url,
            'site_name': current_site.name,
        })
        plain_message = strip_tags(html_message)
        logger.debug(f"Sending email to {user.email} with verification URL: {verification_url}")
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Verification email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}", exc_info=True)
        return False


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

        # Create inactive user
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
            is_active=False  # User must verify email first
        )
        
        # Send verification email
        if send_verification_email(request, user):
            messages.success(request, f"Registration successful! Please check your email ({email}) for a verification link.")
        else:
            messages.error(request, "Registration successful but failed to send verification email. Please contact support.")
        
        return redirect('registration_complete')
    
    return render(request, 'classroom/register.html')


def registration_complete(request):
    """Show registration complete page"""
    return render(request, 'classroom/registration_complete.html')


def verify_email(request, uidb64, token):
    """Verify email address"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            if not user.is_active:
                user.is_active = True
                user.save()
                messages.success(request, 'Email verified successfully! You can now log in.')
            else:
                messages.info(request, 'Email already verified.')
            return redirect('login')
        else:
            messages.error(request, 'Invalid verification link.')
            return redirect('resend_verification')
            
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'Invalid verification link.')
        return redirect('resend_verification')


def resend_verification(request):
    """Resend verification email"""
    email = request.GET.get('email', '')  # Prefill if present
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email, is_active=False)
            if send_verification_email(request, user):
                messages.success(request, f'Verification email resent to {email}')
            else:
                messages.error(request, 'Failed to send verification email. Please try again.')
        except User.DoesNotExist:
            messages.error(request, 'No inactive account found with this email address.')
        return redirect('resend_verification')
    return render(request, 'classroom/resend_verification.html', {'email': email})


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
        form = UserProfileForm(instance=request.user)

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

def forgot_password(request):
    """Handle forgot password functionality"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                messages.error(request, 'You must verify your email before you can reset your password.')
                return redirect('forgot_password')
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(
                reverse('reset_password', kwargs={'uidb64': uid, 'token': token})
            )
            subject = 'Reset your iClassroom password'
            html_message = render_to_string('classroom/emails/reset_password_email.html', {
                'user': user,
                'reset_url': reset_url,
                'site_name': current_site.name,
            })
            plain_message = strip_tags(html_message)
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            messages.success(request, f'Password reset link sent to {email}.')
        except User.DoesNotExist:
            messages.error(request, 'No account found with that email address.')
        return redirect('forgot_password')
    
    return render(request, 'classroom/forgot_password.html')

def reset_password(request, uidb64, token):
    """Reset user password"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if not user.is_active:
            messages.error(request, 'You must verify your email before you can reset your password.')
            return redirect('login')

        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')

                if new_password == confirm_password:
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'Password reset successfully! You can now log in.')
                    return redirect('login')
                else:
                    messages.error(request, 'Passwords do not match.')
            return render(request, 'classroom/reset_password.html', {'uidb64': uidb64, 'token': token})
        else:
            messages.error(request, 'Invalid password reset link.')
            return redirect('forgot_password')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'Invalid password reset link.')
        return redirect('forgot_password')