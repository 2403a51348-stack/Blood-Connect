from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import UserProfile
from donors.models import DonorProfile
from requests_app.models import RequesterProfile


class AccountAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_donor_registration_success(self):
        url = reverse('register_donor')
        payload = {
            'first_name': 'Test',
            'last_name': 'Donor',
            'username': 'test_donor_1',
            'email': 'donor1@test.com',
            'password': 'Password123',
            'confirm_password': 'Password123',
            'blood_group': 'O+',
            'phone': '+91 9876543210',
            'city': 'Hyderabad',
            'state': 'Telangana',
            'address': 'Madhapur, Hyderabad',
        }
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='test_donor_1').exists())
        user = User.objects.get(username='test_donor_1')
        self.assertEqual(user.donor_profile.blood_group, 'O+')
        self.assertEqual(user.profile.role, 'DONOR')

    def test_requester_registration_success(self):
        url = reverse('register_requester')
        payload = {
            'first_name': 'Test',
            'last_name': 'Requester',
            'username': 'test_req_1',
            'email': 'req1@test.com',
            'password': 'Password123',
            'confirm_password': 'Password123',
            'phone': '+91 9876543211',
            'city': 'Secunderabad',
            'state': 'Telangana',
            'address': 'Marredpally',
            'organization_name': 'Care Hospital',
        }
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='test_req_1').exists())
        user = User.objects.get(username='test_req_1')
        self.assertEqual(user.profile.role, 'REQUESTER')
        self.assertEqual(user.requester_profile.organization_name, 'Care Hospital')

    def test_duplicate_username_prevented(self):
        User.objects.create_user(username='existinguser', password='Password123')
        url = reverse('register_donor')
        payload = {
            'first_name': 'Test',
            'last_name': 'Donor',
            'username': 'existinguser',
            'email': 'newemail@test.com',
            'password': 'Password123',
            'confirm_password': 'Password123',
            'blood_group': 'A+',
            'phone': '+91 9876543210',
            'city': 'Hyderabad',
            'state': 'Telangana',
            'address': 'Hyderabad',
        }
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'username', 'This username is already taken. Please choose another.')

    def test_login_and_logout(self):
        user = User.objects.create_user(username='loginuser', password='Password123')
        UserProfile.objects.create(user=user, role='DONOR', phone='9876543210', city='Hyderabad')
        DonorProfile.objects.create(user=user, blood_group='B+', phone='9876543210', city='Hyderabad', address='Hyd')

        login_url = reverse('login')
        response = self.client.post(login_url, {'username': 'loginuser', 'password': 'Password123'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('donor_dashboard'))

        logout_url = reverse('logout')
        logout_response = self.client.get(logout_url)
        self.assertEqual(logout_response.status_code, 302)
        self.assertRedirects(logout_response, reverse('home'))
