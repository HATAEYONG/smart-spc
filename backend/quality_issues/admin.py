from django.contrib import admin
from .models import QualityIssue, IssueAnalysis4M, ProblemSolvingStep


@admin.register(QualityIssue)
class QualityIssueAdmin(admin.ModelAdmin):
    list_display = ['issue_number', 'title', 'severity', 'status', 'department', 'reported_date']
    list_filter = ['severity', 'status', 'department', 'reported_date']
    search_fields = ['issue_number', 'title', 'product_code', 'product_name', 'defect_type']
    readonly_fields = ['reported_date', 'created_at', 'updated_at']
    date_hierarchy = 'reported_date'


@admin.register(IssueAnalysis4M)
class IssueAnalysis4MAdmin(admin.ModelAdmin):
    list_display = ['issue', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['issue__issue_number', 'description']


@admin.register(ProblemSolvingStep)
class ProblemSolvingStepAdmin(admin.ModelAdmin):
    list_display = ['issue', 'step_number', 'step_name', 'completed', 'completed_at']
    list_filter = ['completed', 'step_number']
    search_fields = ['issue__issue_number', 'step_name', 'content']
