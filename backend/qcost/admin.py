"""
Q-COST Admin Configuration
"""
from django.contrib import admin
from .models import QCostCategory, QCostItem, QCostEntry, AIClassificationHistory


@admin.register(QCostCategory)
class QCostCategoryAdmin(admin.ModelAdmin):
    list_display = ['category_id', 'category_type', 'name', 'is_active', 'created_at']
    list_filter = ['category_type', 'is_active', 'created_at']
    search_fields = ['category_id', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(QCostItem)
class QCostItemAdmin(admin.ModelAdmin):
    list_display = ['item_id', 'category', 'code', 'name', 'unit', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['item_id', 'code', 'name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(QCostEntry)
class QCostEntryAdmin(admin.ModelAdmin):
    list_display = ['entry_id', 'item', 'occurred_at', 'quantity', 'unit_cost', 'total_cost']
    list_filter = ['item', 'occurred_at']
    search_fields = ['entry_id', 'reference_id', 'notes']
    readonly_fields = ['created_at']


@admin.register(AIClassificationHistory)
class AIClassificationHistoryAdmin(admin.ModelAdmin):
    list_display = ['classification_id', 'amount', 'suggested_category', 'confidence', 'is_applied', 'created_at']
    list_filter = ['suggested_category', 'is_applied', 'created_at']
    search_fields = ['classification_id', 'description', 'reasoning']
    readonly_fields = ['created_at']
