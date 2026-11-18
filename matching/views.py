from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseForbidden

from requests_app.models import BloodRequest
from donors.models import DonorProfile
from .models import DonorMatch, DonationResponse
from .services import (
    find_and_rank_matching_donors,
    contact_matched_donor,
    MEDICAL_DISCLAIMER
)
from notifications.utils import create_notification


@login_required
def matching_results(request, request_id):
    """
    Displays ranked matching donors for a given blood request with
    match scores, breakdown explanations, and contact actions.
    """
    blood_request = get_object_or_404(BloodRequest, id=request_id)

    # Permission check: Requester or Admin
    if blood_request.requester != request.user and not request.user.is_staff:
        messages.error(request, "You do not have permission to view matching donors for this request.")
        return redirect('home')

    filter_available_only = request.GET.get('available_only', 'false').lower() == 'true'

    # Run the matching algorithm
    evaluated_matches = find_and_rank_matching_donors(
        blood_request,
        filter_available_only=filter_available_only
    )

    context = {
        'blood_request': blood_request,
        'matches': evaluated_matches,
        'filter_available_only': filter_available_only,
        'total_matches': len(evaluated_matches),
        'disclaimer': MEDICAL_DISCLAIMER,
    }
    return render(request, 'matching/matching_results.html', context)


@login_required
def contact_donor(request, match_id):
    """
    Initiates contact with an individual matched donor, sending an in-app notification.
    """
    match_record = get_object_or_404(DonorMatch, id=match_id)
    blood_request = match_record.blood_request

    # Verify authorization
    if blood_request.requester != request.user and not request.user.is_staff:
        messages.error(request, "Permission denied.")
        return redirect('home')

    if request.method == 'POST':
        contact_matched_donor(blood_request, match_record.donor)
        messages.success(
            request,
            f"Donation request sent to donor {match_record.donor.full_name} ({match_record.donor.blood_group})!"
        )

    return redirect('matching_results', request_id=blood_request.id)


@login_required
def contact_all_donors(request, request_id):
    """
    Broadcasts donation request notifications to all available matching donors.
    """
    blood_request = get_object_or_404(BloodRequest, id=request_id)

    if blood_request.requester != request.user and not request.user.is_staff:
        messages.error(request, "Permission denied.")
        return redirect('home')

    if request.method == 'POST':
        # Retrieve all matches that are available and not yet contacted
        eligible_matches = DonorMatch.objects.filter(
            blood_request=blood_request,
            donor__is_available=True,
            status='SUGGESTED'
        )

        count = 0
        for match in eligible_matches:
            contact_matched_donor(blood_request, match.donor)
            count += 1

        if count > 0:
            messages.success(request, f"Donation requests successfully broadcast to {count} matching donor(s)!")
        else:
            messages.info(request, "No new uncontacted available donors found for broadcast.")

    return redirect('matching_results', request_id=blood_request.id)


@login_required
def respond_to_request(request, match_id):
    """
    Enables a contacted donor to Accept or Decline a blood donation request.
    """
    match_record = get_object_or_404(DonorMatch, id=match_id)
    donor = match_record.donor

    # Verify that the logged-in user is indeed the donor
    if donor.user != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorized to respond to this request.")
        return redirect('home')

    blood_request = match_record.blood_request

    if request.method == 'POST':
        decision = request.POST.get('response')  # 'ACCEPTED' or 'DECLINED'
        remarks = request.POST.get('remarks', '').strip()

        if decision not in ['ACCEPTED', 'DECLINED']:
            messages.error(request, "Invalid response decision.")
            return redirect('donor_dashboard')

        # Update Match record
        match_record.status = decision
        match_record.responded_at = timezone.now()
        match_record.save()

        # Create Response record
        DonationResponse.objects.create(
            donor_match=match_record,
            donor=donor,
            blood_request=blood_request,
            response=decision,
            remarks=remarks
        )

        if decision == 'ACCEPTED':
            # Update blood request status to ACCEPTED
            blood_request.status = 'ACCEPTED'
            blood_request.save()

            # Notify Requester
            create_notification(
                recipient=blood_request.requester,
                title=f"Donor Accepted! ({donor.blood_group})",
                message=(
                    f"Great news! Donor {donor.full_name} ({donor.blood_group}) has accepted your blood request "
                    f"for {blood_request.patient_name} at {blood_request.hospital_name}. "
                    f"Contact Donor: {donor.phone} | Remarks: {remarks or 'None'}"
                ),
                notification_type='DONOR_ACCEPTED',
                related_url=f"/requests/{blood_request.id}/track/"
            )

            messages.success(
                request,
                f"Thank you for accepting! The requester has been notified with your contact details ({donor.phone})."
            )

        elif decision == 'DECLINED':
            # Notify Requester
            create_notification(
                recipient=blood_request.requester,
                title=f"Donor Declined Request",
                message=(
                    f"Donor {donor.full_name} is currently unable to donate for request {blood_request.request_id}. "
                    f"Remarks: {remarks or 'Not specified'}."
                ),
                notification_type='DONOR_DECLINED',
                related_url=f"/requests/{blood_request.id}/track/"
            )

            messages.info(request, "You have declined this request. The requester has been informed.")

        return redirect('donor_dashboard')

    context = {
        'match': match_record,
        'request_obj': blood_request,
        'disclaimer': MEDICAL_DISCLAIMER,
    }
    return render(request, 'matching/respond_request.html', context)
