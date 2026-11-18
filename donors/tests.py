from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import UserProfile
from donors.models import DonorProfile, DonationHistory
from datetime import date


class DonorFeatureTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='donor_test', password='Password123')
        self.user_profile = UserProfile.objects.create(user=self.user, role='DONOR', phone='9876543210', city='Hyderabad')
        self.donor_profile = DonorProfile.objects.create(
            user=self.user,
            blood_group='A+',
            phone='9876543210',
            city='Hyderabad',
            state='Telangana',
            address='Banjara Hills',
            is_available=True
        )

    def test_donor_dashboard_accessible(self):
        self.client.login(username='donor_test', password='Password123')
        response = self.client.get(reverse('donor_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A+')
        self.assertContains(response, 'Available')

    def test_toggle_availability(self):
        self.client.login(username='donor_test', password='Password123')
        self.assertTrue(self.donor_profile.is_available)

        response = self.client.post(reverse('toggle_availability'))
        self.assertEqual(response.status_code, 302)
        self.donor_profile.refresh_from_db()
        self.assertFalse(self.donor_profile.is_available)

        # Toggle back
        self.client.post(reverse('toggle_availability'))
        self.donor_profile.refresh_from_db()
        self.assertTrue(self.donor_profile.is_available)

    def test_add_donation_history(self):
        self.client.login(username='donor_test', password='Password123')
        url = reverse('add_donation_record')
        payload = {
            'donation_date': '2026-11-01',
            'units_donated': 1,
            'hospital_name': 'NIMS Hospital',
            'notes': 'Test voluntary donation',
        }
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, 302)
        self.donor_profile.refresh_from_db()
        self.assertEqual(self.donor_profile.total_donations, 1)
        self.assertEqual(self.donor_profile.last_donation_date, date(2026, 11, 1))
