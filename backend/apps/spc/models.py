from django.db import models
from django.utils import timezone
from apps.aps.ai_llm_models import PredictiveModel


class Product(models.Model):
    """제품 정보"""
    product_code = models.CharField(max_length=50, unique=True)
    product_name = models.CharField(max_length=200)

    # 규격 정보
    usl = models.FloatField(help_text='Upper Specification Limit')
    lsl = models.FloatField(help_text='Lower Specification Limit')
    target_value = models.FloatField(null=True, blank=True)

    # 메타데이터
    unit = models.CharField(max_length=20, default='mm')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'spc_product'
        ordering = ['product_code']

    def __str__(self):
        return f"{self.product_code} - {self.product_name}"


class InspectionPlan(models.Model):
    """검사 계획"""
    FREQUENCY_CHOICES = [
        ('HOURLY', '시간당'),
        ('SHIFT', '교대당'),
        ('DAILY', '일일'),
        ('BATCH', '배치당'),
    ]

    SAMPLING_CHOICES = [
        ('ALL', '전수 검사'),
        ('RANDOM', '랜덤 샘플링'),
        ('PERIODIC', '주기적 샘플링'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inspection_plans')
    plan_name = models.CharField(max_length=200)

    # 검사 주기
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    sample_size = models.IntegerField(default=5)
    subgroup_size = models.IntegerField(default=5)
    sampling_method = models.CharField(max_length=20, choices=SAMPLING_CHOICES)

    # 검사 항목
    characteristic = models.CharField(max_length=100, help_text='검사 특성 (예: 직경, 무게)')
    measurement_method = models.TextField(blank=True)

    # 상태
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'spc_inspection_plan'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.plan_name} - {self.product.product_code}"


class QualityMeasurement(models.Model):
    """품질 측정 데이터"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='measurements')
    inspection_plan = models.ForeignKey(InspectionPlan, on_delete=models.SET_NULL, null=True, blank=True)

    # 측정 정보
    measurement_value = models.FloatField()
    sample_number = models.IntegerField(help_text='샘플 번호')
    subgroup_number = models.IntegerField(help_text='부분군 번호')

    # 측정 메타데이터
    measured_at = models.DateTimeField(default=timezone.now)
    measured_by = models.CharField(max_length=100)
    machine_id = models.CharField(max_length=50, blank=True)
    lot_number = models.CharField(max_length=50, blank=True)

    # 판정 결과
    is_within_spec = models.BooleanField(default=True)
    is_within_control = models.BooleanField(default=True)

    # 추가 정보
    remarks = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'spc_quality_measurement'
        ordering = ['-measured_at']
        indexes = [
            models.Index(fields=['product', 'measured_at']),
            models.Index(fields=['subgroup_number']),
        ]

    def __str__(self):
        return f"{self.product.product_code} - {self.measurement_value} ({self.measured_at})"


class ControlChart(models.Model):
    """관리도 설정 및 한계선"""
    CHART_TYPE_CHOICES = [
        ('XBAR_R', 'X-bar & R Chart'),
        ('XBAR_S', 'X-bar & S Chart'),
        ('I_MR', 'Individual & Moving Range Chart'),
        ('P_CHART', 'p-Chart (불량률)'),
        ('NP_CHART', 'np-Chart (불량수)'),
        ('C_CHART', 'c-Chart (결점수)'),
        ('U_CHART', 'u-Chart (단위당 결점수)'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='control_charts')
    inspection_plan = models.ForeignKey(InspectionPlan, on_delete=models.CASCADE, related_name='control_charts')

    # 관리도 타입
    chart_type = models.CharField(max_length=20, choices=CHART_TYPE_CHOICES)

    # X-bar Chart 한계선
    xbar_ucl = models.FloatField(null=True, blank=True, help_text='X-bar Upper Control Limit')
    xbar_cl = models.FloatField(null=True, blank=True, help_text='X-bar Center Line')
    xbar_lcl = models.FloatField(null=True, blank=True, help_text='X-bar Lower Control Limit')

    # R Chart 한계선
    r_ucl = models.FloatField(null=True, blank=True, help_text='R Upper Control Limit')
    r_cl = models.FloatField(null=True, blank=True, help_text='R Center Line')
    r_lcl = models.FloatField(null=True, blank=True, help_text='R Lower Control Limit')

    # S Chart 한계선
    s_ucl = models.FloatField(null=True, blank=True, help_text='S Upper Control Limit')
    s_cl = models.FloatField(null=True, blank=True, help_text='S Center Line')
    s_lcl = models.FloatField(null=True, blank=True, help_text='S Lower Control Limit')

    # p, np, c, u Chart 한계선
    p_ucl = models.FloatField(null=True, blank=True)
    p_cl = models.FloatField(null=True, blank=True)
    p_lcl = models.FloatField(null=True, blank=True)

    # 계산 정보
    subgroup_size = models.IntegerField(default=5)
    num_subgroups = models.IntegerField(default=25, help_text='한계선 계산에 사용된 부분군 수')
    calculated_at = models.DateTimeField(auto_now=True)

    # 상태
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'spc_control_chart'
        ordering = ['-created_at']
        unique_together = [['product', 'chart_type', 'is_active']]

    def __str__(self):
        return f"{self.product.product_code} - {self.chart_type}"


class ProcessCapability(models.Model):
    """공정능력 분석 결과"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='capabilities')
    control_chart = models.ForeignKey(ControlChart, on_delete=models.SET_NULL, null=True, blank=True)

    # 공정능력 지수
    cp = models.FloatField(help_text='Process Capability Index')
    cpk = models.FloatField(help_text='Process Capability Index (adjusted)')
    cpu = models.FloatField(help_text='Upper Capability Index')
    cpl = models.FloatField(help_text='Lower Capability Index')

    # 장기 공정능력 지수
    pp = models.FloatField(null=True, blank=True, help_text='Process Performance Index')
    ppk = models.FloatField(null=True, blank=True, help_text='Process Performance Index (adjusted)')

    # 통계 정보
    mean = models.FloatField()
    std_deviation = models.FloatField()
    sample_size = models.IntegerField()

    # 정규성 검정
    is_normal = models.BooleanField(default=True)
    normality_test_statistic = models.FloatField(null=True, blank=True)
    normality_test_p_value = models.FloatField(null=True, blank=True)

    # 분석 기간
    analysis_start = models.DateTimeField()
    analysis_end = models.DateTimeField()
    analyzed_at = models.DateTimeField(auto_now_add=True)

    # 추가 정보
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'spc_process_capability'
        ordering = ['-analyzed_at']

    def __str__(self):
        return f"{self.product.product_code} - Cp={self.cp:.2f}, Cpk={self.cpk:.2f}"


class RunRuleViolation(models.Model):
    """Run Rule 위반 기록"""
    RULE_CHOICES = [
        ('RULE_1', 'Rule 1: 관리 한계 벗어남'),
        ('RULE_2', 'Rule 2: 9개 연속 중심선 한쪽'),
        ('RULE_3', 'Rule 3: 6개 연속 증가/감소'),
        ('RULE_4', 'Rule 4: 14개 연속 교대 상승/하강'),
        ('RULE_5', 'Rule 5: 3개 중 2개가 2σ 벗어남'),
        ('RULE_6', 'Rule 6: 5개 중 4개가 1σ 벗어남'),
        ('RULE_7', 'Rule 7: 15개 연속 1σ 이내'),
        ('RULE_8', 'Rule 8: 8개 연속 1σ 벗어남'),
    ]

    control_chart = models.ForeignKey(ControlChart, on_delete=models.CASCADE, related_name='violations')
    measurement = models.ForeignKey(QualityMeasurement, on_delete=models.CASCADE, related_name='violations')

    # 위반 정보
    rule_type = models.CharField(max_length=20, choices=RULE_CHOICES)
    description = models.TextField()
    severity = models.IntegerField(default=1, help_text='1=낮음, 2=보통, 3=높음, 4=긴급')

    # 위반 데이터
    violation_data = models.JSONField(default=dict, help_text='위반 관련 데이터 (인덱스, 값 등)')

    # 처리 상태
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'spc_run_rule_violation'
        ordering = ['-detected_at']

    def __str__(self):
        return f"{self.rule_type} - {self.measurement.product.product_code}"


class QualityAlert(models.Model):
    """품질 경고"""
    ALERT_TYPE_CHOICES = [
        ('OUT_OF_SPEC', '규격 이탈'),
        ('OUT_OF_CONTROL', '관리 한계 이탈'),
        ('RUN_RULE', 'Run Rule 위반'),
        ('TREND', '트렌드 경고'),
        ('PREDICTION', 'AI 예측 경고'),
        ('CAPABILITY', '공정능력 저하'),
    ]

    PRIORITY_CHOICES = [
        (1, '낮음'),
        (2, '보통'),
        (3, '높음'),
        (4, '긴급'),
    ]

    STATUS_CHOICES = [
        ('NEW', '신규'),
        ('ACKNOWLEDGED', '확인됨'),
        ('INVESTIGATING', '조사중'),
        ('RESOLVED', '해결됨'),
        ('CLOSED', '종료됨'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='alerts')
    measurement = models.ForeignKey(QualityMeasurement, on_delete=models.SET_NULL, null=True, blank=True)
    violation = models.ForeignKey(RunRuleViolation, on_delete=models.SET_NULL, null=True, blank=True)

    # 경고 정보
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)

    # 상태 관리
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    assigned_to = models.CharField(max_length=100, blank=True)

    # 처리 정보
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.CharField(max_length=100, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.CharField(max_length=100, blank=True)
    resolution_notes = models.TextField(blank=True)

    # 근본 원인 분석
    root_cause = models.TextField(blank=True)
    corrective_action = models.TextField(blank=True)
    preventive_action = models.TextField(blank=True)

    # 메타데이터
    alert_data = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'spc_quality_alert'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['product', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title}"


class QualityReport(models.Model):
    """품질 보고서"""
    REPORT_TYPE_CHOICES = [
        ('DAILY', '일일 보고서'),
        ('WEEKLY', '주간 보고서'),
        ('MONTHLY', '월간 보고서'),
        ('CUSTOM', '사용자 정의'),
    ]

    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=200)

    # 보고서 기간
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    # 포함된 제품
    products = models.ManyToManyField(Product, related_name='reports')

    # 보고서 내용
    summary = models.TextField(blank=True)
    key_findings = models.JSONField(default=list, blank=True)
    recommendations = models.JSONField(default=list, blank=True)

    # 통계 요약
    total_measurements = models.IntegerField(default=0)
    out_of_spec_count = models.IntegerField(default=0)
    out_of_control_count = models.IntegerField(default=0)
    alert_count = models.IntegerField(default=0)

    # 보고서 파일
    report_file = models.CharField(max_length=500, blank=True, help_text='PDF/Excel 파일 경로')

    # 생성 정보
    generated_by = models.CharField(max_length=100)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'spc_quality_report'
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.title} ({self.start_date.date()} ~ {self.end_date.date()})"


