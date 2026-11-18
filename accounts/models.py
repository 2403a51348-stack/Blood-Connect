from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Profile extension for the built-in Django User model.
    Maintains role distinction between Donors, Requesters, and Administrators.
    """
    ROLE_CHOICES = [
        ('DONOR', 'Blood Donor'),
        ('REQUESTER', 'Blood Requester'),
        ('ADMIN', 'Administrator'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='DONOR'
    )
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, default='Telangana')
    address = models.TextField(blank=True)
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
