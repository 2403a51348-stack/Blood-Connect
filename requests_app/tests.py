from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import UserProfile
from requests_app.models import BloodRequest, RequesterProfile


class BloodRequestTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.req_user = User.objects.create_user(username='requester_test', password='Password123')
        self.profile = UserProfile.objects.create(user=self.req_user, role='REQUESTER', phone='9876543210', city='Hyderabad')
        self.req_profile = RequesterProfile.objects.create(
            user=self.req_user,
            phone='9876543210',
            city='Hyderabad',
            state='Telangana',
            address='Jubilee Hills'
        )

    def test_create_blood_request(self):
        self.client.login(username='requester_test', password='Password123')
        url = reverse('create_blood_request')
        payload = {
            'patient_name': 'Emergency Patient X',
            'blood_group': 'O-',
            'units_required': 2,
            'hospital_name': 'Care Hospital',
            'hospital_address': 'Road 1, Banjara Hills',
            'city': 'Hyderabad',
            'state': 'Telangana',
            'contact_name': 'Dr. Sharma',
            'contact_phone': '9876543210',
            'urgency': 'CRITICAL',
            'additional_notes': 'Immediate blood needed',
        }
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(BloodRequest.objects.filter(patient_name='Emergency Patient X').exists())
        req = BloodRequest.objects.get(patient_name='Emergency Patient X')
        self.assertTrue(req.request_id.startswith('REQ-'))
        self.assertEqual(req.status, 'PENDING')

    def test_cancel_blood_request(self):
        self.client.login(username='requester_test', password='Password123')
        req = BloodRequest.objects.create(
            requester=self.req_user,
            patient_name='Patient Cancel Test',
            blood_group='A+',
            units_required=1,
            hospital_name='Apollo Hospital',
            hospital_address='Jubilee Hills',
            city='Hyderabad',
            contact_name='Attendant',
            contact_phone='9876543210',
            urgency='HIGH',
            status='PENDING'
        )
        url = reverse('cancel_request', args=[req.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        req.refresh_from_db()
        self.assertEqual(req.status, 'CANCELLED')
