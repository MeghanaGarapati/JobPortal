from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.db import IntegrityError
from django.urls import reverse_lazy
from .models import Company, JobPosting, Candidate, JobApplication, RecruiterProfile
from .forms import CandidateForm, JobApplicationForm, CandidateSignupForm, JobPostingForm, RecruiterSignupForm

class RecruiterRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Access denied. Only recruiters can view the recruiter dashboard.")
            return redirect('job_list')
        return super().dispatch(request, *args, **kwargs)

class JobListView(ListView):
    model = JobPosting
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    
    def get_queryset(self):
        return JobPosting.objects.filter(is_active=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['candidate_form'] = CandidateForm()
        context['application_form'] = JobApplicationForm()
        # Get list of unique categories or tags for filtering
        tags = set()
        for job in self.get_queryset():
            tags.update(job.get_tags_list())
        context['all_tags'] = sorted(list(tags))
        return context

class JobDetailView(DetailView):
    model = JobPosting
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['candidate_form'] = CandidateForm()
        context['application_form'] = JobApplicationForm()
        return context

class ApplyToJobView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if request.user.is_staff or request.user.is_superuser:
            return JsonResponse({
                'success': False,
                'errors': {'__all__': ['Recruiters cannot apply for jobs.']}
            }, status=400)
            
        job = get_object_or_404(JobPosting, pk=pk)
        
        # Ensure candidate profile exists
        candidate = getattr(request.user, 'candidate_profile', None)
        if not candidate:
            return JsonResponse({
                'success': False,
                'errors': {'__all__': ['Please complete your candidate profile before applying.']}
            }, status=400)
            
        application_form = JobApplicationForm(request.POST)
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        if application_form.is_valid():
            try:
                # Create the job application link
                application = JobApplication.objects.create(
                    job_posting=job,
                    candidate=candidate,
                    cover_letter=application_form.cleaned_data.get('cover_letter')
                )
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Your application was submitted successfully!'
                    })
                
                messages.success(request, 'Your application was submitted successfully!')
                return redirect('job_detail', pk=job.pk)
                
            except IntegrityError:
                message = 'You have already applied for this position.'
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'errors': {'cover_letter': [message]}
                    }, status=400)
                
                messages.error(request, message)
                return redirect('job_detail', pk=job.pk)
        else:
            errors = {field: [str(e) for e in err_list] for field, err_list in application_form.errors.items()}
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': errors
                }, status=400)
            
            for field, err_list in errors.items():
                for err in err_list:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {err}")
            return redirect('job_detail', pk=job.pk)

class RecruiterDashboardView(RecruiterRequiredMixin, ListView):
    model = JobApplication
    template_name = 'jobs/recruiter_dashboard.html'
    context_object_name = 'applications'
    
    def get_company(self):
        profile = getattr(self.request.user, 'recruiter_profile', None)
        if not profile:
            company = Company.objects.first()
            if not company:
                company = Company.objects.create(name="ApexLabs", location="Remote", description="Default company")
            profile = RecruiterProfile.objects.create(user=self.request.user, company=company)
        return profile.company
        
    def get_queryset(self):
        company = self.get_company()
        return JobApplication.objects.filter(job_posting__company=company).select_related('candidate', 'job_posting')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        apps = self.get_queryset()
        company = self.get_company()
        
        # Kanban categories mapping
        context['applied_apps'] = apps.filter(status='Applied')
        context['review_apps'] = apps.filter(status='Under Review')
        context['shortlisted_apps'] = apps.filter(status='Shortlisted')
        context['rejected_apps'] = apps.filter(status='Rejected')
        
        # Operational analytics
        context['total_applications'] = apps.count()
        context['active_jobs_count'] = JobPosting.objects.filter(company=company, is_active=True).count()
        context['shortlisted_count'] = context['shortlisted_apps'].count()
        context['rejected_count'] = context['rejected_apps'].count()
        context['company'] = company
        
        return context


class JobCreateView(RecruiterRequiredMixin, CreateView):
    model = JobPosting
    form_class = JobPostingForm
    template_name = 'jobs/job_create.html'
    success_url = reverse_lazy('recruiter_dashboard')
    
    def get_company(self):
        profile = getattr(self.request.user, 'recruiter_profile', None)
        if not profile:
            company = Company.objects.first()
            if not company:
                company = Company.objects.create(name="ApexLabs", location="Remote", description="Default company")
            profile = RecruiterProfile.objects.create(user=self.request.user, company=company)
        return profile.company

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.get_company()
        return context

    def form_valid(self, form):
        form.instance.company = self.get_company()
        messages.success(self.request, f"Job '{form.instance.title}' posted successfully!")
        return super().form_valid(form)

