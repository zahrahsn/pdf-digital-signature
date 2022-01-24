"""
WSGI config for digitalsignature project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.contrib.auth.models import User
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digitalsignature.settings')

application = get_wsgi_application()

User.objects.create_superuser(
    username=os.getenv("SUPERUSER_USERNAME"),
    email=os.getenv("SUPERUSER_EMAIL"),
    password=os.getenv("SUPERUSER_PASS"),
    is_active=True,
    is_staff=True
)