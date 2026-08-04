from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_feed_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('setup/', views.profile_setup_view, name='profile_setup'),
    path('employer/create-job/', views.create_job_view, name='create_job'),
    path('employer/ats/', views.employer_ats_view, name='ats'),
    path('candidate/feed/', views.job_feed_view, name='job_feed'),
    path('candidate/dashboard/', views.candidate_dashboard_view, name='candidate_dashboard'),
    path('job/<int:pk>/', views.job_detail_view, name='job_detail'),
    path('job/<int:pk>/apply/', views.apply_job_view, name='apply'),
    path('employer/application/<int:pk>/status/', views.application_status_view, name='application_status'),
]
