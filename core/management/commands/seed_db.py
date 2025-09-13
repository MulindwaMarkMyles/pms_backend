from django.core.management.base import BaseCommand
from core.models import Amenity, Furnishing
from tenants.models import TenantType
from complaints.models import ComplaintStatus
from payments.models import PaymentStatus


class Command(BaseCommand):
    help = 'Seed the database with initial data for property management system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))
        
        # Seed Amenities
        self.seed_amenities()
        
        # Seed Furnishings
        self.seed_furnishings()
        
        # Seed Tenant Types
        self.seed_tenant_types()
        
        # Seed Complaint Statuses
        self.seed_complaint_statuses()
        
        # Seed Payment Statuses
        self.seed_payment_statuses()
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))

    def seed_amenities(self):
        """Seed amenities data"""
        amenities_data = [
            {'name': 'Water', 'description': '24/7 running water supply'},
            {'name': 'Electricity', 'description': 'Reliable electricity connection'},
            {'name': 'Internet', 'description': 'High-speed internet connectivity'},
            {'name': 'Parking', 'description': 'Dedicated parking space'},
            {'name': 'Security', 'description': '24/7 security services'},
            {'name': 'Swimming Pool', 'description': 'Community swimming pool access'},
            {'name': 'Gym', 'description': 'Fitness center and gym facilities'},
            {'name': 'Playground', 'description': 'Children playground area'},
            {'name': 'Generator', 'description': 'Backup power generator'},
            {'name': 'CCTV', 'description': 'CCTV surveillance system'},
            {'name': 'Garden', 'description': 'Well-maintained garden area'},
            {'name': 'Elevator', 'description': 'Elevator access for upper floors'},
            {'name': 'Laundry', 'description': 'Laundry facilities'},
            {'name': 'Waste Management', 'description': 'Regular waste collection services'},
            {'name': 'Fire Safety', 'description': 'Fire safety systems and equipment'},
        ]
        
        created_count = 0
        for amenity_data in amenities_data:
            amenity, created = Amenity.objects.get_or_create(
                name=amenity_data['name'],
                defaults={'description': amenity_data['description']}
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created amenity: {amenity.name}")
        
        self.stdout.write(self.style.SUCCESS(f'Amenities: {created_count} new records created'))

    def seed_furnishings(self):
        """Seed furnishings data"""
        furnishings_data = [
            {'name': 'Air Conditioning', 'description': 'Central or split AC system'},
            {'name': 'Kitchen Appliances', 'description': 'Complete kitchen appliance set'},
            {'name': 'Bedroom Furniture', 'description': 'Bed, wardrobe, and bedroom essentials'},
            {'name': 'Living Room Furniture', 'description': 'Sofa set, coffee table, TV stand'},
            {'name': 'Dining Set', 'description': 'Dining table and chairs'},
            {'name': 'Washing Machine', 'description': 'Automatic washing machine'},
            {'name': 'Refrigerator', 'description': 'Large capacity refrigerator'},
            {'name': 'Microwave', 'description': 'Microwave oven'},
            {'name': 'Television', 'description': 'Smart TV with cable connection'},
            {'name': 'Water Heater', 'description': 'Electric or gas water heater'},
            {'name': 'Curtains & Blinds', 'description': 'Window treatments and privacy'},
            {'name': 'Study Table', 'description': 'Work desk and office chair'},
            {'name': 'Storage Cabinets', 'description': 'Additional storage solutions'},
            {'name': 'Ceiling Fans', 'description': 'Ceiling fans in all rooms'},
            {'name': 'Lighting Fixtures', 'description': 'Modern lighting throughout'},
        ]
        
        created_count = 0
        for furnishing_data in furnishings_data:
            furnishing, created = Furnishing.objects.get_or_create(
                name=furnishing_data['name'],
                defaults={'description': furnishing_data['description']}
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created furnishing: {furnishing.name}")
        
        self.stdout.write(self.style.SUCCESS(f'Furnishings: {created_count} new records created'))

    def seed_tenant_types(self):
        """Seed tenant types data"""
        tenant_types_data = [
            {'name': 'Short Stay (6 months or less)', 'description': 'Tenants with lease period of 6 months or less'},
            {'name': 'Long Term Stay (1+ years)', 'description': 'Tenants with lease period of 1 year or more'},
            {'name': 'Corporate Tenant', 'description': 'Company or organization leasing for employees'},
            {'name': 'Student Housing', 'description': 'Students or educational institution housing'},
            {'name': 'Vacation Rental', 'description': 'Short-term vacation or holiday rentals'},
            {'name': 'Monthly Rental', 'description': 'Month-to-month rental agreements'},
            {'name': 'Family Residence', 'description': 'Families seeking long-term residence'},
            {'name': 'Professional Housing', 'description': 'Working professionals and executives'},
        ]
        
        created_count = 0
        for tenant_type_data in tenant_types_data:
            tenant_type, created = TenantType.objects.get_or_create(
                name=tenant_type_data['name'],
                defaults={'description': tenant_type_data['description']}
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created tenant type: {tenant_type.name}")
        
        self.stdout.write(self.style.SUCCESS(f'Tenant Types: {created_count} new records created'))

    def seed_complaint_statuses(self):
        """Seed complaint statuses data"""
        complaint_statuses_data = [
            {'name': 'Open'},
            {'name': 'In Progress'},
            {'name': 'Pending Review'},
            {'name': 'Waiting for Parts'},
            {'name': 'Resolved'},
            {'name': 'Closed'},
            {'name': 'Cancelled'},
            {'name': 'Escalated'},
        ]
        
        created_count = 0
        for status_data in complaint_statuses_data:
            status, created = ComplaintStatus.objects.get_or_create(
                name=status_data['name']
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created complaint status: {status.name}")
        
        self.stdout.write(self.style.SUCCESS(f'Complaint Statuses: {created_count} new records created'))

    def seed_payment_statuses(self):
        """Seed payment statuses data"""
        payment_statuses_data = [
            {'name': 'Pending'},
            {'name': 'Paid'},
            {'name': 'Overdue'},
            {'name': 'Partial'},
            {'name': 'Cancelled'},
            {'name': 'Refunded'},
            {'name': 'Processing'},
            {'name': 'Failed'},
        ]
        
        created_count = 0
        for status_data in payment_statuses_data:
            status, created = PaymentStatus.objects.get_or_create(
                name=status_data['name']
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created payment status: {status.name}")
        
        self.stdout.write(self.style.SUCCESS(f'Payment Statuses: {created_count} new records created'))