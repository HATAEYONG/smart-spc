"""
SPC Models - SPC-01
"""
from django.db import models


class SamplingRule(models.Model):
    """표본 추출 규칙 모델"""
    STANDARD_CHOICES = [
        ('MIL-STD-105E', 'MIL-STD-105E'),
        ('ISO-2859-1', 'ISO 2859-1'),
        ('ISO-2859-2', 'ISO 2859-2'),
        ('ANSI-ASQ-Z1.4', 'ANSI/ASQ Z1.4'),
    ]

    rule_id = models.CharField(max_length=50, unique=True, help_text="규칙 ID")
    standard = models.CharField(max_length=20, choices=STANDARD_CHOICES, help_text="표준")
    aql = models.FloatField(help_text="AQL 수준")
    lot_size_from = models.IntegerField(help_text="로트 크기 시작")
    lot_size_to = models.IntegerField(help_text="로트 크기 종료")
    sample_size = models.IntegerField(help_text="표본 크기")
    accept_limit = models.IntegerField(help_text="합격 판정 개수")
    reject_limit = models.IntegerField(help_text="불합격 판정 개수")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sampling_rule'
        verbose_name = 'Sampling Rule'
        verbose_name_plural = 'Sampling Rules'
        ordering = ['standard', 'lot_size_from']

    def __str__(self):
        return f"{self.standard} - AQL {self.aql}"


class SpcChartDefinition(models.Model):
    """SPC 관리도 정의 모델"""
    CHART_TYPES = [
        ('XBAR_R', 'X-bar R 관리도'),
        ('XBAR_S', 'X-bar S 관리도'),
        ('I_MR', 'I-MR 관리도'),
        ('P', 'P 관리도'),
        ('NP', 'NP 관리도'),
        ('U', 'U 관리도'),
        ('C', 'C 관리도'),
    ]

    chart_def_id = models.CharField(max_length=50, unique=True, help_text="관리도 정의 ID")
    parameter_id = models.CharField(max_length=50, help_text="파라미터 ID")
    chart_type = models.CharField(max_length=10, choices=CHART_TYPES, help_text="관리도 종류")
    sample_size = models.IntegerField(help_text="표본 크기 (n)")
    ucl = models.FloatField(null=True, blank=True, help_text="상한 (UCL)")
    cl = models.FloatField(null=True, blank=True, help_text="중심선 (CL)")
    lcl = models.FloatField(null=True, blank=True, help_text="하한 (LCL)")
    is_active = models.BooleanField(default=True, help_text="활성화 여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'spc_chart_definition'
        verbose_name = 'SPC Chart Definition'
        verbose_name_plural = 'SPC Chart Definitions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.chart_def_id} - {self.chart_type}"


class SpcPoint(models.Model):
    """SPC 측정 포인트 모델"""
    point_id = models.CharField(max_length=50, unique=True, help_text="포인트 ID")
    chart_def = models.ForeignKey(SpcChartDefinition, on_delete=models.CASCADE, related_name='points', help_text="관리도 정의")
    timestamp = models.DateTimeField(help_text="측정일시")
    sample_id = models.CharField(max_length=50, help_text="표본 ID")
    value = models.FloatField(help_text="측정값")
    mean = models.FloatField(null=True, blank=True, help_text="평균 (Xbar)")
    range_val = models.FloatField(null=True, blank=True, help_text="범위 (R)")
    std_dev = models.FloatField(null=True, blank=True, help_text="표준편차 (S)")
    violated_rules = models.JSONField(blank=True, null=True, help_text="위반 규칙 목록 (JSON)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'spc_point'
        verbose_name = 'SPC Point'
        verbose_name_plural = 'SPC Points'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.point_id} - {self.value}"


class SpcEvent(models.Model):
    """SPC 이벤트 모델"""
    EVENT_TYPES = [
        ('OOS', '규격 이탈'),
        ('RULE_1', 'Rule 1: 1점이 3σ 벗어남'),
        ('RULE_2', 'Rule 2: 연속 3점 중 2점이 2σ 벗어남'),
        ('RULE_3', 'Rule 3: 연속 5점 중 4점이 1σ 벗어남'),
        ('RULE_4', 'Rule 4: 연속 8점이 중심선同一편'),
        ('RULE_5', 'Rule 5: 연속 6점이 단조 증가/감소'),
        ('RULE_6', 'Rule 6: 연속 14점이 교차'),
        ('RULE_7', 'Rule 7: 연속 15점이 1σ 내'),
        ('RULE_8', 'Rule 8: 연속 8점이 1σ 밖'),
        ('TREND', '추세 이상'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('INVESTIGATING', 'Investigating'),
        ('CLOSED', 'Closed'),
    ]

    event_id = models.CharField(max_length=50, unique=True, help_text="이벤트 ID")
    chart_def = models.ForeignKey(SpcChartDefinition, on_delete=models.CASCADE, related_name='events', help_text="관리도 정의")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, help_text="이벤트 유형")
    triggered_at = models.DateTimeField(help_text="발생일시")
    description = models.TextField(help_text="설명")
    severity = models.IntegerField(help_text="심각도 (1-5)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN', help_text="상태")
    assigned_to = models.CharField(max_length=50, blank=True, help_text="담당자")
    resolved_at = models.DateTimeField(null=True, blank=True, help_text="해결일시")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'spc_event'
        verbose_name = 'SPC Event'
        verbose_name_plural = 'SPC Events'
        ordering = ['-triggered_at']

    def __str__(self):
        return f"{self.event_id} - {self.event_type}"
