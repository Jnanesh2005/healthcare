from django import forms
from django.contrib.auth.models import User
from .models import HealthRecord, Profile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user']

class HealthRecordForm(forms.ModelForm):
    class Meta:
        model = HealthRecord
        fields = ['heart_rate', 'spo2', 'temperature', 'breaths_per_minute']

class OTPForm(forms.Form):
    otp = forms.CharField(label="Enter the OTP", max_length=6)

class CombinedLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    otp = forms.CharField(max_length=6, label="OTP Code")
