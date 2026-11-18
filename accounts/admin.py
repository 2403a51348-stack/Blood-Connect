from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'city', 'state', 'is_verified', 'created_at')
    list_filter = ('role', 'state', 'city', 'is_verified')
    search_fields = ('user__username', 'user__email', 'phone', 'city')
