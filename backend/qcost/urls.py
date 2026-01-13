"""
Q-COST URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    path('categories', views.get_qcost_categories, name='qcost-categories'),
    path('categories/create', views.create_qcost_category, name='qcost-category-create'),
    path('items', views.get_qcost_items, name='qcost-items'),
    path('items/create', views.create_qcost_item, name='qcost-item-create'),
    path('entries', views.get_qcost_entries, name='qcost-entries'),
    path('entries/create', views.create_qcost_entry, name='qcost-entry-create'),
    path('ai/qcost-classify', views.classify_qcost, name='qcost-ai-classify'),
    path('reports/copq', views.generate_copq_report, name='qcost-copq-report'),
]
