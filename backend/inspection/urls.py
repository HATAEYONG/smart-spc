"""
Inspection URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    path('flows', views.get_flows, name='inspection-flows'),
    path('flows/create', views.create_flow, name='inspection-flow-create'),
    path('flows/<str:flow_id>/steps', views.get_steps, name='inspection-steps'),
    path('flows/<str:flow_id>/steps/create', views.create_step, name='inspection-step-create'),
    path('ai/process-design', views.design_process, name='inspection-ai-process-design'),
    path('ai/criteria-checklist', views.generate_criteria_checklist, name='inspection-ai-checklist'),
    path('runs', views.create_run, name='inspection-run-create'),
    path('runs/<str:run_id>/results/bulk', views.add_bulk_results, name='inspection-bulk-results'),
    path('runs/<str:run_id>/judge', views.judge_run, name='inspection-judge'),
]
