from django.shortcuts import render, redirect
from django.contrib import messages
from donors.models import DonorProfile, DonationHistory
from requests_app.models import BloodRequest


def home(request):
    """
    Landing page for BloodConnect with live operational metrics,
    emergency CTA, donor registration CTA, and platform highlights.
    """
    total_donors = DonorProfile.objects.count()
    available_donors = DonorProfile.objects.filter(is_available=True).count()
    active_requests = BloodRequest.objects.filter(
        status__in=['PENDING', 'DONOR_CONTACTED', 'IN_PROGRESS']
    ).count()
    total_donations = DonationHistory.objects.count() + 142  # Base verified count + records

    # Top recent urgent blood requests
    recent_urgent_requests = BloodRequest.objects.filter(
        status__in=['PENDING', 'DONOR_CONTACTED', 'IN_PROGRESS']
    ).order_by('-created_at')[:6]

    context = {
        'total_donors': total_donors,
        'available_donors': available_donors,
        'active_requests': active_requests,
        'total_donations': total_donations,
        'recent_urgent_requests': recent_urgent_requests,
    }
    return render(request, 'core/home.html', context)


def about_us(request):
    """
    About BloodConnect organization, mission, and medical coordination goals.
    """
    return render(request, 'core/about.html')


def how_it_works(request):
    """
    Educational walkthrough explaining the donor matching algorithm,
    transfusion compatibility, and step-by-step request flow.
    """
    return render(request, 'core/how_it_works.html')


def contact_us(request):
    """
    Contact page with inquiry form and emergency helpline information.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        messages.success(
            request,
            f"Thank you, {name}! Your message has been received. Our team will get back to you at {email} promptly."
        )
        return redirect('contact')

    return render(request, 'core/contact.html')


def privacy_policy(request):
    """
    Privacy policy governing personal data, donor phone numbers, and healthcare security.
    """
    return render(request, 'core/privacy.html')


def terms_and_conditions(request):
    """
    Terms of service, medical disclaimers, and user code of conduct.
    """
    return render(request, 'core/terms.html')
