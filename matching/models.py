from django.db import models
from django.utils import timezone


class DonorMatch(models.Model):
    """
    Represents a preliminary match between a BloodRequest and a DonorProfile.
    """
    STATUS_CHOICES = [
        ('SUGGESTED', 'Suggested by Algorithm'),
        ('CONTACTED', 'Contacted by Requester'),
        ('ACCEPTED', 'Accepted by Donor'),
        ('DECLINED', 'Declined by Donor'),
    ]

    blood_request = models.ForeignKey(
        'requests_app.BloodRequest',
        on_delete=models.CASCADE,
        related_name='matches'
    )
    donor = models.ForeignKey(
        'donors.DonorProfile',
        on_delete=models.CASCADE,
        related_name='matches'
    )
    match_score = models.PositiveIntegerField(
        default=0,
        help_text="Calculated compatibility score (0 - 100)"
    )
    match_reasons = models.TextField(
        blank=True,
        help_text="Human-readable breakdown of factors contributing to this match score."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SUGGESTED'
    )
    contacted_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blood_request', 'donor')
        ordering = ['-match_score', '-created_at']

    def __str__(self):
        return f"Match: {self.donor.full_name} ({self.donor.blood_group}) for {self.blood_request.request_id} - Score: {self.match_score}%"


class DonationResponse(models.Model):
    """
    Formal response given by a donor when contacted for a blood request.
    """
    RESPONSE_CHOICES = [
        ('ACCEPTED', 'Accepted - Ready to Donate'),
        ('DECLINED', 'Declined - Currently Unable'),
    ]

    donor_match = models.ForeignKey(
        DonorMatch,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    donor = models.ForeignKey(
        'donors.DonorProfile',
        on_delete=models.CASCADE,
        related_name='responses'
    )
    blood_request = models.ForeignKey(
        'requests_app.BloodRequest',
        on_delete=models.CASCADE,
        related_name='responses'
    )
    response = models.CharField(
        max_length=20,
        choices=RESPONSE_CHOICES
    )
    remarks = models.TextField(
        blank=True,
        help_text="Optional comments, estimated arrival time, or reason for declining."
    )
    responded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-responded_at']

    def __str__(self):
        return f"{self.donor.full_name} {self.response} for {self.blood_request.request_id}"
