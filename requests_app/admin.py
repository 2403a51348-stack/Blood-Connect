from django.contrib import admin
from .models import RequesterProfile, BloodRequest


@admin.register(RequesterProfile)
class RequesterProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'state', 'organization_name', 'created_at')
    list_filter = ('state', 'city')
    search_fields = ('user__username', 'phone', 'city', 'organization_name')


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'patient_name', 'blood_group', 'units_required', 'hospital_name', 'city', 'urgency', 'status', 'created_at')
    list_filter = ('blood_group', 'urgency', 'status', 'city', 'created_at')
    search_fields = ('request_id', 'patient_name', 'hospital_name', 'contact_name', 'contact_phone')
    list_editable = ('status', 'urgency')
