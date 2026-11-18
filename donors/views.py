from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from accounts.decorators import donor_required
from .models import DonorProfile, DonationHistory
from .forms import DonationHistoryForm
from requests_app.models import BloodRequest
from matching.models import DonorMatch, DonationResponse
from matching.services import DONOR_CAN_DONATE_TO


@donor_required
def donor_dashboard(request):
    """
    Primary dashboard for Blood Donors: displays profile metrics,
    availability switcher, direct donation requests, and public matching opportunities.
    """
    donor_profile = request.user.donor_profile

    # Direct requests sent specifically to this donor
    direct_matches = DonorMatch.objects.filter(
        donor=donor_profile
    ).select_related('blood_request', 'blood_request__requester').order_by('-created_at')[:10]

    # Find recipient blood groups that this donor's blood can be given to
    compatible_recipient_groups = DONOR_CAN_DONATE_TO.get(donor_profile.blood_group, [donor_profile.blood_group])

    # Open blood requests in the system matching this donor's blood
    relevant_requests = BloodRequest.objects.filter(
        blood_group__in=compatible_recipient_groups,
        status__in=['PENDING', 'DONOR_CONTACTED', 'IN_PROGRESS']
    ).exclude(requester=request.user).order_by('-created_at')[:10]

    recent_donations = donor_profile.donation_history.all()[:5]

    context = {
        'donor': donor_profile,
        'direct_matches': direct_matches,
        'relevant_requests': relevant_requests,
        'recent_donations': recent_donations,
    }
    return render(request, 'donors/dashboard.html', context)


@donor_required
def toggle_availability(request):
    """
    Allows a donor to quickly toggle their availability status (Available <-> Unavailable).
    """
    if request.method == 'POST':
        donor = request.user.donor_profile
        donor.is_available = not donor.is_available
        donor.availability_updated_at = timezone.now()
        donor.save()

        status_text = "Available" if donor.is_available else "Unavailable"
        messages.success(request, f"Your status has been updated to '{status_text}'.")
    return redirect('donor_dashboard')


@donor_required
def donation_history_list(request):
    """
    Displays the complete donation history for the authenticated donor.
    """
    donor = request.user.donor_profile
    history = donor.donation_history.all()
    form = DonationHistoryForm()

    context = {
        'donor': donor,
        'history': history,
        'form': form,
    }
    return render(request, 'donors/donation_history.html', context)


@donor_required
def add_donation_record(request):
    """
    Allows a donor to record a past or recent blood donation.
    """
    donor = request.user.donor_profile

    if request.method == 'POST':
        form = DonationHistoryForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.donor = donor
            record.save()

            # Update donor's aggregate donation stats
            donor.total_donations += record.units_donated
            donor.last_donation_date = record.donation_date
            donor.save()

            messages.success(request, 'Donation record added successfully!')
            return redirect('donor_history')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = DonationHistoryForm()

    return render(request, 'donors/donation_history.html', {
        'donor': donor,
        'history': donor.donation_history.all(),
        'form': form
    })
