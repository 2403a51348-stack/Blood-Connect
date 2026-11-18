from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def donor_required(view_func):
    """
    Decorator for views that checks if the logged-in user is a registered Donor.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to access this page.')
            return redirect('login')
        
        # Check donor profile existence or role
        if hasattr(request.user, 'donor_profile') or (hasattr(request.user, 'profile') and request.user.profile.role == 'DONOR'):
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Access restricted to registered Blood Donors.')
        return redirect('home')
    return _wrapped_view


def requester_required(view_func):
    """
    Decorator for views that checks if the logged-in user is a registered Blood Requester.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to access this page.')
            return redirect('login')
        
        if hasattr(request.user, 'requester_profile') or (hasattr(request.user, 'profile') and request.user.profile.role == 'REQUESTER'):
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Access restricted to registered Blood Requesters.')
        return redirect('home')
    return _wrapped_view


def admin_required(view_func):
    """
    Decorator for views that checks if the logged-in user is an Administrator or Staff.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in with administrator credentials.')
            return redirect('login')
        
        if request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN'):
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Administrator privileges required to access this page.')
        return redirect('home')
    return _wrapped_view
