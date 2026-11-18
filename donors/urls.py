from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('toggle-availability/', views.toggle_availability, name='toggle_availability'),
    path('history/', views.donation_history_list, name='donor_history'),
    path('history/add/', views.add_donation_record, name='add_donation_record'),
]
