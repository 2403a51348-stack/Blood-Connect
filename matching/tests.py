from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import UserProfile
from donors.models import DonorProfile
from requests_app.models import BloodRequest
from matching.models import DonorMatch, DonationResponse
from matching.services import (
    get_compatible_donor_blood_groups,
    evaluate_donor_match,
    find_and_rank_matching_donors,
    contact_matched_donor,
    RED_CELL_COMPATIBILITY
)
from notifications.models import Notification


class DonorMatchingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.req_user = User.objects.create_user(username='req_user', password='Password123')
        self.donor_user = User.objects.create_user(username='donor_user', password='Password123')

        self.donor_profile = DonorProfile.objects.create(
            user=self.donor_user,
            blood_group='O-',
            phone='+91 9876543210',
            city='Hyderabad',
            state='Telangana',
            address='Madhapur',
            is_available=True,
            total_donations=3
        )

        self.blood_request = BloodRequest.objects.create(
            requester=self.req_user,
            patient_name='Cardiac Patient',
            blood_group='A+',
            units_required=2,
            hospital_name='Apollo Hospital',
            hospital_address='Jubilee Hills',
            city='Hyderabad',
            state='Telangana',
            contact_name='Dr. Rao',
            contact_phone='+91 9876543211',
            urgency='HIGH',
            status='PENDING'
        )

    def test_transfusion_compatibility_rules(self):
        # O- can be accepted by all recipient blood groups
        for bg in RED_CELL_COMPATIBILITY:
            compatible_donors = get_compatible_donor_blood_groups(bg)
            self.assertIn('O-', compatible_donors)

        # AB+ is universal recipient (can receive from all 8 groups)
        self.assertEqual(len(get_compatible_donor_blood_groups('AB+')), 8)

        # O- recipient can only receive from O-
        self.assertEqual(get_compatible_donor_blood_groups('O-'), ['O-'])

    def test_evaluate_donor_match_scoring(self):
        score, reasons, is_compatible = evaluate_donor_match(self.blood_request, self.donor_profile)
        # O- donor for A+ request:
        # Compatible blood (30) + Available (25) + Same city (25) + >=3 donations (6) + freshness (4) = 90
        self.assertTrue(is_compatible)
        self.assertGreaterEqual(score, 80)
        self.assertTrue(any('compatible' in r.lower() for r in reasons))
        self.assertTrue(any('same city' in r.lower() for r in reasons))

    def test_contact_matched_donor_creates_notification(self):
        match_record = contact_matched_donor(self.blood_request, self.donor_profile)
        self.assertEqual(match_record.status, 'CONTACTED')
        self.blood_request.refresh_from_db()
        self.assertEqual(self.blood_request.status, 'DONOR_CONTACTED')

        # Donor should receive a notification
        donor_notifs = Notification.objects.filter(recipient=self.donor_user)
        self.assertTrue(donor_notifs.exists())
        self.assertEqual(donor_notifs.first().notification_type, 'DONOR_CONTACTED')

    def test_donor_accepts_request_flow(self):
        match_record = DonorMatch.objects.create(
            blood_request=self.blood_request,
            donor=self.donor_profile,
            match_score=90,
            status='CONTACTED'
        )

        self.client.login(username='donor_user', password='Password123')
        respond_url = reverse('respond_request', args=[match_record.id])
        payload = {
            'response': 'ACCEPTED',
            'remarks': 'I will be there in 30 minutes',
        }
        response = self.client.post(respond_url, data=payload)
        self.assertEqual(response.status_code, 302)

        match_record.refresh_from_db()
        self.assertEqual(match_record.status, 'ACCEPTED')

        self.blood_request.refresh_from_db()
        self.assertEqual(self.blood_request.status, 'ACCEPTED')

        # Requester must receive acceptance notification
        req_notif = Notification.objects.filter(recipient=self.req_user, notification_type='DONOR_ACCEPTED')
        self.assertTrue(req_notif.exists())
        self.assertIn(self.donor_profile.phone, req_notif.first().message)
