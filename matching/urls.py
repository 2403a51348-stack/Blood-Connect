from django.urls import path
from . import views

urlpatterns = [
    path('<int:request_id>/matches/', views.matching_results, name='matching_results'),
    path('contact/<int:match_id>/', views.contact_donor, name='contact_donor'),
    path('<int:request_id>/contact-all/', views.contact_all_donors, name='contact_all_donors'),
    path('respond/<int:match_id>/', views.respond_to_request, name='respond_request'),
]
