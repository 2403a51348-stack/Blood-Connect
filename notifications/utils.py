from .models import Notification


def create_notification(recipient, title, message, notification_type='SYSTEM', related_url=''):
    """
    Utility function to create an in-app database notification.
    """
    if not recipient:
        return None
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        related_url=related_url
    )
