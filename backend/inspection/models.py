"""
Inspection Models - INSP-01/02
"""
from django.db import models


class ProcessFlow(models.Model):
    """검사 프로세스 흐름 모델"""
    flow_id = models.CharField(max_length=50, unique=True, help_text="프로세스 흐름 ID")
    product_id = models.CharField(max_length=50, help_text="제품 ID")
    version = models.CharField(max_length=20, help_text="버전")
    is_active = models.BooleanField(default=True, help_text="활성화 여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'process_flow'
        verbose_name = 'Process Flow'
        verbose_name_plural = 'Process Flows'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.flow_id} - {self.product_id}"


class ProcessStep(models.Model):
    """검사 프로세스 단계 모델"""
    INSPECTION_TYPES = [
        ('IQC', '입고검사'),
        ('IPQC', '공정검사'),
        ('FQC', '최종검사'),
        ('OQC', '출하검사'),
    ]

    step_id = models.CharField(max_length=50, unique=True, help_text="단계 ID")
    flow = models.ForeignKey(ProcessFlow, on_delete=models.CASCADE, related_name='steps', help_text="프로세스 흐름")
    step_order = models.IntegerField(help_text="순서")
    step_name = models.CharField(max_length=100, help_text="공정명")
    inspection_type = models.CharField(max_length=10, choices=INSPECTION_TYPES, help_text="검사 유형")
    criteria = models.JSONField(help_text="검사 기준 (JSON)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'process_step'
        verbose_name = 'Process Step'
        verbose_name_plural = 'Process Steps'
        ordering = ['flow', 'step_order']

    def __str__(self):
        return f"{self.step_order}. {self.step_name}"


class InspectionRun(models.Model):
    """검사 실시 모델"""
    RUN_TYPES = [
        ('NORMAL', '정검사'),
        ('R&A', 'R&A'),
        ('RED_TAG', 'RED TAG'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
        ('JUDGED', 'Judged'),
    ]

    run_id = models.CharField(max_length=50, unique=True, help_text="실시 ID")
    flow = models.ForeignKey(ProcessFlow, on_delete=models.CASCADE, related_name='runs', help_text="프로세스 흐름")
    run_type = models.CharField(max_length=20, choices=RUN_TYPES, help_text="실시 유형")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN', help_text="상태")
    inspector_id = models.CharField(max_length=50, help_text="검사원 ID")
    started_at = models.DateTimeField(help_text="시작일시")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="완료일시")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inspection_run'
        verbose_name = 'Inspection Run'
        verbose_name_plural = 'Inspection Runs'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.run_id} - {self.status}"


class InspectionResult(models.Model):
    """검사 결과 모델"""
    result_id = models.CharField(max_length=50, unique=True, help_text="결과 ID")
    run = models.ForeignKey(InspectionRun, on_delete=models.CASCADE, related_name='results', help_text="검사 실시")
    step = models.ForeignKey(ProcessStep, on_delete=models.CASCADE, related_name='results', help_text="프로세스 단계")
    sample_id = models.CharField(max_length=50, help_text="표본 ID")
    measurement_value = models.FloatField(help_text="측정값")
    is_oos = models.BooleanField(default=False, help_text="규격 이탈 여부")
    measured_at = models.DateTimeField(help_text="측정일시")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inspection_result'
        verbose_name = 'Inspection Result'
        verbose_name_plural = 'Inspection Results'
        ordering = ['-measured_at']

    def __str__(self):
        return f"{self.result_id} - {self.measurement_value}"


class AIProcessDesignHistory(models.Model):
    """AI 공정 설계 기록 모델"""
    design_id = models.CharField(max_length=50, unique=True, help_text="설계 ID")
    product_description = models.TextField(help_text="제품 설명")
    quality_requirements = models.TextField(help_text="품질 요구사항")
    production_volume = models.CharField(max_length=50, blank=True, help_text="생산량")
    proposed_flow = models.ForeignKey(ProcessFlow, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_designs', help_text="제안된 공정 흐름")
    confidence = models.FloatField(help_text="신뢰도 (0-1)")
    reasoning = models.TextField(help_text="설계 사유")
    is_applied = models.BooleanField(default=False, help_text="적용 여부")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_process_design_history'
        verbose_name = 'AI Process Design History'
        verbose_name_plural = 'AI Process Design Histories'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.design_id} - {self.confidence}"
