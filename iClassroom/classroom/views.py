from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
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
