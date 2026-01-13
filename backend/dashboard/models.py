"""
Dashboard Models - DASH-01
"""
from django.db import models


class DashboardKPI(models.Model):
    """KPI 저장 모델"""
    period = models.CharField(max_length=7, help_text="기간 (YYYY-MM)")
    copq_rate = models.FloatField(help_text="COPQ 비율")
    total_copq = models.IntegerField(help_text="총 COPQ 금액")
    total_qcost = models.IntegerField(help_text="총 품질 비용")
    oos_count = models.IntegerField(help_text="OOS 발생 횟수")
    spc_open_events = models.IntegerField(help_text="SPC 오픈 이벤트 수")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dashboard_kpi'
        verbose_name = 'Dashboard KPI'
        verbose_name_plural = 'Dashboard KPIs'
        ordering = ['-period']

    def __str__(self):
        return f"KPI {self.period}"


class TopDefect(models.Model):
    """상위 불항 현황 모델"""
    period = models.CharField(max_length=7, help_text="기간 (YYYY-MM)")
    defect = models.CharField(max_length=100, help_text="불량 유형")
    count = models.IntegerField(help_text="발생 횟수")
    cost = models.IntegerField(help_text="불량 비용")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'top_defect'
        verbose_name = 'Top Defect'
        verbose_name_plural = 'Top Defects'
        ordering = ['-period', '-count']

    def __str__(self):
        return f"{self.period} - {self.defect}"


class Alert(models.Model):
    """알림 모델"""
    event_id = models.CharField(max_length=50, unique=True, help_text="이벤트 ID")
    type = models.CharField(max_length=20, help_text="알림 유형")
    severity = models.IntegerField(help_text="심각도 (1-5)")
    title = models.CharField(max_length=200, help_text="알림 제목")
    description = models.TextField(blank=True, help_text="상세 설명")
    status = models.CharField(max_length=20, default='OPEN', help_text="상태 (OPEN/INVESTIGATING/CLOSED)")
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'alert'
        verbose_name = 'Alert'
        verbose_name_plural = 'Alerts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type} - {self.title}"


class AIInsight(models.Model):
    """AI 인사이트 모델"""
    ai_id = models.CharField(max_length=50, unique=True, help_text="AI 인사이트 ID")
    period = models.CharField(max_length=7, help_text="기간 (YYYY-MM)")
    title = models.CharField(max_length=200, help_text="인사이트 제목")
    summary = models.TextField(help_text="인사이트 요약")
    confidence = models.FloatField(help_text="신뢰도 (0-1)")
    insight_type = models.CharField(max_length=20, help_text="인사이트 유형 (PREDICTION/ANOMALY/OPTIMIZATION/RISK)")
    actionable = models.BooleanField(default=True, help_text="실행 가능 여부")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_insight'
        verbose_name = 'AI Insight'
        verbose_name_plural = 'AI Insights'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ai_id} - {self.title}"
