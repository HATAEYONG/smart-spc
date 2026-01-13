"""
Inspection Models
검수 프로세스를 위한 Django 모델
ERD 1-2: 검사(Inspection) 도메인
"""

from django.db import models
from django.utils import timezone
from apps.spc.models_qcost import OrganizationSite


class ProductItem(models.Model):
    """품목 마스터 (product_item)"""
    item_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='product_items')

    item_code = models.CharField(max_length=50)
    item_name = models.CharField(max_length=200)
    spec_version = models.CharField(max_length=20, default='A0')
    uom = models.CharField(max_length=20, help_text='단위 (mm, kg, etc)')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_item'
        ordering = ['item_code']
        unique_together = [['site', 'item_code']]

    def __str__(self):
        return f"{self.item_code} - {self.item_name}"


class ProcessFlow(models.Model):
    """공정 흐름 (process_flow)"""
    STATUS_CHOICES = [
        ('DRAFT', '초안'),
        ('ACTIVE', '활성'),
        ('OBSOLETE', '폐기'),
    ]

    flow_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='process_flows')

    flow_name = models.CharField(max_length=200)
    rev_no = models.CharField(max_length=20)  # 리비전 번호
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'process_flow'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.flow_name} Rev.{self.rev_no}"


class ProcessStep(models.Model):
    """공정 단계 (process_step)"""
    step_id = models.AutoField(primary_key=True)
    flow = models.ForeignKey(ProcessFlow, on_delete=models.CASCADE, related_name='steps')

    seq_no = models.IntegerField(help_text='순서')
    step_name = models.CharField(max_length=100)
    workcenter = models.CharField(max_length=100, blank=True)
    machine_group = models.CharField(max_length=100, blank=True)

    is_inspection_point = models.BooleanField(default=False, help_text='검사 지점 여부')

    class Meta:
        db_table = 'process_step'
        ordering = ['flow', 'seq_no']
        unique_together = [['flow', 'seq_no']]

    def __str__(self):
        return f"{self.seq_no}. {self.step_name}"


class LotProduction(models.Model):
    """생산 LOT (lot_production)"""
    lot_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='production_lots')
    item = models.ForeignKey(ProductItem, on_delete=models.PROTECT, related_name='production_lots')
    flow = models.ForeignKey(ProcessFlow, on_delete=models.PROTECT, related_name='production_lots')

    lot_no = models.CharField(max_length=50, unique=True)
    qty = models.DecimalField(max_digits=15, decimal_places=2)
    start_dt = models.DateTimeField()
    end_dt = models.DateTimeField(null=True, blank=True)
    shift = models.CharField(max_length=20)  # 교대조
    operator_id = models.IntegerField(null=True, blank=True)

    status = models.CharField(max_length=20, default='IN_PROGRESS')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lot_production'
        ordering = ['-start_dt']

    def __str__(self):
        return f"{self.lot_no} - {self.item.item_code}"


class QCCharacteristic(models.Model):
    """품질특성/CTQ (qc_characteristic)"""
    CHAR_TYPE_CHOICES = [
        ('DIM', '치수 특성'),
        ('ATTR', '속성 특성'),
        ('SENSORY', '관능 특성'),
    ]

    CRITICALITY_CHOICES = [
        ('C', 'Critical'),
        ('A', 'A'),
        ('B', 'B'),
    ]

    char_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='characteristics')
    item = models.ForeignKey(ProductItem, on_delete=models.CASCADE, related_name='characteristics', null=True, blank=True)
    step = models.ForeignKey(ProcessStep, on_delete=models.CASCADE, related_name='characteristics', null=True, blank=True)

    char_name = models.CharField(max_length=100)
    char_type = models.CharField(max_length=20, choices=CHAR_TYPE_CHOICES)
    unit = models.CharField(max_length=20, blank=True)

    # 규격
    target = models.FloatField(null=True, blank=True)
    lsl = models.FloatField(null=True, blank=True, help_text='하한규격')
    usl = models.FloatField(null=True, blank=True, help_text='상한규격')

    criticality = models.CharField(max_length=10, choices=CRITICALITY_CHOICES, default='B')

    # 템플릿 여부 (공통 템플릿으로 사용 가능)
    is_template = models.BooleanField(default=False, help_text='공통 템플릿 여부')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'qc_characteristic'
        ordering = ['item', 'step', 'char_name']

    def __str__(self):
        return f"{self.char_name} ({self.get_char_type_display()})"


class SamplingRule(models.Model):
    """샘플링 규칙 (sampling_rule)"""
    STANDARD_CHOICES = [
        ('ISO2859', 'ISO 2859-1'),
        ('ANSI_Z1_4', 'ANSI/ASQ Z1.4'),
        ('INHOUSE', '사내 규격'),
    ]

    sample_rule_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='sampling_rules')

    rule_name = models.CharField(max_length=100)
    standard = models.CharField(max_length=20, choices=STANDARD_CHOICES)

    aql = models.FloatField(help_text='Acceptable Quality Level')
    inspection_level = models.CharField(max_length=20, default='II')  # 일반 검사 수준 II

    lot_size_min = models.IntegerField(null=True, blank=True)
    lot_size_max = models.IntegerField(null=True, blank=True)

    sample_size = models.IntegerField(help_text='샘플 크기')
    accept_num = models.IntegerField(help_text='합격 판정 수')
    reject_num = models.IntegerField(help_text='불합격 판정 수')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sampling_rule'
        ordering = ['rule_name']

    def __str__(self):
        return f"{self.rule_name} (AQL {self.aql}%)"


