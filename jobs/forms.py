import re
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Candidate, JobApplication, JobPosting, Company, RecruiterProfile

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['full_name', 'email', 'phone', 'resume_url', 'portfolio_url', 'skills', 'bio']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Jane Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'jane.doe@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 019-2834'}),
            'resume_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://drive.google.com/... (Optional)'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/janedoe (Optional)'}),
            'skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Python, Django, HTML, CSS'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description about yourself (Optional)...'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            raise ValidationError("Phone number is required.")
        
        # Verify it has at least 7 digits
        digits_only = re.sub(r'\D', '', phone)
        if len(digits_only) < 7:
            raise ValidationError("Please enter a valid phone number with at least 7 digits.")
        
        # Check allowed characters: digits, spaces, hyphens, plus, parenthesis
        if not re.match(r'^[\d\s\-\+\(\)]+$', phone):
            raise ValidationError("Phone number contains invalid characters. Use digits, spaces, -, +, and parentheses.")
        
        return phone

    def clean_skills(self):
        skills = self.cleaned_data.get('skills', '').strip()
        if not skills:
            raise ValidationError("Please provide at least one skill.")
        return skills

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Explain why you are a great fit for this position...'}),
        }
        
    def clean_cover_letter(self):
        cover_letter = self.cleaned_data.get('cover_letter', '').strip()
        if not cover_letter:
            raise ValidationError("Please write a short cover letter.")
        if len(cover_letter) < 20:
            raise ValidationError("Your cover letter must be at least 20 characters long.")
        return cover_letter

class CandidateSignupForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'janesmith'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'jane.smith@example.com'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
        label="Confirm Password"
    )
    
    # Candidate profile fields
    full_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Jane Smith'})
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 43210'})
    )
    skills = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Python, Django, HTML, CSS'}),
        help_text="Comma-separated skills"
    )
    resume_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://drive.google.com/... (Optional)'})
    )
    portfolio_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/... (Optional)'})
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description about yourself... (Optional)'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("A user with this username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email address already exists.")
        return email

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise ValidationError("Passwords do not match.")
        return password_confirm

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            raise ValidationError("Phone number is required.")
        digits_only = re.sub(r'\D', '', phone)
        if len(digits_only) < 7:
            raise ValidationError("Please enter a valid phone number with at least 7 digits.")
        if not re.match(r'^[\d\s\-\+\(\)]+$', phone):
            raise ValidationError("Phone number contains invalid characters.")
        return phone

    def clean_skills(self):
        skills = self.cleaned_data.get('skills', '').strip()
        if not skills:
            raise ValidationError("Please provide at least one skill.")
        return skills
        
    def save(self):
        cleaned_data = self.cleaned_data
        user = User.objects.create_user(
            username=cleaned_data['username'],
            email=cleaned_data['email'],
            password=cleaned_data['password']
        )
        Candidate.objects.create(
            user=user,
            full_name=cleaned_data['full_name'],
            email=cleaned_data['email'],
            phone=cleaned_data['phone'],
            skills=cleaned_data['skills'],
            resume_url=cleaned_data.get('resume_url'),
            portfolio_url=cleaned_data.get('portfolio_url'),
            bio=cleaned_data.get('bio', '')
        )
        return user


class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['title', 'description', 'requirements', 'location', 'job_type', 'experience_level', 'salary_range', 'tags', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Senior Backend Engineer'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe the role, responsibilities, and team...'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter requirements (one per line)...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bangalore, India or Remote'}),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'salary_range': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ₹12,00,000 - ₹18,00,000 or Competitive'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python, Django, PostgreSQL (comma separated)'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RecruiterSignupForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'recruiter_username'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'recruiter@company.com'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
        label="Confirm Password"
    )
    
    # Company Selection
    company_choice = forms.ChoiceField(
        choices=[],  # Will populate dynamically in __init__
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_company_choice'}),
        label="Select Company",
        required=True
    )
    
    # New Company Fields
    new_company_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Acme Corp'}),
        label="Company Name"
    )
    new_company_location = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. San Francisco, CA'}),
        label="Location"
    )
    new_company_website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://acme.com'}),
        label="Website URL"
    )
    new_company_logo_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://acme.com/logo.png'}),
        label="Logo Image URL"
    )
    new_company_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Acme Corp is a leading provider of...'}),
        label="Company Description"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically load companies
        companies = [(str(c.id), c.name) for c in Company.objects.all()]
        self.fields['company_choice'].choices = [
            ('', '-- Select an existing company --'),
            ('new', '-- Register a New Company --')
        ] + companies

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("A user with this username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email address already exists.")
        return email

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise ValidationError("Passwords do not match.")
        return password_confirm

    def clean(self):
        cleaned_data = super().clean()
        company_choice = cleaned_data.get('company_choice')
        
        # If registering a new company, name and location are required
        if company_choice == 'new':
            new_name = cleaned_data.get('new_company_name')
            new_location = cleaned_data.get('new_company_location')
            
            if not new_name:
                self.add_error('new_company_name', "This field is required for new companies.")
            if not new_location:
                self.add_error('new_company_location', "This field is required for new companies.")
                
        return cleaned_data

    def save(self):
        cleaned_data = self.cleaned_data
        company_choice = cleaned_data['company_choice']
        
        # 1. Resolve company
        if company_choice == 'new':
            company = Company.objects.create(
                name=cleaned_data['new_company_name'],
                location=cleaned_data['new_company_location'],
                website=cleaned_data.get('new_company_website', ''),
                logo_url=cleaned_data.get('new_company_logo_url', ''),
                description=cleaned_data.get('new_company_description', '')
            )
        else:
            company = Company.objects.get(id=int(company_choice))
            
        # 2. Create Django user with staff status
        user = User.objects.create_user(
            username=cleaned_data['username'],
            email=cleaned_data['email'],
            password=cleaned_data['password']
        )
        user.is_staff = True
        user.save()
        
        # 3. Create recruiter profile
        RecruiterProfile.objects.create(
            user=user,
            company=company
        )
        return user


