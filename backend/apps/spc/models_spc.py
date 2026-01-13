"""
SPC (Statistical Process Control) Enhanced Models
관리도 및 SPC 이벤트 관리를 위한 Django 모델
ERD 1-3: 관리도(SPC) 도메인
"""

from django.db import models
from django.utils import timezone
from apps.spc.models_qcost import OrganizationSite
from apps.spc.models_inspection import ProductItem, QCCharacteristic, InspectionRun


class SPCChartDefinition(models.Model):
    """관리도 정의 (spc_chart_def)"""
    CHART_TYPE_CHOICES = [
        ('XBAR_R', 'X-bar & R Chart'),
        ('XBAR_S', 'X-bar & S Chart'),
        ('I_MR', 'Individual & Moving Range Chart'),
        ('P', 'p-Chart'),
        ('NP', 'np-Chart'),
        ('C', 'c-Chart'),
        ('U', 'u-Chart'),
    ]

    CALC_METHOD_CHOICES = [
        ('STANDARD', '표준 방법'),
        ('ROBUST', 'Robust 방법'),
    ]

    chart_def_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='spc_charts')
    char = models.ForeignKey(QCCharacteristic, on_delete=models.CASCADE, related_name='spc_charts')

    chart_type = models.CharField(max_length=20, choices=CHART_TYPE_CHOICES)
    calc_method = models.CharField(max_length=20, choices=CALC_METHOD_CHOICES, default='STANDARD')

    # 부분군 설정
    subgroup_size = models.IntegerField(default=5)

    # 규칙 세트 (JSON: WECO/NELSON/Custom)
    rule_set = models.JSONField(default=dict, help_text='적용할 WECO Rules 등')

    # 기준 기간
    baseline_from_dt = models.DateTimeField(help_text='기준 기간 시작')
    baseline_to_dt = models.DateTimeField(help_text='기준 기간 종료')

    # 계산된 관리한계
    ucl = models.FloatField(null=True, blank=True, help_text='상한관리선')
    cl = models.FloatField(null=True, blank=True, help_text='중심선')
    lcl = models.FloatField(null=True, blank=True, help_text='하한관리선')

    # 공정능력
    cp = models.FloatField(null=True, blank=True)
    cpk = models.FloatField(null=True, blank=True)

    status = models.CharField(max_length=20, default='ACTIVE')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'spc_chart_def'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.char.char_name} - {self.chart_type}"


class SPCChartPoint(models.Model):
    """관리도 점/통계 (spc_chart_point)"""
    point_id = models.AutoField(primary_key=True)
    chart_def = models.ForeignKey(SPCChartDefinition, on_delete=models.CASCADE, related_name='points')
    run = models.ForeignKey(InspectionRun, on_delete=models.SET_NULL, null=True, related_name='spc_points')

    point_dt = models.DateTimeField(default=timezone.now)

    # 통계량
    n = models.IntegerField(help_text='샘플 수')
    xbar = models.FloatField(null=True, blank=True, help_text='평균')
    r = models.FloatField(null=True, blank=True, help_text='범위')
    s = models.FloatField(null=True, blank=True, help_text='표준편차')
    mr = models.FloatField(null=True, blank=True, help_text='이동 범위')
    p = models.FloatField(null=True, blank=True, help_text='불합격률')
    np = models.FloatField(null=True, blank=True, help_text='불합격수')
    c = models.FloatField(null=True, blank=True, help_text='결점수')
    u = models.FloatField(null=True, blank=True, help_text='단위당 결점수')

    # 관리한계 (점별로 다를 수 있음)
    ucl = models.FloatField(null=True, blank=True)
    cl = models.FloatField(null=True, blank=True)
    lcl = models.FloatField(null=True, blank=True)

    # 공정능력 (점별)
    cp = models.FloatField(null=True, blank=True)
    cpk = models.FloatField(null=True, blank=True)

    # 위반 여부
    is_violation = models.BooleanField(default=False)
    violation_codes = models.JSONField(default=list, help_text='위반한 규칙 리스트')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'spc_chart_point'
        ordering = ['-point_dt']
        indexes = [
            models.Index(fields=['chart_def', 'point_dt']),
        ]

    def __str__(self):
        return f"Point {self.point_id} - Xbar={self.xbar}"


class SPCEvent(models.Model):
    """SPC 이상/경보 (spc_event)"""
    EVENT_TYPE_CHOICES = [
        ('OOS', 'Out of Spec'),
        ('RULE_VIOLATION', 'Rule Violation'),
        ('SHIFT', 'Shift Change'),
        ('TREND', 'Trend'),
    ]

    SEVERITY_CHOICES = [
        ('LOW', '낮음'),
        ('MEDIUM', '보통'),
        ('HIGH', '높음'),
        ('CRITICAL', '긴급'),
    ]

    STATUS_CHOICES = [
        ('OPEN', '미해결'),
        ('ACK', '확인됨'),
        ('INVESTIGATING', '조사중'),
        ('CLOSED', '종료'),
    ]

    event_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='spc_events')
    chart_def = models.ForeignKey(SPCChartDefinition, on_delete=models.CASCADE, related_name='events')
    point = models.ForeignKey(SPCChartPoint, on_delete=models.CASCADE, related_name='events')

    event_dt = models.DateTimeField(default=timezone.now)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)

    description = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')

    # 담당자
    owner_user_id = models.IntegerField(help_text='담당자 ID')

    # AI 근본원인 분석 연계
    ai_rootcause_id = models.IntegerField(null=True, blank=True)
    ai_analysis = models.JSONField(null=True, blank=True, help_text='AI 분석 결과')

    # 조치 내용
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.IntegerField(null=True, blank=True)

    root_cause = models.TextField(blank=True)
    corrective_action = models.TextField(blank=True)
    preventive_action = models.TextField(blank=True)

    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'spc_event'
        ordering = ['-event_dt']
        indexes = [
            models.Index(fields=['site', 'status']),
            models.Index(fields=['event_dt']),
        ]

    def __str__(self):
        return f"[{self.severity}] {self.event_type} - {self.event_dt}"