# Import Six Sigma DMAIC Models - Temporarily disabled due to encoding issues
# from apps.spc.models_six_sigma import (
#     DMAICProject, DefinePhase, MeasurePhase, AnalyzePhase,
#     ImprovePhase, ControlPhase, DMAICMilestone, DMAICDocument,
#     DMAICRisk, StatisticalTool
# )

# Import Master Data Models
from apps.spc.models_master_data import (
    QualityItemMaster,
    QualityProcessMaster,
    QualityCharacteristicMaster,
    MeasurementInstrumentMaster,
    MeasurementSystemMaster,
    MeasurementSystemComponent,
    InspectionStandardMaster,
    QualitySyncLog
)

# Import Q-COST Models
from apps.spc.models_qcost import (
    OrganizationSite,
    OrganizationDepartment,
    QCostCategory,
    QCostItemMaster,
    QCostEntry,
    COPQSummary
)

# Import Inspection Models
from apps.spc.models_inspection import (
    ProductItem,
    ProcessFlow,
    ProcessStep,
    LotProduction,
    QCCharacteristic,
    SamplingRule,
    InspectionPlanNew,
    InspectionSpec,
    InspectionRun,
    InspectionResult,
    DefectCode,
    GageMaster
)

# Import Enhanced SPC Models
from apps.spc.models_spc import (
    SPCChartDefinition,
    SPCChartPoint,
    SPCEvent
)

# Import QA Models
from apps.spc.models_qa import (
    QAProcess,
    QARequirement,
    QAAssessment,
    QAGapFinding,
    CAPACase,
    ChangeControl,
    DocFile,
    AIOutput
)

