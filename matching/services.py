from django.utils import timezone
from django.db.models import Q
from donors.models import DonorProfile
from notifications.utils import create_notification
from .models import DonorMatch

# Red blood cell transfusion compatibility mapping:
# Key = Recipient's Blood Group (What patient needs)
# Value = List of Compatible Donor Blood Groups (Who can give to patient)
RED_CELL_COMPATIBILITY = {
    'O-': ['O-'],
    'O+': ['O-', 'O+'],
    'A-': ['O-', 'A-'],
    'A+': ['O-', 'O+', 'A-', 'A+'],
    'B-': ['O-', 'B-'],
    'B+': ['O-', 'O+', 'B-', 'B+'],
    'AB-': ['O-', 'A-', 'B-', 'AB-'],
    'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],  # Universal recipient
}

# Reverse mapping: Who can a donor give to?
DONOR_CAN_DONATE_TO = {
    'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],  # Universal donor
    'O+': ['O+', 'A+', 'B+', 'AB+'],
    'A-': ['A-', 'A+', 'AB-', 'AB+'],
    'A+': ['A+', 'AB+'],
    'B-': ['B-', 'B+', 'AB-', 'AB+'],
    'B+': ['B+', 'AB+'],
    'AB-': ['AB-', 'AB+'],
    'AB+': ['AB+'],
}

MEDICAL_DISCLAIMER = (
    "PRELIMINARY DISCOVERY NOTICE: The BloodConnect matching system is an initial "
    "software-based locator intended solely for coordinating communication with potential donors. "
    "Software matching DOES NOT constitute medical certification of compatibility. "
    "Actual biological compatibility, cross-matching, donor eligibility, infectious disease testing, "
    "and transfusions must always be conducted and confirmed by licensed medical professionals or "
    "accredited blood banks."
)


def get_compatible_donor_blood_groups(recipient_blood_group):
    """
    Returns the list of donor blood groups compatible with the given recipient group.
    """
    return RED_CELL_COMPATIBILITY.get(recipient_blood_group, [recipient_blood_group])


def evaluate_donor_match(blood_request, donor):
    """
    Evaluates compatibility between a BloodRequest and a DonorProfile.
    Returns:
        (score: int, reasons: list of str, is_medically_compatible: bool)
    """
    score = 0
    reasons = []

    req_bg = blood_request.blood_group
    donor_bg = donor.blood_group
    compatible_groups = get_compatible_donor_blood_groups(req_bg)

    # 1. Blood Group Compatibility (up to 40 points)
    if donor_bg == req_bg:
        score += 40
        reasons.append(f"Identical blood group match ({donor_bg}) [+40 pts]")
        is_compatible = True
    elif donor_bg in compatible_groups:
        score += 30
        reasons.append(f"Medically compatible red-cell donor ({donor_bg} can donate to {req_bg}) [+30 pts]")
        is_compatible = True
    else:
        reasons.append(f"Incompatible red-cell blood group ({donor_bg} for {req_bg}) [0 pts]")
        is_compatible = False

    # 2. Availability Status (up to 25 points)
    if donor.is_available:
        score += 25
        reasons.append("Donor is currently marked as Available [+25 pts]")
    else:
        reasons.append("Donor is currently marked as Unavailable [0 pts]")

    # 3. Location / Distance Factor (up to 25 points)
    req_city = (blood_request.city or '').strip().lower()
    donor_city = (donor.city or '').strip().lower()
    req_state = (blood_request.state or '').strip().lower()
    donor_state = (donor.state or '').strip().lower()

    if req_city and donor_city and req_city == donor_city:
        score += 25
        reasons.append(f"Same city location ({donor.city}) [+25 pts]")
    elif req_state and donor_state and req_state == donor_state:
        score += 15
        reasons.append(f"Same state location ({donor.state}, different city: {donor.city}) [+15 pts]")
    else:
        score += 5
        reasons.append("Interstate / distant donor location [+5 pts]")

    # 4. Donor Activity & Reliability History (up to 10 points)
    if donor.total_donations >= 3:
        score += 6
        reasons.append(f"Experienced donor with {donor.total_donations} verified donations [+6 pts]")
    elif donor.total_donations > 0:
        score += 3
        reasons.append(f"Past donor with {donor.total_donations} donation(s) [+3 pts]")

    # Recent availability freshness bonus (within 14 days)
    if donor.availability_updated_at:
        days_since_update = (timezone.now() - donor.availability_updated_at).days
        if days_since_update <= 7:
            score += 4
            reasons.append("Availability recently verified within the last 7 days [+4 pts]")
        elif days_since_update <= 30:
            score += 2
            reasons.append("Availability verified within the last 30 days [+2 pts]")

    return min(score, 100), reasons, is_compatible


def find_and_rank_matching_donors(blood_request, filter_available_only=False):
    """
    Finds all potential donors, calculates match scores, and stores or updates
    DonorMatch records in the database.
    """
    compatible_groups = get_compatible_donor_blood_groups(blood_request.blood_group)

    # Filter donors with compatible blood groups
    donors_query = DonorProfile.objects.filter(
        blood_group__in=compatible_groups,
        user__is_active=True
    ).exclude(user=blood_request.requester)

    if filter_available_only:
        donors_query = donors_query.filter(is_available=True)

    evaluated_matches = []

    for donor in donors_query:
        score, reasons, is_compatible = evaluate_donor_match(blood_request, donor)
        reasons_text = "\n".join(reasons)

        match_record, _ = DonorMatch.objects.update_or_create(
            blood_request=blood_request,
            donor=donor,
            defaults={
                'match_score': score,
                'match_reasons': reasons_text,
            }
        )

        evaluated_matches.append({
            'donor': donor,
            'match_record': match_record,
            'score': score,
            'reasons': reasons,
            'is_compatible': is_compatible,
            'is_available': donor.is_available,
        })

    # Sort primarily by match score descending, then by availability
    evaluated_matches.sort(
        key=lambda item: (item['score'], item['is_available']),
        reverse=True
    )

    return evaluated_matches


def contact_matched_donor(blood_request, donor_profile):
    """
    Sends a direct donation request notification to a specific matched donor.
    """
    match_record, _ = DonorMatch.objects.get_or_create(
        blood_request=blood_request,
        donor=donor_profile,
    )
    match_record.status = 'CONTACTED'
    match_record.contacted_at = timezone.now()
    match_record.save()

    # Update request status to DONOR_CONTACTED if still pending
    if blood_request.status == 'PENDING':
        blood_request.status = 'DONOR_CONTACTED'
        blood_request.save()

    # Send in-app notification to the donor
    create_notification(
        recipient=donor_profile.user,
        title=f"Urgent Blood Request ({blood_request.blood_group}) - {blood_request.city}",
        message=(
            f"Patient {blood_request.patient_name} urgently requires {blood_request.units_required} unit(s) "
            f"of {blood_request.blood_group} blood at {blood_request.hospital_name}, {blood_request.city}. "
            f"Urgency: {blood_request.get_urgency_display()}."
        ),
        notification_type='DONOR_CONTACTED',
        related_url=f"/requests/{blood_request.id}/track/"
    )

    return match_record
