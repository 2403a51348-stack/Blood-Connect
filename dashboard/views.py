from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone

from accounts.decorators import admin_required
from accounts.models import UserProfile
from donors.models import DonorProfile
from requests_app.models import BloodRequest, RequesterProfile
from matching.models import DonorMatch, DonationResponse
from .models import AdminActivityLog


@admin_required
def admin_dashboard(request):
    """
    Central administrative dashboard providing high-level operational metrics,
    system activity logs, and management shortcuts.
    """
    total_users = User.objects.count()
    total_donors = DonorProfile.objects.count()
    available_donors = DonorProfile.objects.filter(is_available=True).count()
    unavailable_donors = total_donors - available_donors
    total_requesters = RequesterProfile.objects.count()

    total_requests = BloodRequest.objects.count()
    pending_requests = BloodRequest.objects.filter(status='PENDING').count()
    accepted_requests = BloodRequest.objects.filter(status='ACCEPTED').count()
    completed_requests = BloodRequest.objects.filter(status='COMPLETED').count()
    cancelled_requests = BloodRequest.objects.filter(status='CANCELLED').count()

    # Blood group distribution among registered donors
    blood_group_counts = DonorProfile.objects.values('blood_group').annotate(
        count=Count('id')
    ).order_by('blood_group')

    # Urgency breakdown for requests
    urgency_counts = BloodRequest.objects.values('urgency').annotate(
        count=Count('id')
    )

    recent_logs = AdminActivityLog.objects.select_related('admin_user').order_by('-timestamp')[:10]
    recent_requests = BloodRequest.objects.select_related('requester').order_by('-created_at')[:8]
    recent_donors = DonorProfile.objects.select_related('user').order_by('-created_at')[:6]

    context = {
        'total_users': total_users,
        'total_donors': total_donors,
        'available_donors': available_donors,
        'unavailable_donors': unavailable_donors,
        'total_requesters': total_requesters,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'accepted_requests': accepted_requests,
        'completed_requests': completed_requests,
        'cancelled_requests': cancelled_requests,
        'blood_group_counts': blood_group_counts,
        'urgency_counts': urgency_counts,
        'recent_logs': recent_logs,
        'recent_requests': recent_requests,
        'recent_donors': recent_donors,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@admin_required
def manage_donors(request):
    """
    Administrative list and management view for all registered blood donors.
    """
    donors = DonorProfile.objects.select_related('user').all()

    # Filter options
    bg = request.GET.get('blood_group')
    city = request.GET.get('city')
    availability = request.GET.get('availability')

    if bg:
        donors = donors.filter(blood_group=bg)
    if city:
        donors = donors.filter(city__icontains=city)
    if availability in ['true', 'false']:
        donors = donors.filter(is_available=(availability == 'true'))

    context = {
        'donors': donors,
        'selected_bg': bg,
        'selected_city': city,
        'selected_availability': availability,
        'blood_groups': [b[0] for b in DonorProfile.BLOOD_GROUPS],
    }
    return render(request, 'dashboard/manage_donors.html', context)


@admin_required
def manage_requesters(request):
    """
    Administrative view for all registered blood requesters.
    """
    requesters = RequesterProfile.objects.select_related('user').all()
    city = request.GET.get('city')
    if city:
        requesters = requesters.filter(city__icontains=city)

    return render(request, 'dashboard/manage_requesters.html', {
        'requesters': requesters,
        'selected_city': city,
    })


@admin_required
def manage_requests(request):
    """
    Administrative overview of all blood requests with filtering and status controls.
    """
    requests_list = BloodRequest.objects.select_related('requester').all().order_by('-created_at')

    status_filter = request.GET.get('status')
    urgency_filter = request.GET.get('urgency')

    if status_filter:
        requests_list = requests_list.filter(status=status_filter)
    if urgency_filter:
        requests_list = requests_list.filter(urgency=urgency_filter)

    return render(request, 'dashboard/manage_requests.html', {
        'requests': requests_list,
        'status_choices': BloodRequest.STATUS_CHOICES,
        'urgency_choices': BloodRequest.URGENCY_LEVELS,
        'selected_status': status_filter,
        'selected_urgency': urgency_filter,
    })


@admin_required
def toggle_user_active(request, user_id):
    """
    Enables administrators to deactivate/block or reactivate suspicious user accounts.
    """
    target_user = get_object_or_404(User, id=user_id)

    if target_user == request.user:
        messages.error(request, "You cannot deactivate your own administrative account.")
        return redirect('admin_dashboard')

    if request.method == 'POST':
        target_user.is_active = not target_user.is_active
        target_user.save()

        action = "USER_REACTIVATED" if target_user.is_active else "USER_DEACTIVATED"
        desc = f"Administrator {request.user.username} changed account status of '{target_user.username}' to active={target_user.is_active}."

        AdminActivityLog.objects.create(
            admin_user=request.user,
            action_type=action,
            description=desc,
            target_model='User',
            target_id=str(target_user.id),
            ip_address=request.META.get('REMOTE_ADDR')
        )

        status_msg = "activated" if target_user.is_active else "deactivated"
        messages.success(request, f"User account '{target_user.username}' has been {status_msg}.")

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('admin_dashboard')


@admin_required
def update_request_status_admin(request, request_id):
    """
    Allows administrators to manually intervene and update the status of any blood request.
    """
    blood_request = get_object_or_404(BloodRequest, id=request_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = [choice[0] for choice in BloodRequest.STATUS_CHOICES]

        if new_status in valid_statuses:
            old_status = blood_request.status
            blood_request.status = new_status
            blood_request.save()

            AdminActivityLog.objects.create(
                admin_user=request.user,
                action_type='REQUEST_STATUS_UPDATED',
                description=f"Status for {blood_request.request_id} updated from {old_status} to {new_status}.",
                target_model='BloodRequest',
                target_id=str(blood_request.id),
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Request {blood_request.request_id} status updated to {new_status}.")
        else:
            messages.error(request, "Invalid status choice selected.")

    return redirect('manage_requests')


@admin_required
def activity_logs_view(request):
    """
    View complete administrative audit logs.
    """
    logs = AdminActivityLog.objects.select_related('admin_user').order_by('-timestamp')
    return render(request, 'dashboard/activity_logs.html', {'logs': logs})
