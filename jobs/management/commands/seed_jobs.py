from django.core.management.base import BaseCommand
from jobs.models import Company, JobPosting, Candidate, JobApplication

class Command(BaseCommand):
    help = 'Seeds initial companies and job postings for testing.'

    def handle(self, *args, **options):
        self.stdout.write("Clearing existing data...")
        JobApplication.objects.all().delete()
        Candidate.objects.all().delete()
        JobPosting.objects.all().delete()
        Company.objects.all().delete()

        self.stdout.write("Seeding companies...")
        stripe = Company.objects.create(
            name="Stripe",
            logo_url="https://images.ctfassets.net/fzn2n1nzq1n5/6O2Q3s1e7X7eUqUgu4cW2O/c7ba8d2f788102a9db26ff52fb97950c/stripe-logo.svg",
            website="https://stripe.com",
            description="Stripe is a financial infrastructure platform for the internet. Millions of companies—from the world’s largest enterprises to the most ambitious startups—use Stripe to accept payments, grow their revenue, and accelerate new business opportunities.",
            location="San Francisco, CA"
        )
        
        vercel = Company.objects.create(
            name="Vercel",
            logo_url="",
            website="https://vercel.com",
            description="Vercel provides the developer experience and infrastructure to build, deploy, and scale the web. Vercel enables developers to host web applications that deploy instantly and scale automatically.",
            location="Remote / New York"
        )
        
        openai = Company.objects.create(
            name="OpenAI",
            logo_url="",
            website="https://openai.com",
            description="OpenAI is an AI research and deployment company. Our mission is to ensure that artificial general intelligence benefits all of humanity.",
            location="San Francisco, CA"
        )
        
        apex = Company.objects.create(
            name="ApexLabs",
            logo_url="",
            website="https://apexlabs.ai",
            description="ApexLabs builds state of the art agentic AI infrastructure and coding co-pilots for developers worldwide.",
            location="Austin, TX"
        )

        self.stdout.write("Seeding job postings...")
        JobPosting.objects.create(
            company=stripe,
            title="Senior Django Backend Engineer",
            description="We are looking for a Senior Backend Engineer to join our Core API team. In this role, you will scale our billing infrastructure using Python and Django, design resilient payment systems, and collaborate with frontend engineers to build world-class user experiences.",
            requirements="5+ years of software engineering experience.\nExpert knowledge of Python and Django framework.\nExperience designing and optimizing PostgreSQL databases.\nFamiliarity with financial systems or payment processing is a strong plus.",
            location="Remote (US / Canada)",
            job_type="Remote",
            experience_level="Senior Level",
            salary_range="₹15,00,000 - ₹25,00,000",
            tags="Python, Django, PostgreSQL, API, Security"
        )

        JobPosting.objects.create(
            company=vercel,
            title="Frontend Developer - Next.js",
            description="Join the Next.js core team to build the future of the web. You will work on optimizing rendering performances, improving developer tools, and crafting high-fidelity design templates for developers worldwide.",
            requirements="Deep knowledge of React, Next.js, and TypeScript.\nExpertise in CSS, TailwindCSS, and layout optimizations.\nStrong understanding of browser rendering and Web Vitals.\nPassion for open-source development.",
            location="New York, NY",
            job_type="Full-time",
            experience_level="Mid Level",
            salary_range="₹12,00,000 - ₹18,00,000",
            tags="TypeScript, React, Next.js, CSS, Tailwind"
        )

        JobPosting.objects.create(
            company=openai,
            title="AI Research Engineer",
            description="OpenAI is searching for Research Engineers to push the boundaries of large language models and multi-modal systems. You will train massive neural networks, optimize model inference speeds, and deploy scalable pipelines.",
            requirements="Strong mathematical foundations in linear algebra, calculus, and probability.\nExpertise in PyTorch and distributed training frameworks.\nExperience working with GPU clusters and high-performance computing.\nTrack record of shipping research models into production environments.",
            location="San Francisco, CA",
            job_type="Full-time",
            experience_level="Lead / Exec",
            salary_range="₹35,00,000 - ₹50,00,000",
            tags="Python, PyTorch, AI, LLM, CUDA"
        )

        JobPosting.objects.create(
            company=apex,
            title="Full-Stack Engineer (Python/React)",
            description="ApexLabs is looking for a versatile Full-Stack Engineer to build our AI coding platform. You will implement features end-to-end, writing robust APIs in Django/FastAPI and building a responsive, polished UI in React.",
            requirements="3+ years of professional full-stack development experience.\nProficient with Python/Django and React/TypeScript.\nExperience with WebSockets or real-time event streaming.\nEye for detail and passion for slick animations and interactions.",
            location="Austin, TX",
            job_type="Full-time",
            experience_level="Mid Level",
            salary_range="₹10,00,000 - ₹16,00,000",
            tags="Python, Django, React, TypeScript, CSS"
        )
        
        JobPosting.objects.create(
            company=stripe,
            title="Database Administrator Internship",
            description="Stripe is hiring a DBA intern for our database infrastructure team. Learn database replication, query optimization, and performance scaling under the mentorship of senior database engineers.",
            requirements="Currently pursuing a BS/MS in Computer Science or related fields.\nBasic understanding of relational databases (PostgreSQL/MySQL).\nFamiliarity with Linux command line and SQL.",
            location="San Francisco, CA",
            job_type="Internship",
            experience_level="Entry Level",
            salary_range="₹25,000 - ₹40,000 / month",
            tags="PostgreSQL, SQL, Linux, Infrastructure"
        )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
