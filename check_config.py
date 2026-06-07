import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservices.settings')
django.setup()

from django.conf import settings

print('✅ Django Settings Loaded')
print(f'   - DEBUG: {settings.DEBUG}')
print(f'   - INSTALLED_APPS count: {len(settings.INSTALLED_APPS)}')
print(f'   - MIDDLEWARE count: {len(settings.MIDDLEWARE)}')
db_engine = settings.DATABASES['default']['ENGINE']
print(f'   - Database: {db_engine}')

required = ['RAZORPAY_KEY_ID', 'RAZORPAY_KEY_SECRET', 'DEFAULT_FROM_EMAIL', 'EMAIL_HOST']
missing = []
for key in required:
    if not hasattr(settings, key) or not getattr(settings, key):
        missing.append(key)

if missing:
    print(f'\nWarning: Missing settings: {missing}')
else:
    print('✅ All required settings present')

try:
    import razorpay
    print('✅ razorpay package available')
except ImportError:
    print('❌ razorpay package NOT installed')

try:
    from PIL import Image
    print('✅ Pillow package available')
except ImportError:
    print('❌ Pillow package NOT installed')
