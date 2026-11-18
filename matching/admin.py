from django.contrib import admin
from .models import DonorMatch, DonationResponse


@admin.register(DonorMatch)
class DonorMatchAdmin(admin.ModelAdmin):
    list_display = ('blood_request', 'donor', 'match_score', 'status', 'contacted_at', 'responded_at', 'created_at')
    list_filter = ('status', 'match_score', 'created_at')
    search_fields = ('blood_request__request_id', 'donor__user__username')


@admin.register(DonationResponse)
class DonationResponseAdmin(admin.ModelAdmin):
    list_display = ('donor', 'blood_request', 'response', 'responded_at')
    list_filter = ('response', 'responded_at')
    search_fields = ('donor__user__username', 'blood_request__request_id')
