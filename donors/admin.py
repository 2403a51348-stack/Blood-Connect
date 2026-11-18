from django.contrib import admin
from .models import DonorProfile, DonationHistory


@admin.register(DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'blood_group', 'phone', 'city', 'state', 'is_available', 'total_donations', 'last_donation_date')
    list_filter = ('blood_group', 'is_available', 'state', 'city')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone', 'city')
    list_editable = ('is_available',)


@admin.register(DonationHistory)
class DonationHistoryAdmin(admin.ModelAdmin):
    list_display = ('donor', 'donation_date', 'units_donated', 'hospital_name', 'verified_by_hospital', 'created_at')
    list_filter = ('verified_by_hospital', 'donation_date')
    search_fields = ('donor__user__username', 'hospital_name')
