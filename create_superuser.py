import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User

username = os.environ.get('SUPERUSER_USERNAME', 'admin')
password = os.environ.get('SUPERUSER_PASSWORD', 'admin123')
email = os.environ.get('SUPERUSER_EMAIL', 'admin@example.com')

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser: {username}")
    User.objects.create_superuser(username=username, email=email, password=password)
else:
    print(f"Superuser {username} already exists.")
