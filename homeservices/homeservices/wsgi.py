import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservices.settings')

application = get_wsgi_application()

# ── Auto-migrate + seed on Vercel cold start ─────────────────────────────────
def _auto_setup():
    """Run migrations and seed sample services automatically on Vercel."""
    try:
        from django.db import connection

        # Quick connectivity check — bail silently if DB is unreachable
        try:
            connection.ensure_connection()
        except Exception:
            return

        # Run pending migrations
        from django.core.management import call_command
        call_command('migrate', '--run-syncdb', verbosity=0, interactive=False)

        # Seed service categories + services if none exist yet
        from services.models import ServiceCategory, Service

        CATEGORIES = [
            ('Home Cleaning',        '🧹', 'Professional home cleaning services'),
            ('Kitchen Services',     '🍳', 'Kitchen deep clean and maintenance'),
            ('Repair & Maintenance', '🔧', 'All kinds of home repairs'),
            ('Personal Care',        '💅', 'Beauty and personal grooming'),
            ('Laundry',              '👗', 'Laundry and dry cleaning'),
            ('Painting',             '🎨', 'Interior and exterior painting'),
        ]

        SERVICES = [
            ('Home Cleaning',        'Full Home Cleaning',       'Complete deep cleaning of your entire home including all rooms, floors, and surfaces.', 799,  3),
            ('Home Cleaning',        'Living Room Cleaning',     'Thorough cleaning of living room — furniture, floors, windows, and ceiling fans.',    399,  2),
            ('Home Cleaning',        'Bathroom Deep Clean',      'Scrubbing, disinfecting, and sanitising your bathroom completely.',                    349,  1),
            ('Kitchen Services',     'Kitchen Deep Clean',       'Complete kitchen cleaning including chimney, stove, countertops, and appliances.',     599,  2),
            ('Kitchen Services',     'Chimney Cleaning',         'Professional chimney cleaning and degreasing service.',                                449,  2),
            ('Repair & Maintenance', 'Plumbing Repair',          'Fixing leaks, pipe issues, taps, and drainage problems at your home.',                 499,  2),
            ('Repair & Maintenance', 'Electrical Repair',        'Safe fixing of wiring, switches, fans, and all electrical issues.',                    549,  2),
            ('Repair & Maintenance', 'AC Service',               'Full AC cleaning, gas refill check, and complete service checkup.',                    699,  2),
            ('Personal Care',        'Home Makeup Service',      'Professional bridal and party makeup at your doorstep.',                               999,  2),
            ('Personal Care',        'Haircut at Home',          'Professional haircut and styling service done at your home.',                          349,  1),
            ('Laundry',              'Laundry & Folding',        'Washing, drying, and neatly folding your clothes.',                                    299,  3),
            ('Laundry',              'Dry Cleaning',             'Premium dry cleaning for delicate and designer garments.',                             499,  1),
            ('Painting',             'Room Painting',            'Professional painting of a single room with primer and 2 coats of paint.',            1999, 6),
            ('Painting',             'Full House Painting',      'Complete interior painting of your entire home with premium finish.',                  7999, 8),
        ]

        if not Service.objects.exists():
            for name, icon, desc in CATEGORIES:
                ServiceCategory.objects.get_or_create(
                    name=name, defaults={'icon': icon, 'description': desc}
                )
            for cat_name, svc_name, desc, price, hours in SERVICES:
                try:
                    cat = ServiceCategory.objects.get(name=cat_name)
                    Service.objects.get_or_create(
                        name=svc_name, category=cat,
                        defaults={'description': desc, 'price': price, 'duration_hours': hours, 'is_active': True}
                    )
                except ServiceCategory.DoesNotExist:
                    pass

    except Exception as e:
        # Never let setup errors crash the app
        print(f'[wsgi auto-setup] Warning: {e}')


_auto_setup()
