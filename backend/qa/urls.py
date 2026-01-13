"""
QA URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    path('processes', views.get_qa_processes, name='qa-processes'),
    path('processes/create', views.create_qa_process, name='qa-process-create'),
    path('processes/<str:qa_process_id>/checklist', views.get_qa_checklist_items, name='qa-checklist-items'),
    path('processes/<str:qa_process_id>/checklist/create', views.create_qa_checklist_item, name='qa-checklist-create'),
    path('processes/<str:qa_process_id>/assessments', views.get_qa_assessments, name='qa-assessments'),
    path('processes/<str:qa_process_id>/assessments/create', views.create_qa_assessment, name='qa-assessment-create'),
    path('processes/<str:qa_process_id>/findings', views.get_qa_findings, name='qa-findings'),
    path('processes/<str:qa_process_id>/findings/create', views.create_qa_finding, name='qa-finding-create'),
    path('capas', views.get_capas, name='qa-capas'),
    path('capas/create', views.create_capa, name='qa-capa-create'),
    path('capas/<str:capa_id>/actions', views.get_capa_actions, name='qa-capa-actions'),
    path('capas/<str:capa_id>/actions/create', views.create_capa_action, name='qa-capa-action-create'),
    path('ai/root-cause', views.analyze_root_cause, name='qa-ai-root-cause'),
]
