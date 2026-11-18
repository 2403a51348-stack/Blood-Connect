from django.urls import path
from . import views

urlpatterns = [
    path('register/donor/', views.donor_register, name='register_donor'),
    path('register/requester/', views.requester_register, name='register_requester'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile_management, name='profile'),
]
