from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('setup_profile/', views.setup_profile, name='setup_profile'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('submit_vitals/', views.submit_vitals, name='submit_vitals'),
    path('send_otp/', views.send_otp_email_view, name='send_otp'),
]
