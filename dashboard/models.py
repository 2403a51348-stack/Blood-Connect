from django.db import models
from django.contrib.auth.models import User


class AdminActivityLog(models.Model):
    """
    Audit log of administrative actions performed on the platform.
    """
    admin_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_logs'
    )
    action_type = models.CharField(
        max_length=50,
        help_text="e.g. USER_STATUS_CHANGE, REQUEST_UPDATE, ACCOUNT_BLOCKED"
    )
    description = models.TextField()
    target_model = models.CharField(max_length=50, blank=True)
    target_id = models.CharField(max_length=50, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        username = self.admin_user.username if self.admin_user else "System"
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} | {username} | {self.action_type}"
