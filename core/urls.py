from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about_us, name='about'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('contact/', views.contact_us, name='contact'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('terms/', views.terms_and_conditions, name='terms'),
]
