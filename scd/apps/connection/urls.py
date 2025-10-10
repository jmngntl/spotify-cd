from django.urls import path
from . import views

urlpatterns = [
    path('', views.authenticate, name='authenticate'),
    path('redirect/', views.auth_redirect, name='auth_redirect'),
]