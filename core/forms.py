from io import BytesIO

from PIL import Image
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import (
    PAKISTAN_CITIES,
    CandidateProfile,
    CompanyProfile,
    User,
    JobPosting,
)

INPUT_CLASSES = (
    'w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 '
    'shadow-sm placeholder:text-gray-400 '
    'focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition'
)
SELECT_CLASSES = INPUT_CLASSES + ' bg-white'


class UserRegistrationForm(UserCreationForm):
    USER_TYPE_CHOICES = [
        (User.USER_TYPE_CANDIDATE, 'Candidate — I am looking for a job'),
        (User.USER_TYPE_EMPLOYER, 'Employer — I am hiring talent'),
    ]

    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': SELECT_CLASSES}),
    )
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': INPUT_CLASSES}))
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(
            attrs={'class': INPUT_CLASSES, 'placeholder': '+92XXXXXXXXXX'}
        ),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'autofocus': True,
        })
        self.fields['password1'].widget.attrs.update({'class': INPUT_CLASSES})
        self.fields['password2'].widget.attrs.update({'class': INPUT_CLASSES})

    def save(self, commit=True):
        user = super().save(commit=False)
        selected_type = self.cleaned_data['user_type']
        user.is_employer = selected_type == User.USER_TYPE_EMPLOYER
        user.is_candidate = selected_type == User.USER_TYPE_CANDIDATE
        if commit:
            user.save()
        return user


class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = CandidateProfile
        fields = ['cnic_number', 'city', 'raw_skills_text', 'resume_pdf']
        widgets = {
            'cnic_number': forms.TextInput(
                attrs={'class': INPUT_CLASSES, 'placeholder': 'XXXXX-XXXXXXX-X'}
            ),
            'city': forms.Select(choices=PAKISTAN_CITIES, attrs={'class': SELECT_CLASSES}),
            'raw_skills_text': forms.Textarea(
                attrs={
                    'class': INPUT_CLASSES,
                    'rows': 4,
                    'placeholder': 'e.g. Python, Django, PostgreSQL, React, Tailwind CSS',
                }
            ),
            'resume_pdf': forms.FileInput(
                attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 '
                               'file:px-4 file:rounded-lg file:border-0 file:text-sm '
                               'file:font-semibold file:bg-indigo-50 file:text-indigo-600 '
                               'hover:file:bg-indigo-100'}
            ),
        }

    def clean_resume_pdf(self):
        resume = self.cleaned_data.get('resume_pdf')
        if resume:
            if not resume.name.lower().endswith('.pdf'):
                raise forms.ValidationError('Resume must strictly be a PDF file.')
        return resume


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ['company_name', 'description', 'logo']
        widgets = {
            'company_name': forms.TextInput(
                attrs={'class': INPUT_CLASSES, 'placeholder': 'Acme Corporation'}
            ),
            'description': forms.Textarea(
                attrs={
                    'class': INPUT_CLASSES,
                    'rows': 4,
                    'placeholder': 'Tell candidates what your company does...',
                }
            ),
            'logo': forms.FileInput(
                attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 '
                               'file:px-4 file:rounded-lg file:border-0 file:text-sm '
                               'file:font-semibold file:bg-indigo-50 file:text-indigo-600 '
                               'hover:file:bg-indigo-100'}
            ),
        }

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if not logo:
            return logo
        try:
            image = Image.open(BytesIO(logo.read()))
            image.verify()
        except Exception as exc:
            raise forms.ValidationError('Logo must be a valid image file.') from exc
        return logo


class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        exclude = ['company', 'is_active', 'created_at']
        widgets = {
            'title': forms.TextInput(
                attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g. Senior Django Developer'}
            ),
            'description': forms.Textarea(
                attrs={
                    'class': INPUT_CLASSES,
                    'rows': 6,
                    'placeholder': 'Describe the role, responsibilities and requirements...',
                }
            ),
            'city': forms.Select(choices=PAKISTAN_CITIES, attrs={'class': SELECT_CLASSES}),
            'salary_min_pkr': forms.NumberInput(
                attrs={'class': INPUT_CLASSES, 'placeholder': '100000'}
            ),
            'salary_max_pkr': forms.NumberInput(
                attrs={'class': INPUT_CLASSES, 'placeholder': '250000'}
            ),
            'job_type': forms.Select(
                attrs={'class': SELECT_CLASSES},
                choices=[
                    ('Remote', 'Remote'),
                    ('Onsite', 'Onsite'),
                    ('Hybrid', 'Hybrid'),
                ],
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min_pkr')
        salary_max = cleaned_data.get('salary_max_pkr')
        if salary_min is not None and salary_max is not None and salary_max < salary_min:
            self.add_error(
                'salary_max_pkr',
                'Maximum salary must be greater than or equal to minimum salary.',
            )
        return cleaned_data
