from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import CandidateProfile, CompanyProfile, JobPosting, User


class Command(BaseCommand):
    help = 'Seed the database with demo users, companies, and job postings.'

    @transaction.atomic
    def handle(self, *args, **options):
        admin, _ = User.objects.update_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        admin.set_password('admin12345')
        admin.save()
        self.stdout.write('Ensured superuser "admin" (password: admin12345).')

        employer, _ = User.objects.update_or_create(
            username='employer',
            defaults={
                'email': 'employer@example.com',
                'phone_number': '+923001234567',
                'is_employer': True,
            },
        )
        employer.set_password('employer12345')
        employer.save()
        company, _ = CompanyProfile.objects.update_or_create(
            user=employer,
            defaults={
                'company_name': 'Acme Corporation',
                'ntn_number': '1234567-8',
                'description': 'A leading Pakistani technology company building '
                               'world-class digital products.',
                'is_verified': True,
            },
        )
        self.stdout.write(f'Ensured employer "employer" at "{company.company_name}".')

        candidate, _ = User.objects.update_or_create(
            username='candidate',
            defaults={
                'email': 'candidate@example.com',
                'phone_number': '+923332345678',
                'is_candidate': True,
            },
        )
        candidate.set_password('candidate12345')
        candidate.save()
        profile, _ = CandidateProfile.objects.update_or_create(
            user=candidate,
            defaults={
                'cnic_number': '42101-1234567-1',
                'city': 'Karachi',
                'raw_skills_text': 'python django postgresql tailwind css react javascript sql',
            },
        )
        self.stdout.write(f'Ensured candidate "candidate" in {profile.city}.')

        jobs_data = [
            {
                'title': 'Senior Django Developer',
                'description': 'Build and scale Django services. Requirements: python, django, postgresql.',
                'city': 'Karachi',
                'salary_min_pkr': 350000,
                'salary_max_pkr': 500000,
                'job_type': 'Hybrid',
            },
            {
                'title': 'Frontend Engineer (React)',
                'description': 'Craft delightful interfaces with React and Tailwind CSS. Requirements: react, tailwind css, javascript.',
                'city': 'Lahore',
                'salary_min_pkr': 250000,
                'salary_max_pkr': 400000,
                'job_type': 'Remote',
            },
            {
                'title': 'DevOps Engineer',
                'description': 'Own CI/CD and cloud infrastructure. Requirements: docker, kubernetes, aws, linux.',
                'city': 'Islamabad',
                'salary_min_pkr': 300000,
                'salary_max_pkr': 450000,
                'job_type': 'Onsite',
            },
            {
                'title': 'Data Engineer',
                'description': 'Design data pipelines for analytics. Requirements: python, sql, airflow, spark.',
                'city': 'Rawalpindi',
                'salary_min_pkr': 200000,
                'salary_max_pkr': 350000,
                'job_type': 'Remote',
            },
        ]
        for data in jobs_data:
            job, _ = JobPosting.objects.update_or_create(
                company=company,
                title=data['title'],
                defaults=data,
            )
            self.stdout.write(f'Ensured job "{job.title}".')

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully.'))
