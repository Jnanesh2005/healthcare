from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import CombinedLoginForm, OTPForm, HealthRecordForm, ProfileForm, UserRegistrationForm
from .models import OTP, HealthRecord, Profile, Vitals

import smtplib
import ssl
import certifi
import random
import json
from email.mime.text import MIMEText

def send_otp_email(email, code):
    subject = "Your OTP Code"
    body = f"Your OTP code is: {code}"
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "medteknie@gmail.com"
    msg["To"] = email

    context = ssl.create_default_context(cafile=certifi.where())
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login("medteknie@gmail.com", "cxeq iawg ovsi whlv")  # Your Gmail app password
        server.send_message(msg)

@csrf_exempt
def send_otp_email_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            print(f"Email: {email}, Password: {password}")  # Debug

            user = User.objects.get(email=email)
            if user.check_password(password):
                code = str(random.randint(100000, 999999))
                OTP.objects.create(email=email, code=code)
                send_otp_email(email, code)
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "message": "Invalid password."})
        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "Email not registered."})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error: {str(e)}"})

    return JsonResponse({"success": False, "message": "Invalid request."})


def logout_view(request):
    logout(request)
    return redirect('home')

def home(request):
    vitals = None
    if request.user.is_authenticated:
        vitals = HealthRecord.objects.filter(user=request.user).order_by('-recorded_at')
    return render(request, 'tracker/home.html', {'vitals': vitals})

@login_required
def dashboard(request):
    profile = request.user.profile
    return render(request, 'tracker/dashboard.html', {'profile': profile})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('setup_profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'tracker/register.html', {'form': form})

@login_required
def setup_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('home')
    else:
        form = ProfileForm()
    return render(request, 'tracker/setup_profile.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CombinedLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            otp_input = form.cleaned_data['otp']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "Invalid email or password.")
                return redirect('login')

            otp = OTP.objects.filter(email=email, code=otp_input).order_by('-created_at').first()

            if otp and not otp.is_expired():
                if user.check_password(password):
                    login(request, user)
                    if not hasattr(user, 'profile'):
                        return redirect('setup_profile')
                    return redirect('home')
                else:
                    messages.error(request, "Invalid password.")
            else:
                messages.error(request, "Invalid or expired OTP.")
    else:
        form = CombinedLoginForm()

    return render(request, 'tracker/login.html', {'form': form})

@login_required
def student_dashboard(request):
    status = None
    if request.method == 'POST':
        form = HealthRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.save()
            hr = record.heart_rate
            spo2 = record.spo2
            temp = record.temperature
            breath = record.breaths_per_minute
            if spo2 < 95 or hr > 100 or temp > 37.5 or breath > 20:
                status = "⚠️ Abnormal vitals — Please consult a doctor."
            else:
                status = "✅ Vitals normal."
    else:
        form = HealthRecordForm()
    return render(request, 'tracker/student_dashboard.html', {'form': form, 'status': status})

@login_required
def submit_vitals(request):
    if request.method == 'POST':
        form = HealthRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.save()
            vitals = Vitals.objects.create(
                profile=request.user.profile,
                temperature=record.temperature,
                heart_rate=record.heart_rate,
                spo2=record.spo2,
                breaths_per_minute=record.breaths_per_minute
            )
            status = vitals.health_status()
            return render(request, 'tracker/health_result.html', {'status': status, 'record': record})
    else:
        form = HealthRecordForm()
    return render(request, 'tracker/submit_vitals.html', {'form': form})