class UpdateApplicationStatusView(RecruiterRequiredMixin, View):
    def post(self, request, pk):
        application = get_object_or_404(JobApplication, pk=pk)
        new_status = request.POST.get('status')
        
        valid_statuses = [choice[0] for choice in JobApplication.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
            
        application.status = new_status
        application.save()
        
        return JsonResponse({
            'success': True,
            'message': f"Application updated to '{new_status}'.",
            'application_id': application.id,
            'status': application.status
        })

class RecruiterLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                return redirect('recruiter_dashboard')
            else:
                logout(request)
        form = AuthenticationForm()
        return render(request, 'jobs/login.html', {'form': form})
        
    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_staff or user.is_superuser:
                    login(request, user)
                    messages.success(request, f"Logged in as recruiter {username}.")
                    return redirect('recruiter_dashboard')
                else:
                    messages.error(request, "Access denied. Candidates must sign in using the Candidate Portal.")
                    return render(request, 'jobs/login.html', {'form': form})
        
        messages.error(request, "Invalid credentials.")
        return render(request, 'jobs/login.html', {'form': form})

class RecruiterLogoutView(View):
    def post(self, request):
        logout(request)
        messages.success(request, "You have logged out successfully.")
        return redirect('job_list')
        
    def get(self, request):
        logout(request)
        messages.success(request, "You have logged out successfully.")
        return redirect('job_list')

class CandidateSignupView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('candidate_dashboard')
        form = CandidateSignupForm()
        return render(request, 'jobs/candidate_signup.html', {'form': form})
        
    def post(self, request):
        form = CandidateSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome to ApexHire!")
            return redirect('candidate_dashboard')
        return render(request, 'jobs/candidate_signup.html', {'form': form})

class CandidateLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if not (request.user.is_staff or request.user.is_superuser):
                return redirect('candidate_dashboard')
            else:
                logout(request)
        form = AuthenticationForm()
        return render(request, 'jobs/candidate_login.html', {'form': form})
        
    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if not (user.is_staff or user.is_superuser):
                    login(request, user)
                    messages.success(request, f"Welcome back, {username}!")
                    return redirect('candidate_dashboard')
                else:
                    messages.error(request, "Invalid credentials. Recruiters must sign in using the Recruiter Portal.")
                    return render(request, 'jobs/candidate_login.html', {'form': form})
        
        messages.error(request, "Invalid username or password.")
        return render(request, 'jobs/candidate_login.html', {'form': form})

class CandidateDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.is_staff or request.user.is_superuser:
            messages.info(request, "Recruiters are redirected to the ATS Dashboard.")
            return redirect('recruiter_dashboard')
            
        candidate = getattr(request.user, 'candidate_profile', None)
        if not candidate:
            candidate = Candidate.objects.create(
                user=request.user,
                full_name=request.user.get_full_name() or request.user.username,
                email=request.user.email,
                phone='',
                skills=''
            )
            
        form = CandidateForm(instance=candidate)
        applications = candidate.applications.all().select_related('job_posting', 'job_posting__company')
        
        return render(request, 'jobs/candidate_dashboard.html', {
            'candidate': candidate,
            'applications': applications,
            'form': form
        })
        
    def post(self, request):
        candidate = get_object_or_404(Candidate, user=request.user)
        form = CandidateForm(request.POST, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('candidate_dashboard')
            
        applications = candidate.applications.all().select_related('job_posting', 'job_posting__company')
        return render(request, 'jobs/candidate_dashboard.html', {
            'candidate': candidate,
            'applications': applications,
            'form': form
        })


class RecruiterSignupView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                return redirect('recruiter_dashboard')
            else:
                return redirect('candidate_dashboard')
        form = RecruiterSignupForm()
        return render(request, 'jobs/recruiter_signup.html', {'form': form})
        
    def post(self, request):
        form = RecruiterSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, recruiter {user.username}! Your company and account are now registered.")
            return redirect('recruiter_dashboard')
        return render(request, 'jobs/recruiter_signup.html', {'form': form})


