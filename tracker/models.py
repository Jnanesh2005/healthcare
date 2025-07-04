from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    school_name = models.CharField(max_length=100)
    sex = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    height = models.FloatField(help_text="in cm")
    weight = models.FloatField(help_text="in kg")
    diseases_to_monitor = models.TextField(blank=True)
    contact = models.CharField(max_length=15)

    def __str__(self):
        return self.full_name

class OTP(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

    def __str__(self):
        return f"{self.email} - {self.code}"

class HealthRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    heart_rate = models.IntegerField()
    spo2 = models.IntegerField()
    temperature = models.FloatField(help_text="in °C")
    breaths_per_minute = models.IntegerField(default=16)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"

class Vitals(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    temperature = models.FloatField(help_text="in °C")
    heart_rate = models.IntegerField()
    spo2 = models.IntegerField()
    breaths_per_minute = models.IntegerField(default=16)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def health_status(self):
        if self.temperature > 38 or self.spo2 < 95 or self.heart_rate > 100 or self.breaths_per_minute > 24:
            return "Needs Attention"
        elif (
            36.5 <= self.temperature <= 37.5 and
            95 <= self.spo2 <= 100 and
            60 <= self.heart_rate <= 100 and
            12 <= self.breaths_per_minute <= 20
        ):
            return "Normal"
        else:
            return "Watch"

    def __str__(self):
        return f"{self.profile.full_name if self.profile else 'No Profile'} - {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"
