from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('donors/', views.manage_donors, name='manage_donors'),
    path('requesters/', views.manage_requesters, name='manage_requesters'),
    path('requests/', views.manage_requests, name='manage_requests'),
    path('users/<int:user_id>/toggle-active/', views.toggle_user_active, name='toggle_user_active'),
    path('requests/<int:request_id>/update-status/', views.update_request_status_admin, name='update_request_status_admin'),
    path('logs/', views.activity_logs_view, name='activity_logs'),
]
