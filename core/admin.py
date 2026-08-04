from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Application,
    CandidateProfile,
    CompanyProfile,
    JobPosting,
    SavedJob,
    SubscriptionTier,
    User,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'phone_number',
        'is_employer', 'is_candidate', 'is_staff',
    )
    list_filter = ('is_employer', 'is_candidate', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')


@admin.register(SubscriptionTier)
class SubscriptionTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_pkr', 'max_jobs', 'has_featured_badge', 'has_cpp_matching_priority')
    list_filter = ('has_featured_badge', 'has_cpp_matching_priority')
    search_fields = ('name',)


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = (
        'company_name', 'user', 'ntn_number', 'tier',
        'is_verified', 'is_premium',
    )
    list_filter = ('is_verified', 'is_premium', 'tier')
    search_fields = ('company_name', 'ntn_number', 'website', 'user__username', 'user__email')


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'city', 'cnic_number', 'is_featured', 'resume_pdf')
    list_filter = ('city', 'is_featured')
    search_fields = ('user__username', 'user__email', 'cnic_number', 'title', 'raw_skills_text')


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'company', 'city', 'workplace_type',
        'salary_min_pkr', 'salary_max_pkr', 'is_featured', 'is_active', 'created_at',
    )
    list_filter = ('is_active', 'is_featured', 'workplace_type', 'city', 'created_at')
    search_fields = ('title', 'description', 'requirements', 'company__company_name')


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job', 'saved_at')
    search_fields = ('candidate__user__username', 'job__title')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job', 'status', 'match_score', 'applied_at')
    list_filter = ('status', 'match_score', 'applied_at')
    search_fields = ('candidate__user__username', 'candidate__user__email', 'job__title')
