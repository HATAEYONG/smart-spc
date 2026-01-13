from django.contrib import admin
from .models import APSEvent, APSDecisionLog, APSDepEdge, StageFactPlanOut


@admin.register(APSEvent)
class APSEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'event_type', 'mc_cd', 'wo_no', 'event_ts']
    list_filter = ['event_type', 'mc_cd']
    search_fields = ['wo_no', 'mc_cd', 'itm_id']
    ordering = ['-event_ts']


@admin.register(APSDecisionLog)
class APSDecisionLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'decision', 'mc_cd', 'scope_size', 'created_ts']
    list_filter = ['decision', 'mc_cd']
    ordering = ['-created_ts']


@admin.register(APSDepEdge)
class APSDepEdgeAdmin(admin.ModelAdmin):
    list_display = ['id', 'src_wo_no', 'dst_wo_no', 'edge_type', 'edge_weight']
    list_filter = ['edge_type']
    search_fields = ['src_wo_no', 'dst_wo_no']


@admin.register(StageFactPlanOut)
class StageFactPlanOutAdmin(admin.ModelAdmin):
    list_display = ['wo_no', 'mc_cd', 'itm_id', 'fr_ts', 'to_ts', 'freeze_level']
    list_filter = ['mc_cd', 'locked_yn', 'freeze_level']
    search_fields = ['wo_no', 'itm_id']
    ordering = ['fr_ts']
