"""
Management command to seed initial data (service categories + services)
Run: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from services.models import ServiceCategory, Service


class Command(BaseCommand):
    help = 'Seeds the database with initial service categories and services'

    def handle(self, *args, **kwargs):
        # Categories
        cats = [
            ('Home Cleaning', '🧹', 'Professional home cleaning services'),
            ('Kitchen Services', '🍳', 'Kitchen deep clean and maintenance'),
            ('Repair & Maintenance', '🔧', 'All kinds of home repairs'),
            ('Personal Care', '💅', 'Beauty and personal grooming'),
            ('Laundry', '👗', 'Laundry and dry cleaning'),
            ('Painting', '🎨', 'Interior and exterior painting'),
        ]
        for name, icon, desc in cats:
            cat, created = ServiceCategory.objects.get_or_create(name=name, defaults={'icon': icon, 'description': desc})
            if created:
                self.stdout.write(f'  ✅ Created category: {name}')

        # Services
        services = [
            ('Home Cleaning',          'Full Home Cleaning',       'Complete deep cleaning of your entire home including all rooms and surfaces.', 799, 3),
            ('Home Cleaning',          'Living Room Cleaning',     'Thorough cleaning of living room — furniture, floors, windows.', 399, 2),
            ('Home Cleaning',          'Bathroom Deep Clean',      'Scrubbing, disinfecting, and sanitising your bathroom completely.', 349, 1),
            ('Kitchen Services',       'Kitchen Deep Clean',       'Complete kitchen cleaning including chimney, stove, and appliances.', 599, 2),
            ('Kitchen Services',       'Chimney Cleaning',         'Professional chimney cleaning and degreasing service.', 449, 2),
            ('Repair & Maintenance',   'Plumbing Repair',         'Fixing leaks, pipe issues, taps, and drainage problems.', 499, 2),
            ('Repair & Maintenance',   'Electrical Repair',        'Safe fixing of wiring, switches, fans, and electrical issues.', 549, 2),
            ('Repair & Maintenance',   'AC Service',              'Full AC cleaning, gas refill, and service checkup.', 699, 2),
            ('Personal Care',          'Home Makeup Service',      'Professional bridal and party makeup at your doorstep.', 999, 2),
            ('Personal Care',          'Haircut at Home',          'Professional haircut and styling service at home.', 349, 1),
            ('Laundry',                'Laundry & Folding',       'Washing, drying, and folding of clothes.', 299, 3),
            ('Laundry',                'Dry Cleaning',            'Premium dry cleaning for delicate garments.', 499, 1),
            ('Painting',               'Room Painting',           'Professional painting of a single room with primer and 2 coats.', 1999, 6),
            ('Painting',               'Full House Painting',     'Complete interior painting of your entire home.', 7999, 8),
        ]
        for cat_name, svc_name, desc, price, hours in services:
            try:
                cat = ServiceCategory.objects.get(name=cat_name)
                svc, created = Service.objects.get_or_create(
                    name=svc_name, category=cat,
                    defaults={'description': desc, 'price': price, 'duration_hours': hours}
                )
                if created:
                    self.stdout.write(f'    ✅ Created service: {svc_name} (₹{price})')
            except ServiceCategory.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ⚠️ Category not found: {cat_name}'))

        self.stdout.write(self.style.SUCCESS('\n🎉 Seed data complete! You can now log in and start using the platform.'))
