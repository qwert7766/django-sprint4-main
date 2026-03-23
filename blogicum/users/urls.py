from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('edit/', views.edit_profile, name='edit_profile'),
]