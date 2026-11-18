from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as account_views

urlpatterns = [
    # Built-in Django Admin
    path('admin/', admin.site.urls),

    # Core Informational & Marketing Pages
    path('', include('core.urls')),

    # User Authentication & Role Management
    path('accounts/', include('accounts.urls')),
    path('login/', account_views.user_login, name='login'),
    path('logout/', account_views.user_logout, name='logout'),

    # Donor Operations
    path('donor/', include('donors.urls')),

    # Blood Request Operations
    path('requests/', include('requests_app.urls')),

    # Donor Matching & Responses
    path('matching/', include('matching.urls')),

    # Notifications System
    path('notifications/', include('notifications.urls')),

    # Administrator Operations
    path('admin-dashboard/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
