from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from jobs.models import Company, JobPosting, Candidate, JobApplication, RecruiterProfile

class ApexHireAuthTests(TestCase):
    def setUp(self):
        # Create a company
        self.company = Company.objects.create(
            name="Test Corp",
            location="Bangalore"
        )
        # Create a job
        self.job = JobPosting.objects.create(
            company=self.company,
            title="Software Developer",
            description="Django developer",
            requirements="Python",
            location="Remote",
            salary_range="₹8,00,000 - ₹12,00,000"
        )
        
        # Create recruiter user
        self.recruiter_user = User.objects.create_user(
            username="recruiter",
            email="recruiter@test.com",
            password="password123",
            is_staff=True
        )
        
        # Create candidate user & profile
        self.candidate_user = User.objects.create_user(
            username="candidate",
            email="candidate@test.com",
            password="password123"
        )
        self.candidate_profile = Candidate.objects.create(
            user=self.candidate_user,
            full_name="Jane Doe",
            email="candidate@test.com",
            phone="9876543210",
            skills="Python, Django"
        )

    def test_candidate_signup(self):
        response = self.client.post(reverse('candidate_signup'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'password123',
            'password_confirm': 'password123',
            'full_name': 'New Candidate',
            'phone': '9999988888',
            'skills': 'React'
        })
        self.assertEqual(response.status_code, 302) # Redirect to candidate dashboard
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(Candidate.objects.filter(full_name='New Candidate').exists())

    def test_candidate_dashboard_access(self):
        # Candidate dashboard redirects unauthenticated
        response = self.client.get(reverse('candidate_dashboard'))
        self.assertEqual(response.status_code, 302)
        
        # Logged in recruiter is redirected to ATS dashboard
        self.client.login(username='recruiter', password='password123')
        response = self.client.get(reverse('candidate_dashboard'))
        self.assertRedirects(response, reverse('recruiter_dashboard'))
        self.client.logout()

        # Logged in candidate can access dashboard
        self.client.login(username='candidate', password='password123')
        response = self.client.get(reverse('candidate_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_recruiter_dashboard_access(self):
        # Recruiter dashboard redirects unauthenticated
        response = self.client.get(reverse('recruiter_dashboard'))
        self.assertEqual(response.status_code, 302)
        
        # Logged in candidate cannot access and gets redirected to job list
        self.client.login(username='candidate', password='password123')
        response = self.client.get(reverse('recruiter_dashboard'))
        self.assertRedirects(response, reverse('job_list'))
        self.client.logout()

        # Logged in recruiter can access dashboard
        self.client.login(username='recruiter', password='password123')
        response = self.client.get(reverse('recruiter_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_recruiter_cannot_apply_for_jobs(self):
        self.client.login(username='recruiter', password='password123')
        response = self.client.post(reverse('apply_to_job', args=[self.job.id]), {
            'cover_letter': 'I want this job!'
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(JobApplication.objects.filter(job_posting=self.job).exists())

    def test_candidate_can_apply_for_jobs(self):
        self.client.login(username='candidate', password='password123')
        response = self.client.post(reverse('apply_to_job', args=[self.job.id]), {
            'cover_letter': 'I am a perfect fit for this job!'
        })
        self.assertEqual(response.status_code, 302) # Redirect to job detail (success message)
        self.assertTrue(JobApplication.objects.filter(job_posting=self.job, candidate=self.candidate_profile).exists())

    def test_recruiter_company_isolation(self):
        # Create secondary company & recruiter
        company_b = Company.objects.create(name="Company B", location="Mumbai")
        recruiter_b_user = User.objects.create_user(
            username="recruiter_b",
            email="recruiter_b@test.com",
            password="password123",
            is_staff=True
        )
        # Explicitly assign recruiter profiles
        RecruiterProfile.objects.create(user=self.recruiter_user, company=self.company)
        RecruiterProfile.objects.create(user=recruiter_b_user, company=company_b)
        
        # Create job & application for Company B
        job_b = JobPosting.objects.create(
            company=company_b,
            title="Frontend Developer",
            description="React developer",
            requirements="JS",
            location="Remote"
        )
        app_b = JobApplication.objects.create(
            job_posting=job_b,
            candidate=self.candidate_profile,
            cover_letter="I love React!"
        )
        
        # Create application for Company A (self.job)
        app_a = JobApplication.objects.create(
            job_posting=self.job,
            candidate=self.candidate_profile,
            cover_letter="I love Django!"
        )
        
        # Log in as Recruiter A (linked to self.company)
        self.client.login(username='recruiter', password='password123')
        response = self.client.get(reverse('recruiter_dashboard'))
        self.assertEqual(response.status_code, 200)
        # Should see App A but not App B
        self.assertContains(response, app_a.candidate.full_name)
        self.assertNotContains(response, app_b.job_posting.title)
        self.client.logout()
        
        # Log in as Recruiter B (linked to company_b)
        self.client.login(username='recruiter_b', password='password123')
        response = self.client.get(reverse('recruiter_dashboard'))
        self.assertEqual(response.status_code, 200)
        # Should see App B but not App A
        self.assertContains(response, app_b.candidate.full_name)
        self.assertNotContains(response, app_a.job_posting.title)
        self.client.logout()

    def test_recruiter_can_post_job(self):
        # Explicitly associate recruiter with self.company
        RecruiterProfile.objects.create(user=self.recruiter_user, company=self.company)
        
        self.client.login(username='recruiter', password='password123')
        
        # Check GET request renders form
        response = self.client.get(reverse('post_job'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Post a New Job Role")
        
        # Submit form
        response = self.client.post(reverse('post_job'), {
            'title': 'New Product Manager',
            'description': 'Manage product lifecycle',
            'requirements': 'Experience with SaaS',
            'location': 'Bangalore',
            'job_type': 'Full-time',
            'experience_level': 'Senior Level',
            'salary_range': '₹15,00,000 - ₹20,00,000',
            'tags': 'PM, Product',
            'is_active': True
        })
        self.assertRedirects(response, reverse('recruiter_dashboard'))
        
        # Verify it was created and assigned to Recruiter's company
        new_job = JobPosting.objects.get(title='New Product Manager')
        self.assertEqual(new_job.company, self.company)
        self.client.logout()

    def test_candidate_cannot_post_job(self):
        self.client.login(username='candidate', password='password123')
        response = self.client.get(reverse('post_job'))
        # Should redirect candidate away (RecruiterRequiredMixin redirects to job_list)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('job_list'))

    def test_recruiter_signup_existing_company(self):
        response = self.client.post(reverse('recruiter_signup'), {
            'username': 'new_recruiter',
            'email': 'new_recruiter@test.com',
            'password': 'password123',
            'password_confirm': 'password123',
            'company_choice': str(self.company.id)
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('recruiter_dashboard'))
        
        # Verify database
        user = User.objects.get(username='new_recruiter')
        self.assertTrue(user.is_staff)
        self.assertEqual(user.recruiter_profile.company, self.company)

    def test_recruiter_signup_new_company(self):
        response = self.client.post(reverse('recruiter_signup'), {
            'username': 'new_recruiter_new_co',
            'email': 'new_recruiter_new_co@test.com',
            'password': 'password123',
            'password_confirm': 'password123',
            'company_choice': 'new',
            'new_company_name': 'SuperTech Ltd',
            'new_company_location': 'Berlin'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('recruiter_dashboard'))
        
        # Verify database
        user = User.objects.get(username='new_recruiter_new_co')
        self.assertTrue(user.is_staff)
        
        company = Company.objects.get(name='SuperTech Ltd')
        self.assertEqual(company.location, 'Berlin')
        self.assertEqual(user.recruiter_profile.company, company)

    def test_recruiter_signup_validation_new_company_missing_fields(self):
        response = self.client.post(reverse('recruiter_signup'), {
            'username': 'recruiter_fail',
            'email': 'recruiter_fail@test.com',
            'password': 'password123',
            'password_confirm': 'password123',
            'company_choice': 'new',
            'new_company_name': '',  # missing!
            'new_company_location': ''  # missing!
        })
        self.assertEqual(response.status_code, 200) # Form re-rendered
        self.assertFormError(response.context['form'], 'new_company_name', "This field is required for new companies.")
        self.assertFormError(response.context['form'], 'new_company_location', "This field is required for new companies.")



