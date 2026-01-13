"""
SPC URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    path('sampling/rules', views.get_sampling_rule, name='spc-sampling-rule'),
    path('charts', views.create_chart, name='spc-chart-create'),
    path('charts/<str:chart_def_id>/recalc', views.recalc_chart, name='spc-chart-recalc'),
    path('charts/<str:chart_def_id>/points', views.get_points, name='spc-points'),
    path('events', views.create_event, name='spc-event-create'),
]
