import job_matcher

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CandidateProfileForm, CompanyProfileForm, JobPostingForm, UserRegistrationForm
from .models import (
    PAKISTAN_CITIES,
    Application,
    CandidateProfile,
    CompanyProfile,
    JobPosting,
)
from .templatetags.currency_tags import pkr_compact


def _serialize_jobs(jobs):
    return [
        {
            'id': job.pk,
            'title': job.title,
            'company': job.company.company_name,
            'city': job.city,
            'job_type': job.job_type,
            'salary_min': job.salary_min_pkr,
            'salary_max': job.salary_max_pkr,
            'salary_display': (
                f'PKR {pkr_compact(job.salary_min_pkr)} - {pkr_compact(job.salary_max_pkr)}'
                if job.salary_max_pkr else 'Salary not disclosed'
            ),
            'description': job.description,
            'verified': job.company.is_verified,
            'created': job.created_at.strftime('%b %d, %Y'),
        }
        for job in jobs
    ]


def home_feed_view(request):
    query = request.GET.get('q', '').strip()
    city = request.GET.get('city', '')

    jobs = (
        JobPosting.objects.filter(is_active=True)
        .select_related('company')
        .order_by('-created_at')
    )
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(company__company_name__icontains=query)
        )
    if city:
        jobs = jobs.filter(city=city)

    return render(request, 'home.html', {
        'jobs': jobs,
        'jobs_data': _serialize_jobs(jobs),
        'query': query,
        'city': city,
        'cities': PAKISTAN_CITIES,
    })


def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Complete your profile to get started.')
            return redirect('core:profile_setup')
    else:
        form = UserRegistrationForm()

    return render(request, 'auth/register.html', {'form': form})


@login_required
def profile_setup_view(request):
    if request.user.is_employer:
        profile, _ = CompanyProfile.objects.get_or_create(user=request.user)
        form_class = CompanyProfileForm
    elif request.user.is_candidate:
        profile, _ = CandidateProfile.objects.get_or_create(user=request.user)
        form_class = CandidateProfileForm
    else:
        messages.error(request, 'Please select a user type to complete your profile.')
        return redirect('core:home')

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been saved.')
            if request.user.is_employer:
                return redirect('core:create_job')
            return redirect('core:job_feed')
    else:
        form = form_class(instance=profile)

    return render(request, 'profiles/setup.html', {
        'form': form,
        'is_employer': request.user.is_employer,
    })


@login_required
def create_job_view(request):
    if not request.user.is_employer:
        messages.error(request, 'Only employer accounts can post jobs.')
        return redirect('core:home')

    company = getattr(request.user, 'company_profile', None)
    if company is None:
        messages.error(request, 'Please set up your company profile first.')
        return redirect('core:profile_setup')

    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = company
            job.is_active = True
            job.save()
            messages.success(request, f'"{job.title}" has been posted successfully.')
            return redirect('core:ats')
    else:
        form = JobPostingForm()

    return render(request, 'employer/create_job.html', {'form': form, 'company': company})


@login_required
def job_feed_view(request):
    if not request.user.is_candidate:
        messages.error(request, 'Only candidate accounts can access the job feed.')
        return redirect('core:home')

    candidate = get_object_or_404(CandidateProfile, user=request.user)

    jobs = (
        JobPosting.objects.filter(is_active=True)
        .select_related('company')
        .order_by('-created_at')
    )

    scored_jobs = []
    for job in jobs:
        score = job_matcher.calculate_match(candidate.raw_skills_text, job.description)
        scored_jobs.append({'job': job, 'score': score})

    scored_jobs.sort(key=lambda item: item['score'], reverse=True)

    return render(request, 'candidate/feed.html', {
        'scored_jobs': scored_jobs,
        'candidate': candidate,
    })


@login_required
def candidate_dashboard_view(request):
    if not request.user.is_candidate:
        messages.error(request, 'Only candidate accounts can access the dashboard.')
        return redirect('core:home')

    candidate = get_object_or_404(CandidateProfile, user=request.user)
    applications = (
        Application.objects.filter(candidate=candidate)
        .select_related('job__company')
        .order_by('-match_score', '-applied_at')
    )

    return render(request, 'candidate/dashboard.html', {
        'candidate': candidate,
        'applications': applications,
    })


@login_required
@require_POST
def apply_job_view(request, pk):
    if not request.user.is_candidate:
        messages.error(request, 'Only candidate accounts can apply for jobs.')
        return redirect('core:home')

    job = get_object_or_404(
        JobPosting.objects.select_related('company'),
        pk=pk,
        is_active=True,
    )
    candidate = get_object_or_404(CandidateProfile, user=request.user)

    score = job_matcher.calculate_match(candidate.raw_skills_text, job.description)

    application, created = Application.objects.get_or_create(
        candidate=candidate,
        job=job,
        defaults={'match_score': score},
    )
    if not created:
        application.match_score = score
        application.save(update_fields=['match_score'])
        messages.info(request, f'You had already applied. Match score refreshed to {score}%.')
    else:
        messages.success(request, f'Application submitted! Match score: {score}%.')

    return redirect('core:job_feed')


@login_required
def employer_ats_view(request):
    if not request.user.is_employer:
        messages.error(request, 'Only employer accounts can access the ATS.')
        return redirect('core:home')

    company = getattr(request.user, 'company_profile', None)
    if company is None:
        messages.error(request, 'Please set up your company profile first.')
        return redirect('core:profile_setup')

    jobs = JobPosting.objects.filter(company=company).prefetch_related(
        Prefetch(
            'applications',
            queryset=Application.objects.select_related('candidate__user').order_by('-match_score'),
        )
    ).order_by('-created_at')

    applications = []
    for job in jobs:
        applications.extend(job.applications.all())

    high_match = [a for a in applications if a.match_score >= 80]
    medium_match = [a for a in applications if 50 <= a.match_score < 80]
    low_match = [a for a in applications if a.match_score < 50]

    return render(request, 'employer/kanban.html', {
        'company': company,
        'jobs': jobs,
        'high_match': high_match,
        'medium_match': medium_match,
        'low_match': low_match,
    })


def job_detail_view(request, pk):
    job = get_object_or_404(
        JobPosting.objects.select_related('company'),
        pk=pk,
        is_active=True,
    )
    return render(request, 'job_detail.html', {'job': job})
