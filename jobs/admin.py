from django.contrib import admin
from .models import Company, JobPosting, Candidate, JobApplication, RecruiterProfile

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'website')
    search_fields = ('name', 'location')

@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company')
    list_filter = ('company',)
    search_fields = ('user__username', 'company__name')


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'job_type', 'experience_level', 'salary_range', 'is_active', 'created_at')
    list_filter = ('is_active', 'job_type', 'experience_level', 'company')
    search_fields = ('title', 'company__name', 'tags', 'description')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'portfolio_url')
    search_fields = ('full_name', 'email', 'skills')

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job_posting', 'status', 'applied_at', 'updated_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('candidate__full_name', 'candidate__email', 'job_posting__title')
    list_editable = ('status',)
    date_hierarchy = 'applied_at'

