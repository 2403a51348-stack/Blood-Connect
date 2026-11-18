from django.contrib import admin
from .models import AdminActivityLog


@admin.register(AdminActivityLog)
class AdminActivityLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'admin_user', 'action_type', 'target_model', 'target_id')
    list_filter = ('action_type', 'target_model', 'timestamp')
    search_fields = ('admin_user__username', 'description', 'action_type')
    readonly_fields = ('admin_user', 'action_type', 'description', 'target_model', 'target_id', 'ip_address', 'timestamp')
