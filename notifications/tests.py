from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from notifications.models import Notification
from notifications.utils import create_notification


class NotificationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='notif_user', password='Password123')

    def test_create_and_read_notification(self):
        notif = create_notification(
            recipient=self.user,
            title='Test Alert',
            message='Emergency request alert',
            notification_type='SYSTEM',
            related_url='/notifications/'
        )
        self.assertFalse(notif.is_read)

        self.client.login(username='notif_user', password='Password123')
        read_url = reverse('mark_notification_read', args=[notif.id])
        response = self.client.get(read_url)
        self.assertEqual(response.status_code, 302)

        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

    def test_mark_all_read(self):
        create_notification(recipient=self.user, title='N1', message='M1')
        create_notification(recipient=self.user, title='N2', message='M2')
        self.assertEqual(Notification.objects.filter(recipient=self.user, is_read=False).count(), 2)

        self.client.login(username='notif_user', password='Password123')
        response = self.client.post(reverse('mark_all_notifications_read'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Notification.objects.filter(recipient=self.user, is_read=False).count(), 0)
