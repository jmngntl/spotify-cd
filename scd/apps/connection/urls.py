from django.urls import path
from . import views

urlpatterns = [
    path('redirect/', views.auth_redirect, name='auth_redirect'),
]