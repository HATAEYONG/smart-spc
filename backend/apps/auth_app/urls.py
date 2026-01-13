"""
Authentication URLs
"""
from django.urls import path
from . import views

urlpatterns = [
    # JWT Authentication Endpoints
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('refresh/', views.RefreshView.as_view(), name='refresh'),
    path('verify/', views.VerifyView.as_view(), name='verify'),
    path('me/', views.MeView.as_view(), name='me'),
]
