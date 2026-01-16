"""
작업지시 관리 시스템 모델
작업지시, 설비, 치공구 연계 관리
"""
from django.db import models
from django.contrib.auth.models import User

# Forward references for circular imports
Equipment = 'equipment.Equipment'
Tool = 'tools.Tool'


class WorkOrder(models.Model):
    """작업지시 모델"""

    class Status(models.TextChoices):
        PENDING = 'PENDING', '대기'
        ASSIGNED = 'ASSIGNED', '할당'
        IN_PROGRESS = 'IN_PROGRESS', '진행중'
        COMPLETED = 'COMPLETED', '완료'
        CANCELLED = 'CANCELLED', '취소'
        ON_HOLD = 'ON_HOLD', '보류'

    class Priority(models.TextChoices):
        LOW = 'LOW', '낮음'
        MEDIUM = 'MEDIUM', '중간'
        HIGH = 'HIGH', '높음'
        CRITICAL = 'CRITICAL', '긴급'

    order_number = models.CharField(max_length=50, unique=True, verbose_name='작업지시 번호')
    product_code = models.CharField(max_length=50, verbose_name='제품 코드')
    product_name = models.CharField(max_length=200, verbose_name='제품명')
    quantity = models.IntegerField(verbose_name='생산 수량')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name='상태')
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM, verbose_name='우선순위')

    # 일정
    start_date = models.DateField(verbose_name='시작일')
    target_end_date = models.DateField(verbose_name='목표 완료일')
    actual_end_date = models.DateField(null=True, blank=True, verbose_name='실제 완료일')

    # 설비 및 치공구 연계
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_orders',
        verbose_name='설비'
    )

    # 담당자
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_work_orders',
        verbose_name='담당자'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_work_orders',
        verbose_name='생성자'
    )

    # 진행률
    progress_percentage = models.IntegerField(default=0, verbose_name='진행률(%)')
    completed_quantity = models.IntegerField(default=0, verbose_name='완료 수량')

    # AI 예측
    predicted_completion_risk = models.CharField(
        max_length=20,
        choices=[('LOW', '낮음'), ('MEDIUM', '중간'), ('HIGH', '높음')],
        default='LOW',
        verbose_name='완료 위험도'
    )
    risk_reasons = models.JSONField(default=list, verbose_name='위험도 사유')

    # 비용
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='예상 비용')
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='실제 비용')

    notes = models.TextField(blank=True, verbose_name='비고')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'work_orders'
        verbose_name = '작업지시'
        verbose_name_plural = '작업지시'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.order_number} - {self.product_name}"


class WorkOrderTool(models.Model):
    """작업지시-치공구 연결 모델"""

    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='work_order_tools',
        verbose_name='작업지시'
    )
    tool = models.ForeignKey(
        Tool,
        on_delete=models.SET_NULL,
        null=True,
        related_name='work_order_tools',
        verbose_name='치공구'
    )
    quantity_required = models.IntegerField(default=1, verbose_name='필요 수량')
    usage_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='사용 시간(시간)')

    class Meta:
        db_table = 'work_order_tools'
        verbose_name = '작업지시 치공구'
        verbose_name_plural = '작업지시 치공구'
        unique_together = ['work_order', 'tool']

    def __str__(self):
        return f"{self.work_order.order_number} - {self.tool.code if self.tool else 'N/A'}"


class WorkOrderProgress(models.Model):
    """작업지시 진행 상황 모델"""

    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='progress_logs',
        verbose_name='작업지시'
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='시간')
    status = models.CharField(max_length=20, choices=WorkOrder.Status.choices, verbose_name='상태')
    progress_percentage = models.IntegerField(verbose_name='진행률(%)')
    completed_quantity = models.IntegerField(default=0, verbose_name='완료 수량')
    notes = models.TextField(blank=True, verbose_name='비고')
    reported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='보고자'
    )

    class Meta:
        db_table = 'work_order_progress'
        verbose_name = '작업지시 진행 상황'
        verbose_name_plural = '작업지시 진행 상황'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.work_order.order_number} - {self.timestamp}"