class InspectionPlanNew(models.Model):
    """검사 계획 (inspection_plan)"""
    INSPECTION_TYPE_CHOICES = [
        ('ALL', '전수 검사'),
        ('SAMPLING', '샘플링 검사'),
        ('SENSORY', '관능 검사'),
    ]

    STATUS_CHOICES = [
        ('DRAFT', '초안'),
        ('ACTIVE', '활성'),
        ('INACTIVE', '비활성'),
    ]

    plan_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='inspection_plans_v2')
    item = models.ForeignKey(ProductItem, on_delete=models.CASCADE, related_name='inspection_plans_v2')
    step = models.ForeignKey(ProcessStep, on_delete=models.CASCADE, related_name='inspection_plans_v2', null=True, blank=True)

    plan_name = models.CharField(max_length=200)
    rev_no = models.CharField(max_length=20, default='1.0')
    inspection_type = models.CharField(max_length=20, choices=INSPECTION_TYPE_CHOICES)

    # 주기 규칙
    FREQUENCY_CHOICES = [
        ('EACH_LOT', 'LOT별'),
        ('EACH_SHIFT', '교대별'),
        ('DAILY', '일일'),
        ('N_PCS', 'N개마다'),
    ]
    frequency_rule = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)

    sampling_rule = models.ForeignKey(SamplingRule, on_delete=models.SET_NULL, null=True, blank=True, related_name='inspection_plans_v2')

    effective_from = models.DateTimeField()
    effective_to = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inspection_plan_v2'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.plan_name} - {self.item.item_code}"


class InspectionSpec(models.Model):
    """검사 규격/판정기준 (inspection_spec)"""
    JUDGE_METHOD_CHOICES = [
        ('NUMERIC', '수치 판정'),
        ('ENUM', '열거 판정'),
        ('TEXT', '텍스트 판정'),
    ]

    spec_id = models.AutoField(primary_key=True)
    plan = models.ForeignKey(InspectionPlanNew, on_delete=models.CASCADE, related_name='specs')
    char = models.ForeignKey(QCCharacteristic, on_delete=models.CASCADE, related_name='specs')

    judge_method = models.CharField(max_length=20, choices=JUDGE_METHOD_CHOICES)

    # 수치 판정 (override 가능)
    numeric_lsl = models.FloatField(null=True, blank=True)
    numeric_target = models.FloatField(null=True, blank=True)
    numeric_usl = models.FloatField(null=True, blank=True)

    # 열거 판정
    enum_values = models.JSONField(null=True, blank=True, help_text='허용값 리스트')

    measurement_method = models.TextField(blank=True)
    gage_id = models.IntegerField(null=True, blank=True)  # 측정기기 연계
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inspection_spec'
        ordering = ['plan', 'char']

    def __str__(self):
        return f"{self.plan.plan_name} - {self.char.char_name}"


class InspectionRun(models.Model):
    """검사 실행 (inspection_run)"""
    JUDGEMENT_CHOICES = [
        ('PASS', '합격'),
        ('FAIL', '불합격'),
        ('HOLD', '보류'),
    ]

    run_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='inspection_runs')
    lot = models.ForeignKey(LotProduction, on_delete=models.CASCADE, related_name='inspection_runs')
    plan = models.ForeignKey(InspectionPlanNew, on_delete=models.PROTECT, related_name='runs')
    step = models.ForeignKey(ProcessStep, on_delete=models.SET_NULL, null=True, related_name='inspection_runs')

    run_dt = models.DateTimeField(default=timezone.now)
    inspector_id = models.IntegerField(help_text='검사자 ID')
    sample_n = models.IntegerField(help_text='샘플 번호')

    environment = models.JSONField(null=True, blank=True, help_text='온습도 등 환경 정보')

    overall_judgement = models.CharField(max_length=20, choices=JUDGEMENT_CHOICES, null=True, blank=True)
    ai_summary_id = models.IntegerField(null=True, blank=True, help_text='AI 요약 연결')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inspection_run'
        ordering = ['-run_dt']

    def __str__(self):
        return f"Run {self.run_id} - {self.lot.lot_no}"


class InspectionResult(models.Model):
    """검사 결과 원시 데이터 (inspection_result)"""
    result_id = models.AutoField(primary_key=True)
    run = models.ForeignKey(InspectionRun, on_delete=models.CASCADE, related_name='results')
    char = models.ForeignKey(QCCharacteristic, on_delete=models.PROTECT, related_name='results')
    spec = models.ForeignKey(InspectionSpec, on_delete=models.PROTECT, related_name='results')

    sample_no = models.IntegerField()
    value_num = models.FloatField(null=True, blank=True)
    value_text = models.CharField(max_length=500, blank=True)
    value_enum = models.CharField(max_length=100, blank=True)

    is_out_of_spec = models.BooleanField(default=False)
    defect_code_id = models.IntegerField(null=True, blank=True)
    remark = models.TextField(blank=True)

    measured_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inspection_result'
        ordering = ['run', 'sample_no']

    def __str__(self):
        return f"Sample {self.sample_no}: {self.value_num}"


class DefectCode(models.Model):
    """불량 코드 (defect_code)"""
    defect_code_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='defect_codes')

    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    severity = models.IntegerField(help_text='1~10, 10이 가장 심각')

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'defect_code'
        ordering = ['category', 'code']
        unique_together = [['site', 'code']]

    def __str__(self):
        return f"{self.code} - {self.name}"


class GageMaster(models.Model):
    """측정기기 마스터 (gage_master)"""
    gage_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='gages')

    gage_name = models.CharField(max_length=200)
    model = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=100, blank=True)

    calibration_due_dt = models.DateTimeField()
    calibration_interval_days = models.IntegerField(default=365)

    status = models.CharField(max_length=20, default='ACTIVE')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'gage_master'
        ordering = ['gage_name']

    def __str__(self):
        return f"{self.gage_name} ({self.model})"
