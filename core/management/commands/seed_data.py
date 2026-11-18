from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from accounts.models import UserProfile
from donors.models import DonorProfile, DonationHistory
from requests_app.models import RequesterProfile, BloodRequest
from matching.models import DonorMatch, DonationResponse
from matching.services import evaluate_donor_match, contact_matched_donor
from notifications.models import Notification
from dashboard.models import AdminActivityLog


class Command(BaseCommand):
    help = 'Seeds the database with realistic demo users, donors, requesters, blood requests, and matches.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Starting BloodConnect demo data generation...'))

        # 1. Create Superuser / Administrator
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@bloodconnect.org',
                'first_name': 'System',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('Admin@12345')
            admin_user.save()
            UserProfile.objects.create(
                user=admin_user,
                role='ADMIN',
                phone='+91 9000000001',
                city='Hyderabad',
                state='Telangana',
                address='BloodConnect Central HQ, Hitec City, Hyderabad'
            )
            self.stdout.write(self.style.SUCCESS('Created Administrator: admin / Admin@12345'))
        else:
            self.stdout.write('Admin already exists.')

        # 2. Create Donors
        donors_data = [
            {
                'username': 'rahul_sharma',
                'first': 'Rahul',
                'last': 'Sharma',
                'email': 'rahul.sharma@example.com',
                'blood': 'O+',
                'phone': '+91 9876500001',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'address': 'Flat 302, Green Meadows, Madhapur, Hyderabad',
                'available': True,
                'donations': 4,
            },
            {
                'username': 'sneha_patel',
                'first': 'Sneha',
                'last': 'Patel',
                'email': 'sneha.patel@example.com',
                'blood': 'O-',
                'phone': '+91 9876500002',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'address': 'Plot 45, Jubilee Hills, Hyderabad',
                'available': True,
                'donations': 6,
            },
            {
                'username': 'vikram_reddy',
                'first': 'Vikram',
                'last': 'Reddy',
                'email': 'vikram.reddy@example.com',
                'blood': 'A+',
                'phone': '+91 9876500003',
                'city': 'Secunderabad',
                'state': 'Telangana',
                'address': 'House 12, West Marredpally, Secunderabad',
                'available': True,
                'donations': 2,
            },
            {
                'username': 'ananya_sen',
                'first': 'Ananya',
                'last': 'Sen',
                'email': 'ananya.sen@example.com',
                'blood': 'B+',
                'phone': '+91 9876500004',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'address': 'Gachibowli Financial District, Hyderabad',
                'available': True,
                'donations': 3,
            },
            {
                'username': 'karthik_nair',
                'first': 'Karthik',
                'last': 'Nair',
                'email': 'karthik.nair@example.com',
                'blood': 'AB+',
                'phone': '+91 9876500005',
                'city': 'Warangal',
                'state': 'Telangana',
                'address': 'Subedari, Hanamkonda, Warangal',
                'available': True,
                'donations': 1,
            },
            {
                'username': 'divya_joshi',
                'first': 'Divya',
                'last': 'Joshi',
                'email': 'divya.joshi@example.com',
                'blood': 'A-',
                'phone': '+91 9876500006',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'address': 'Kukatpally Housing Board, Hyderabad',
                'available': False,
                'donations': 5,
            },
            {
                'username': 'mohammed_ali',
                'first': 'Mohammed',
                'last': 'Ali',
                'email': 'mohammed.ali@example.com',
                'blood': 'B-',
                'phone': '+91 9876500007',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'address': 'Banjara Hills, Road No 10, Hyderabad',
                'available': True,
                'donations': 2,
            },
            {
                'username': 'pooja_verma',
                'first': 'Pooja',
                'last': 'Verma',
                'email': 'pooja.verma@example.com',
                'blood': 'AB-',
                'phone': '+91 9876500008',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'address': 'Indiranagar 100ft Road, Bangalore',
                'available': True,
                'donations': 2,
            },
        ]

        created_donors = []
        for d in donors_data:
            user, created = User.objects.get_or_create(
                username=d['username'],
                defaults={
                    'email': d['email'],
                    'first_name': d['first'],
                    'last_name': d['last'],
                }
            )
            if created:
                user.set_password('Donor@12345')
                user.save()

                UserProfile.objects.create(
                    user=user,
                    role='DONOR',
                    phone=d['phone'],
                    city=d['city'],
                    state=d['state'],
                    address=d['address']
                )

                donor_p = DonorProfile.objects.create(
                    user=user,
                    blood_group=d['blood'],
                    phone=d['phone'],
                    city=d['city'],
                    state=d['state'],
                    address=d['address'],
                    is_available=d['available'],
                    total_donations=d['donations'],
                    last_donation_date=timezone.now().date() - timedelta(days=90)
                )

                # Add a sample past donation record
                DonationHistory.objects.create(
                    donor=donor_p,
                    donation_date=timezone.now().date() - timedelta(days=90),
                    units_donated=1,
                    hospital_name='Apollo Hospital, Jubilee Hills',
                    notes='Voluntary emergency donation through BloodConnect',
                    verified_by_hospital=True
                )
                created_donors.append(donor_p)
                self.stdout.write(f"Created Donor: {d['username']} ({d['blood']}, {d['city']})")

        # 3. Create Requesters
        requesters_data = [
            {
                'username': 'arun_kumar',
                'first': 'Arun',
                'last': 'Kumar',
                'email': 'arun.kumar@example.com',
                'phone': '+91 9888800001',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'address': 'Mehdipatnam, Hyderabad',
                'org': 'Family Patient Representative',
            },
            {
                'username': 'care_hospital_coord',
                'first': 'Dr. Ramesh',
                'last': 'Chandra',
                'email': 'ramesh.chandra@carehospitals.com',
                'phone': '+91 9888800002',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'address': 'Care Hospital, Road No 1, Banjara Hills, Hyderabad',
                'org': 'Care Hospital Blood Bank',
            },
        ]

        created_requesters = []
        for r in requesters_data:
            user, created = User.objects.get_or_create(
                username=r['username'],
                defaults={
                    'email': r['email'],
                    'first_name': r['first'],
                    'last_name': r['last'],
                }
            )
            if created:
                user.set_password('Requester@12345')
                user.save()

                UserProfile.objects.create(
                    user=user,
                    role='REQUESTER',
                    phone=r['phone'],
                    city=r['city'],
                    state=r['state'],
                    address=r['address']
                )

                req_p = RequesterProfile.objects.create(
                    user=user,
                    phone=r['phone'],
                    city=r['city'],
                    state=r['state'],
                    address=r['address'],
                    organization_name=r['org']
                )
                created_requesters.append(req_p)
                self.stdout.write(f"Created Requester: {r['username']}")

        # 4. Create Blood Requests
        if created_requesters:
            req_user_1 = created_requesters[0].user
            req_user_2 = created_requesters[1].user

            req1 = BloodRequest.objects.create(
                requester=req_user_1,
                patient_name='Rajesh Kumar (Cardiac ICU)',
                blood_group='O+',
                units_required=2,
                hospital_name='NIMS Hospital',
                hospital_address='Punjagutta, Hyderabad',
                city='Hyderabad',
                state='Telangana',
                contact_name='Arun Kumar',
                contact_phone='+91 9888800001',
                urgency='CRITICAL',
                status='DONOR_CONTACTED',
                additional_notes='Scheduled for emergency coronary bypass at 9 AM tomorrow.'
            )

            req2 = BloodRequest.objects.create(
                requester=req_user_2,
                patient_name='Deepa Varma (Maternity Ward)',
                blood_group='A+',
                units_required=1,
                hospital_name='Care Hospital',
                hospital_address='Road No 1, Banjara Hills, Hyderabad',
                city='Hyderabad',
                state='Telangana',
                contact_name='Dr. Ramesh Chandra',
                contact_phone='+91 9888800002',
                urgency='HIGH',
                status='PENDING',
                additional_notes='Platelet and whole blood requirement post-operative.'
            )

            req3 = BloodRequest.objects.create(
                requester=req_user_1,
                patient_name='Suresh Rao (Trauma Care)',
                blood_group='B+',
                units_required=3,
                hospital_name='Yashoda Hospital',
                hospital_address='Somajiguda, Hyderabad',
                city='Hyderabad',
                state='Telangana',
                contact_name='Arun Kumar',
                contact_phone='+91 9888800001',
                urgency='MEDIUM',
                status='ACCEPTED',
                additional_notes='Accident emergency trauma care patient.'
            )

            # Match donors for req1
            rahul_donor = DonorProfile.objects.filter(user__username='rahul_sharma').first()
            sneha_donor = DonorProfile.objects.filter(user__username='sneha_patel').first()

            if rahul_donor:
                score, reasons, _ = evaluate_donor_match(req1, rahul_donor)
                m1 = DonorMatch.objects.create(
                    blood_request=req1,
                    donor=rahul_donor,
                    match_score=score,
                    match_reasons="\n".join(reasons),
                    status='CONTACTED',
                    contacted_at=timezone.now() - timedelta(hours=2)
                )
                Notification.objects.create(
                    recipient=rahul_donor.user,
                    title=f"Urgent Blood Request ({req1.blood_group}) - {req1.city}",
                    message=f"Patient {req1.patient_name} urgently requires {req1.units_required} unit(s) at {req1.hospital_name}.",
                    notification_type='DONOR_CONTACTED',
                    related_url=f"/requests/{req1.id}/track/"
                )

            if sneha_donor:
                score, reasons, _ = evaluate_donor_match(req1, sneha_donor)
                m2 = DonorMatch.objects.create(
                    blood_request=req1,
                    donor=sneha_donor,
                    match_score=score,
                    match_reasons="\n".join(reasons),
                    status='ACCEPTED',
                    contacted_at=timezone.now() - timedelta(hours=3),
                    responded_at=timezone.now() - timedelta(hours=1)
                )
                DonationResponse.objects.create(
                    donor_match=m2,
                    donor=sneha_donor,
                    blood_request=req1,
                    response='ACCEPTED',
                    remarks='I can reach NIMS Hospital by 6:00 PM today. Please keep paperwork ready.'
                )
                Notification.objects.create(
                    recipient=req_user_1,
                    title="Donor Accepted! (O-)",
                    message=f"Donor Sneha Patel (O-) accepted request {req1.request_id}. Contact: {sneha_donor.phone}",
                    notification_type='DONOR_ACCEPTED',
                    related_url=f"/requests/{req1.id}/track/"
                )

            # Admin log
            AdminActivityLog.objects.create(
                admin_user=admin_user,
                action_type='SYSTEM_INITIALIZED',
                description='BloodConnect system seed data successfully initialized with verified donors and test requests.',
                target_model='System'
            )

        self.stdout.write(self.style.SUCCESS('BloodConnect demo data seeded successfully!'))
