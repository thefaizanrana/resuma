from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Application, CandidateProfile, CompanyProfile, User, JobPosting


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'phone_number',
        'is_employer', 'is_candidate', 'is_staff',
    )
    list_filter = ('is_employer', 'is_candidate', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'ntn_number', 'is_verified')
    list_filter = ('is_verified',)
    search_fields = ('company_name', 'ntn_number', 'user__username', 'user__email')


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'cnic_number', 'city', 'resume_pdf')
    list_filter = ('city',)
    search_fields = ('user__username', 'user__email', 'cnic_number', 'raw_skills_text')


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'company', 'city', 'job_type',
        'salary_min_pkr', 'salary_max_pkr', 'is_active', 'created_at',
    )
    list_filter = ('is_active', 'job_type', 'city', 'created_at')
    search_fields = ('title', 'description', 'company__company_name')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job', 'match_score', 'applied_at')
    list_filter = ('match_score', 'applied_at')
    search_fields = ('candidate__user__username', 'candidate__user__email', 'job__title')
