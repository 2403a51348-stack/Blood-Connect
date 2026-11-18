from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class DonorProfile(models.Model):
    """
    Profile for registered Blood Donors with blood group and availability status.
    """
    BLOOD_GROUPS = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='donor_profile'
    )
    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUPS,
        db_index=True
    )
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100, default='Telangana')
    address = models.TextField()
    is_available = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Designates whether the donor is currently ready and able to donate."
    )
    last_donation_date = models.DateField(null=True, blank=True)
    total_donations = models.PositiveIntegerField(default=0)
    availability_updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.blood_group}) - {self.city}"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def email(self):
        return self.user.email


class DonationHistory(models.Model):
    """
    Records of past blood donations made by the donor.
    """
    donor = models.ForeignKey(
        DonorProfile,
        on_delete=models.CASCADE,
        related_name='donation_history'
    )
    blood_request = models.ForeignKey(
        'requests_app.BloodRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='donation_records'
    )
    donation_date = models.DateField(default=timezone.now)
    units_donated = models.PositiveIntegerField(default=1)
    hospital_name = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    verified_by_hospital = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-donation_date', '-created_at']
        verbose_name_plural = 'Donation histories'

    def __str__(self):
        return f"{self.donor.full_name} - {self.units_donated} unit(s) at {self.hospital_name} on {self.donation_date}"
