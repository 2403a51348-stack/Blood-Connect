from .models import Notification


def unread_notifications_count(request):
    """
    Context processor that supplies unread notification count
    and role context to all templates.
    """
    if request.user.is_authenticated:
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        role = None
        if hasattr(request.user, 'profile'):
            role = request.user.profile.role
        elif hasattr(request.user, 'donor_profile'):
            role = 'DONOR'
        elif hasattr(request.user, 'requester_profile'):
            role = 'REQUESTER'
        elif request.user.is_staff or request.user.is_superuser:
            role = 'ADMIN'

        return {
            'unread_notifications_count': count,
            'current_user_role': role,
        }
    return {
        'unread_notifications_count': 0,
        'current_user_role': None,
    }
