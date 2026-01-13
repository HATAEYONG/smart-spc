"""
Dashboard URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    path('summary', views.get_dashboard_summary, name='dashboard-summary'),
]
