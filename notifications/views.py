from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Notification


@login_required
def notification_list(request):
    """
    Displays all notifications for the current authenticated user,
    highlighting unread notifications and providing direct action links.
    """
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()

    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@login_required
def mark_as_read(request, notification_id):
    """
    Marks a specific notification as read and redirects to its related URL if provided.
    """
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()

    if notification.related_url:
        return redirect(notification.related_url)

    return redirect('notification_list')


@login_required
def mark_all_as_read(request):
    """
    Marks all notifications for the authenticated user as read.
    """
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        messages.success(request, "All notifications marked as read.")
    return redirect('notification_list')
