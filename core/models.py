from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

PAKISTAN_CITIES = [
    ('Karachi', 'Karachi'),
    ('Lahore', 'Lahore'),
    ('Islamabad', 'Islamabad'),
    ('Rawalpindi', 'Rawalpindi'),
    ('Faisalabad', 'Faisalabad'),
    ('Multan', 'Multan'),
    ('Hyderabad', 'Hyderabad'),
    ('Peshawar', 'Peshawar'),
    ('Quetta', 'Quetta'),
    ('Sialkot', 'Sialkot'),
    ('Gujranwala', 'Gujranwala'),
    ('Other', 'Other'),
]

JOB_TYPES = [
    ('Remote', 'Remote'),
    ('Onsite', 'Onsite'),
    ('Hybrid', 'Hybrid'),
]

phone_validator = RegexValidator(
    regex=r'^\+92\d{10}$',
    message='Phone number must be in the format +92XXXXXXXXXX.',
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
        validators=[phone_validator],
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


class CompanyProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='company_profile',
    )
    company_name = models.CharField(max_length=255, db_index=True)
    ntn_number = models.CharField(max_length=30, blank=True, verbose_name='NTN Number')
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    is_verified = models.BooleanField(default=False, db_index=True)

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
    city = models.CharField(max_length=50, choices=PAKISTAN_CITIES, blank=True, db_index=True)
    resume_pdf = models.FileField(upload_to='resumes/', blank=True, null=True, verbose_name='Resume (PDF)')
    raw_skills_text = models.TextField(blank=True, verbose_name='Skills')

    class Meta:
        verbose_name = 'Candidate Profile'
        verbose_name_plural = 'Candidate Profiles'

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class JobPosting(models.Model):
    company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name='job_postings',
    )
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    city = models.CharField(max_length=50, choices=PAKISTAN_CITIES, blank=True, db_index=True)
    salary_min_pkr = models.PositiveIntegerField(default=0, verbose_name='Minimum Salary (PKR)')
    salary_max_pkr = models.PositiveIntegerField(default=0, verbose_name='Maximum Salary (PKR)')
    job_type = models.CharField(max_length=10, choices=JOB_TYPES, default='Onsite')
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


class Application(models.Model):
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
