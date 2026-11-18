import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class RequesterProfile(models.Model):
    """
    Profile for registered Blood Requesters (patients, patient family, hospitals).
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='requester_profile'
    )
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, default='Telangana')
    address = models.TextField()
    organization_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional organization or hospital affiliation."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.city})"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username


class BloodRequest(models.Model):
    """
    Emergency and standard Blood Requests submitted by requesters.
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

    URGENCY_LEVELS = [
        ('LOW', 'Low - Scheduled in 48+ Hours'),
        ('MEDIUM', 'Medium - Needed within 24 Hours'),
        ('HIGH', 'High - Needed within 12 Hours'),
        ('CRITICAL', 'Critical / Emergency - Immediate Need'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('DONOR_CONTACTED', 'Donor Contacted'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    request_id = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        db_index=True
    )
    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blood_requests'
    )
    patient_name = models.CharField(max_length=150)
    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUPS,
        db_index=True
    )
    units_required = models.PositiveIntegerField(default=1)
    hospital_name = models.CharField(max_length=200)
    hospital_address = models.TextField()
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100, default='Telangana')
    contact_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=15)
    urgency = models.CharField(
        max_length=20,
        choices=URGENCY_LEVELS,
        default='HIGH',
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True
    )
    additional_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.request_id:
            timestamp = timezone.now().strftime('%Y%m%d')
            unique_part = uuid.uuid4().hex[:6].upper()
            self.request_id = f"REQ-{timestamp}-{unique_part}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.request_id} - {self.patient_name} ({self.blood_group}, {self.units_required} unit(s))"

    @property
    def is_active(self):
        return self.status in ['PENDING', 'DONOR_CONTACTED', 'ACCEPTED', 'IN_PROGRESS']
