from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

PAKISTAN_CITIES = [
    ('Karachi', 'Karachi'),
    ('Lahore', 'Lahore'),
    ('Islamabad', 'Islamabad'),
    ('Rawalpindi', 'Rawalpindi'),
    ('Peshawar', 'Peshawar'),
    ('Faisalabad', 'Faisalabad'),
    ('Multan', 'Multan'),
    ('Quetta', 'Quetta'),
    ('Sialkot', 'Sialkot'),
    ('Remote', 'Remote Pakistan'),
]

WORKPLACE_CHOICES = [
    ('Onsite', 'Onsite'),
    ('Remote', 'Remote'),
    ('Hybrid', 'Hybrid'),
]

APPLICATION_STATUS_CHOICES = [
    ('Submitted', 'Submitted'),
    ('Review', 'In Review'),
    ('Shortlist', 'Shortlisted'),
    ('Interview', 'Interview'),
    ('Rejected', 'Rejected'),
]

phone_validator = RegexValidator(
    regex=r'^\+92[0-9]{10}$',
    message="Phone number must be entered in the format: '+92XXXXXXXXXX'.",
)

cnic_validator = RegexValidator(
    regex=r'^\d{5}-\d{7}-\d$',
    message='CNIC must be in the format XXXXX-XXXXXXX-X.',
)


class User(AbstractUser):
    USER_TYPE_EMPLOYER = 'employer'
    USER_TYPE_CANDIDATE = 'candidate'

    is_employer = models.BooleanField(default=False)
    is_candidate = models.BooleanField(default=False)
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[phone_validator],
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


class SubscriptionTier(models.Model):
    name = models.CharField(max_length=50, unique=True)
    price_pkr = models.PositiveIntegerField(default=0, verbose_name='Price (PKR)')
    max_jobs = models.PositiveIntegerField(default=5, verbose_name='Max Active Jobs')
    has_featured_badge = models.BooleanField(default=False, verbose_name='Featured Badge')
    has_cpp_matching_priority = models.BooleanField(
        default=False,
        verbose_name='C++ Matching Priority',
    )

    class Meta:
        verbose_name = 'Subscription Tier'
        verbose_name_plural = 'Subscription Tiers'

    def __str__(self):
        return self.name


class CompanyProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='company_profile',
    )
    company_name = models.CharField(max_length=255, db_index=True)
    ntn_number = models.CharField(max_length=20, blank=True, verbose_name='NTN Number')
    website = models.URLField(blank=True, verbose_name='Website URL')
    description = models.TextField(verbose_name='Company Description')
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    tier = models.ForeignKey(
        SubscriptionTier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='companies',
        verbose_name='Subscription Tier',
    )
    is_verified = models.BooleanField(default=False, db_index=True)
    is_premium = models.BooleanField(default=False, verbose_name='Premium (Gold Badge)')

    class Meta:
        verbose_name = 'Company Profile'
        verbose_name_plural = 'Company Profiles'

    def __str__(self):
        return self.company_name


class CandidateProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='candidate_profile',
    )
    cnic_number = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True,
        validators=[cnic_validator],
        verbose_name='CNIC Number',
    )
    city = models.CharField(
        max_length=50,
        choices=PAKISTAN_CITIES,
        default='Lahore',
        db_index=True,
    )
    title = models.CharField(max_length=150, blank=True, verbose_name='Professional Title')
    raw_skills_text = models.TextField(blank=True, verbose_name='Skills')
    resume_pdf = models.FileField(
        upload_to='resumes/',
        null=True,
        verbose_name='Resume (PDF)',
    )
    is_featured = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Candidate Profile'
        verbose_name_plural = 'Candidate Profiles'

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class JobPosting(models.Model):
    company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name='jobs',
    )
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    requirements = models.TextField(blank=True, verbose_name='Key Requirements')
    city = models.CharField(max_length=50, choices=PAKISTAN_CITIES, db_index=True)
    workplace_type = models.CharField(
        max_length=10,
        choices=WORKPLACE_CHOICES,
        default='Onsite',
        verbose_name='Workplace Type',
    )
    salary_min_pkr = models.PositiveIntegerField(default=0, verbose_name='Minimum Salary (PKR)')
    salary_max_pkr = models.PositiveIntegerField(default=0, verbose_name='Maximum Salary (PKR)')
    is_featured = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Job Posting'
        verbose_name_plural = 'Job Postings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', '-created_at'], name='job_active_created_idx'),
        ]

    def __str__(self):
        return self.title


class SavedJob(models.Model):
    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name='saved_jobs',
    )
    job = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE,
        related_name='saved_by',
    )
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Saved Job'
        verbose_name_plural = 'Saved Jobs'
        unique_together = ('candidate', 'job')
        ordering = ['-saved_at']

    def __str__(self):
        return f'{self.candidate} saved {self.job.title}'


class Application(models.Model):
    STATUS_SUBMITTED = 'Submitted'
    STATUS_REVIEW = 'Review'
    STATUS_SHORTLIST = 'Shortlist'
    STATUS_INTERVIEW = 'Interview'
    STATUS_REJECTED = 'Rejected'

    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name='applications',
    )
    job = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE,
        related_name='applications',
    )
    status = models.CharField(
        max_length=20,
        choices=APPLICATION_STATUS_CHOICES,
        default=STATUS_SUBMITTED,
        db_index=True,
    )
    match_score = models.PositiveIntegerField(default=0)
    applied_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
        unique_together = ('candidate', 'job')
        indexes = [
            models.Index(fields=['-match_score'], name='app_match_score_idx'),
        ]

    def __str__(self):
        return f'{self.candidate} -> {self.job.title} ({self.match_score}%)'
