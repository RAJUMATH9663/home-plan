import os
import django
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservices.settings')
if os.getenv('VERCEL') or os.getenv('VERCEL_ENV'):
    django.setup()
    call_command('migrate', interactive=False, verbosity=0)
application = get_wsgi_application()
