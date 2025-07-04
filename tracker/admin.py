from django.contrib import admin
from .models import Profile, Vitals, HealthRecord

admin.site.register(Vitals)
admin.site.register(Profile)
admin.site.register(HealthRecord)
