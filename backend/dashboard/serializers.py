"""
Dashboard Serializers
Convert Pydantic schemas to Django REST Framework Serializers
"""
from rest_framework import serializers


class KPIsSerializer(serializers.Serializer):
    """KPIs Data Transfer Object"""
    copq_rate = serializers.FloatField(help_text="COPQ 비율")
    total_copq = serializers.IntegerField(help_text="총 COPQ 금액")
    total_qcost = serializers.IntegerField(help_text="총 품질 비용")
    oos_count = serializers.IntegerField(help_text="OOS 발생 횟수")
    spc_open_events = serializers.IntegerField(help_text="SPC 오픈 이벤트 수")


class TopDefectSerializer(serializers.Serializer):
    """Top Defect Data Transfer Object"""
    defect = serializers.CharField(help_text="불량 유형")
    count = serializers.IntegerField(help_text="발생 횟수")
    cost = serializers.IntegerField(help_text="불량 비용")


class AlertSerializer(serializers.Serializer):
    """Alert Data Transfer Object"""
    event_id = serializers.CharField(help_text="이벤트 ID")
    type = serializers.CharField(help_text="알림 유형 (TREND, OOS, RULE_1, etc.)")
    severity = serializers.IntegerField(help_text="심각도 (1-5)")
    title = serializers.CharField(help_text="알림 제목")


class AIInsightSerializer(serializers.Serializer):
    """AI Insight Data Transfer Object"""
    ai_id = serializers.CharField(help_text="AI 인사이트 ID")
    title = serializers.CharField(help_text="인사이트 제목")
    summary = serializers.CharField(help_text="인사이트 요약")
    confidence = serializers.FloatField(help_text="신뢰도 (0-1)")


class DashboardSummarySerializer(serializers.Serializer):
    """Dashboard Summary Data Transfer Object"""
    period = serializers.CharField(help_text="기간 (YYYY-MM)")
    kpis = KPIsSerializer(help_text="KPI 지표들")
    top_defects = TopDefectSerializer(many=True, help_text="상위 불량 현황")
    alerts = AlertSerializer(many=True, help_text="알림 목록")
    ai_insights = AIInsightSerializer(many=True, help_text="AI 인사이트 목록")
