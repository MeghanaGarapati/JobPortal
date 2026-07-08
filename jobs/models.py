from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    name = models.CharField(max_length=255)
    logo_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL to company logo image")
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name

class JobPosting(models.Model):
    JOB_TYPES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Remote', 'Remote'),
        ('Internship', 'Internship'),
    ]
    
    EXP_LEVELS = [
        ('Entry Level', 'Entry Level'),
        ('Mid Level', 'Mid Level'),
        ('Senior Level', 'Senior Level'),
        ('Lead / Exec', 'Lead / Exec'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(help_text="Enter requirements, one per line or markdown formatted.")
    location = models.CharField(max_length=255)
    job_type = models.CharField(max_length=50, choices=JOB_TYPES, default='Full-time')
    experience_level = models.CharField(max_length=50, choices=EXP_LEVELS, default='Mid Level')
    salary_range = models.CharField(max_length=100, blank=True, help_text="e.g. ₹5,00,000 - ₹8,00,000 or Competitive")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags (e.g. Python, Django, React)")

    def get_tags_list(self):
        if self.tags:
            return [t.strip() for t in self.tags.split(',') if t.strip()]
        return []

    def get_requirements_list(self):
        if self.requirements:
            return [r.strip() for r in self.requirements.split('\n') if r.strip()]
        return []

    def __str__(self):
        return f"{self.title} at {self.company.name}"

class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile', null=True, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    resume_url = models.URLField(max_length=500, blank=True, null=True, help_text="Link to resume (Google Drive, Dropbox, etc.)")
    portfolio_url = models.URLField(max_length=500, blank=True, null=True)
    skills = models.CharField(max_length=255, help_text="Comma-separated skills (e.g. HTML, CSS, Django, Python)")
    bio = models.TextField(blank=True)

    def get_skills_list(self):
        if self.skills:
            return [s.strip() for s in self.skills.split(',') if s.strip()]
        return []

    def __str__(self):
        return self.full_name

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('Applied', 'Applied'),
        ('Under Review', 'Under Review'),
        ('Shortlisted', 'Shortlisted'),
        ('Rejected', 'Rejected'),
    ]

    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Applied')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_at']
        unique_together = ('job_posting', 'candidate')

    def __str__(self):
        return f"{self.candidate.full_name} - {self.job_posting.title} ({self.status})"


class RecruiterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recruiter_profile')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='recruiters')

    def __str__(self):
        return f"{self.user.username} ({self.company.name})"

