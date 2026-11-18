from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.requester_dashboard, name='requester_dashboard'),
    path('create/', views.create_blood_request, name='create_blood_request'),
    path('tracking/', views.all_requests_tracking, name='requests_tracking'),
    path('<int:request_id>/track/', views.track_request, name='track_request'),
    path('<int:request_id>/cancel/', views.cancel_request, name='cancel_request'),
    path('<int:request_id>/complete/', views.complete_request, name='complete_request'),
]
