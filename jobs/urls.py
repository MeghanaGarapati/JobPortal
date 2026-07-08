from django.urls import path
from . import views

urlpatterns = [
    path('', views.JobListView.as_view(), name='job_list'),
    path('job/<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path('job/<int:pk>/apply/', views.ApplyToJobView.as_view(), name='apply_to_job'),
    
    # Recruiter URLs
    path('recruiter/login/', views.RecruiterLoginView.as_view(), name='recruiter_login'),
    path('recruiter/signup/', views.RecruiterSignupView.as_view(), name='recruiter_signup'),
    path('recruiter/dashboard/', views.RecruiterDashboardView.as_view(), name='recruiter_dashboard'),
    path('recruiter/job/new/', views.JobCreateView.as_view(), name='post_job'),
    path('recruiter/application/<int:pk>/status/', views.UpdateApplicationStatusView.as_view(), name='update_status'),
    
    # Candidate / User URLs
    path('candidate/signup/', views.CandidateSignupView.as_view(), name='candidate_signup'),
    path('candidate/login/', views.CandidateLoginView.as_view(), name='candidate_login'),
    path('candidate/dashboard/', views.CandidateDashboardView.as_view(), name='candidate_dashboard'),
    
    # Common Authentication
    path('login/', views.CandidateLoginView.as_view(), name='login'), # Default login falls back to Candidate
    path('logout/', views.RecruiterLogoutView.as_view(), name='logout'),
]
