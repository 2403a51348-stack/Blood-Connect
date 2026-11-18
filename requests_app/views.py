from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import BloodRequest, RequesterProfile
from .forms import BloodRequestForm
from matching.services import find_and_rank_matching_donors, MEDICAL_DISCLAIMER
from matching.models import DonorMatch
from notifications.utils import create_notification


@login_required
def requester_dashboard(request):
    """
    Dashboard for Blood Requesters to monitor active requests,
    view potential donor matches, and manage historical emergency posts.
    """
    user_requests = BloodRequest.objects.filter(requester=request.user).order_by('-created_at')

    active_count = user_requests.filter(status__in=['PENDING', 'DONOR_CONTACTED', 'ACCEPTED', 'IN_PROGRESS']).count()
    completed_count = user_requests.filter(status='COMPLETED').count()
    total_count = user_requests.count()

    context = {
        'requests': user_requests,
        'active_count': active_count,
        'completed_count': completed_count,
        'total_count': total_count,
    }
    return render(request, 'requests/dashboard.html', context)


@login_required
def create_blood_request(request):
    """
    Handles emergency blood request submission and initiates donor discovery.
    """
    if request.method == 'POST':
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.requester = request.user
            blood_request.save()

            # Execute preliminary matching algorithm immediately
            matches = find_and_rank_matching_donors(blood_request)

            # Create notification for requester
            create_notification(
                recipient=request.user,
                title=f"Request Created: {blood_request.request_id}",
                message=f"Your blood request for {blood_request.patient_name} ({blood_request.blood_group}) has been registered. We found {len(matches)} potential matching donors.",
                notification_type='REQUEST_CREATED',
                related_url=f"/requests/{blood_request.id}/track/"
            )

            messages.success(
                request,
                f"Emergency blood request {blood_request.request_id} created successfully! Matching donors have been identified."
            )
            return redirect('matching_results', request_id=blood_request.id)
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        # Pre-fill phone and city from user profile if available
        initial = {}
        if hasattr(request.user, 'profile'):
            initial['contact_phone'] = request.user.profile.phone
            initial['city'] = request.user.profile.city
            initial['state'] = request.user.profile.state
            initial['contact_name'] = request.user.get_full_name() or request.user.username
        form = BloodRequestForm(initial=initial)

    return render(request, 'requests/create_request.html', {
        'form': form,
        'disclaimer': MEDICAL_DISCLAIMER
    })


@login_required
def track_request(request, request_id):
    """
    Detailed tracking view for a specific blood request showing timeline and donor responses.
    """
    blood_request = get_object_or_404(BloodRequest, id=request_id)

    # Security check: Requester, staff, or contacted donor can view tracking details
    is_requester = blood_request.requester == request.user
    is_staff = request.user.is_staff or request.user.is_superuser
    is_contacted_donor = DonorMatch.objects.filter(blood_request=blood_request, donor__user=request.user).exists()

    if not (is_requester or is_staff or is_contacted_donor):
        messages.error(request, "You do not have authorization to view this request.")
        return redirect('home')

    matches = DonorMatch.objects.filter(blood_request=blood_request).select_related('donor', 'donor__user').order_by('-match_score')
    responses = blood_request.responses.select_related('donor').order_by('-responded_at')

    context = {
        'request_obj': blood_request,
        'matches': matches,
        'responses': responses,
        'is_requester': is_requester,
        'disclaimer': MEDICAL_DISCLAIMER,
    }
    return render(request, 'requests/track_request.html', context)


@login_required
def all_requests_tracking(request):
    """
    Lists blood requests for tracking (both user's own and system-wide active requests).
    """
    if request.user.is_staff:
        requests_list = BloodRequest.objects.all().order_by('-created_at')
    else:
        requests_list = BloodRequest.objects.filter(requester=request.user).order_by('-created_at')

    return render(request, 'requests/tracking_list.html', {
        'requests': requests_list
    })


@login_required
def cancel_request(request, request_id):
    """
    Allows a requester to cancel an active blood request.
    """
    blood_request = get_object_or_404(BloodRequest, id=request_id)

    if blood_request.requester != request.user and not request.user.is_staff:
        messages.error(request, "You do not have permission to cancel this request.")
        return redirect('requester_dashboard')

    if request.method == 'POST':
        blood_request.status = 'CANCELLED'
        blood_request.save()

        # Notify all contacted donors that the request was cancelled
        contacted_matches = DonorMatch.objects.filter(blood_request=blood_request, status='CONTACTED')
        for match in contacted_matches:
            create_notification(
                recipient=match.donor.user,
                title=f"Request Cancelled ({blood_request.blood_group})",
                message=f"The blood request for {blood_request.patient_name} at {blood_request.hospital_name} has been cancelled.",
                notification_type='REQUEST_CANCELLED',
                related_url=f"/requests/{blood_request.id}/track/"
            )

        messages.info(request, f"Request {blood_request.request_id} has been cancelled.")
        return redirect('track_request', request_id=blood_request.id)

    return redirect('track_request', request_id=blood_request.id)


@login_required
def complete_request(request, request_id):
    """
    Marks a blood request as fulfilled/completed.
    """
    blood_request = get_object_or_404(BloodRequest, id=request_id)

    if blood_request.requester != request.user and not request.user.is_staff:
        messages.error(request, "You do not have permission to update this request.")
        return redirect('requester_dashboard')

    if request.method == 'POST':
        blood_request.status = 'COMPLETED'
        blood_request.save()

        create_notification(
            recipient=request.user,
            title=f"Blood Request Completed: {blood_request.request_id}",
            message=f"Thank you! Blood request for {blood_request.patient_name} is now marked as Completed.",
            notification_type='REQUEST_COMPLETED',
            related_url=f"/requests/{blood_request.id}/track/"
        )

        messages.success(request, f"Request {blood_request.request_id} marked as Completed. Thank you to all donors!")
        return redirect('track_request', request_id=blood_request.id)

    return redirect('track_request', request_id=blood_request.id)
