from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .forms import DonorRegistrationForm, RequesterRegistrationForm, UserLoginForm, ProfileUpdateForm
from .models import UserProfile
from donors.models import DonorProfile
from requests_app.models import RequesterProfile
from notifications.utils import create_notification


def donor_register(request):
    """
    Handles Donor registration workflow with User, UserProfile, and DonorProfile creation.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create base User
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name']
                    )

                    # Create UserProfile role entry
                    UserProfile.objects.create(
                        user=user,
                        role='DONOR',
                        phone=form.cleaned_data['phone'],
                        city=form.cleaned_data['city'],
                        state=form.cleaned_data['state'],
                        address=form.cleaned_data['address']
                    )

                    # Create DonorProfile
                    DonorProfile.objects.create(
                        user=user,
                        blood_group=form.cleaned_data['blood_group'],
                        phone=form.cleaned_data['phone'],
                        city=form.cleaned_data['city'],
                        state=form.cleaned_data['state'],
                        address=form.cleaned_data['address'],
                        is_available=True
                    )

                    # Welcome notification
                    create_notification(
                        recipient=user,
                        title="Welcome to BloodConnect!",
                        message="Your donor profile has been registered. You will receive notifications when urgent blood requests matching your blood group are submitted.",
                        notification_type='SYSTEM',
                        related_url='/donor/dashboard/'
                    )

                messages.success(request, 'Donor registration successful! Welcome to BloodConnect.')
                login(request, user)
                return redirect('donor_dashboard')

            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
    else:
        form = DonorRegistrationForm()

    return render(request, 'accounts/register_donor.html', {'form': form})


def requester_register(request):
    """
    Handles Blood Requester registration workflow.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RequesterRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name']
                    )

                    UserProfile.objects.create(
                        user=user,
                        role='REQUESTER',
                        phone=form.cleaned_data['phone'],
                        city=form.cleaned_data['city'],
                        state=form.cleaned_data['state'],
                        address=form.cleaned_data['address']
                    )

                    RequesterProfile.objects.create(
                        user=user,
                        phone=form.cleaned_data['phone'],
                        city=form.cleaned_data['city'],
                        state=form.cleaned_data['state'],
                        address=form.cleaned_data['address'],
                        organization_name=form.cleaned_data.get('organization_name', '')
                    )

                    create_notification(
                        recipient=user,
                        title="Welcome to BloodConnect!",
                        message="Your requester account is active. You can now post emergency blood requests and connect with matching donors.",
                        notification_type='SYSTEM',
                        related_url='/requester/dashboard/'
                    )

                messages.success(request, 'Requester registration successful! You can now create blood requests.')
                login(request, user)
                return redirect('requester_dashboard')

            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
    else:
        form = RequesterRegistrationForm()

    return render(request, 'accounts/register_requester.html', {'form': form})


def user_login(request):
    """
    Unified login view with smart role-based redirection.
    """
    if request.user.is_authenticated:
        return redirect_user_by_role(request.user)

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect_user_by_role(user)
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    """
    Logs out the user and safely redirects to home.
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


def redirect_user_by_role(user):
    """
    Helper function to direct logged-in users to their respective dashboards.
    """
    if user.is_staff or user.is_superuser:
        return redirect('admin_dashboard')
    
    if hasattr(user, 'profile') and user.profile.role == 'ADMIN':
        return redirect('admin_dashboard')

    if hasattr(user, 'donor_profile'):
        return redirect('donor_dashboard')

    if hasattr(user, 'requester_profile'):
        return redirect('requester_dashboard')

    return redirect('home')


@login_required
def profile_management(request):
    """
    Allows logged-in users (donors, requesters, or admins) to update their contact details.
    """
    user = request.user
    user_profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': 'DONOR' if hasattr(user, 'donor_profile') else 'REQUESTER'}
    )

    donor_profile = getattr(user, 'donor_profile', None)
    requester_profile = getattr(user, 'requester_profile', None)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            with transaction.atomic():
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.email = form.cleaned_data['email']
                user.save()

                user_profile.phone = form.cleaned_data['phone']
                user_profile.city = form.cleaned_data['city']
                user_profile.state = form.cleaned_data['state']
                user_profile.address = form.cleaned_data['address']
                user_profile.save()

                if donor_profile:
                    donor_profile.phone = form.cleaned_data['phone']
                    donor_profile.city = form.cleaned_data['city']
                    donor_profile.state = form.cleaned_data['state']
                    donor_profile.address = form.cleaned_data['address']
                    donor_profile.save()

                if requester_profile:
                    requester_profile.phone = form.cleaned_data['phone']
                    requester_profile.city = form.cleaned_data['city']
                    requester_profile.state = form.cleaned_data['state']
                    requester_profile.address = form.cleaned_data['address']
                    requester_profile.save()

            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone': user_profile.phone,
            'city': user_profile.city,
            'state': user_profile.state,
            'address': user_profile.address,
        }
        form = ProfileUpdateForm(instance=user, initial=initial_data)

    context = {
        'form': form,
        'user_profile': user_profile,
        'donor_profile': donor_profile,
        'requester_profile': requester_profile,
    }
    return render(request, 'accounts/profile.html', context)
