from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    """
    In-app database notifications for users across BloodConnect actions.
    """
    TYPE_CHOICES = [
        ('REQUEST_CREATED', 'New Blood Request'),
        ('DONOR_CONTACTED', 'Donation Request Received'),
        ('DONOR_ACCEPTED', 'Donor Accepted Request'),
        ('DONOR_DECLINED', 'Donor Declined Request'),
        ('REQUEST_COMPLETED', 'Blood Request Completed'),
        ('REQUEST_CANCELLED', 'Blood Request Cancelled'),
        ('SYSTEM', 'System Alert'),
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default='SYSTEM'
    )
    is_read = models.BooleanField(default=False, db_index=True)
    related_url = models.CharField(
        max_length=255,
        blank=True,
        help_text="Direct link to relevant request, dashboard, or match"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status = "Read" if self.is_read else "Unread"
        return f"[{status}] {self.recipient.username} - {self.title}"
