"""
실행 데이터 모델 - Operation Actual, Execution Events

DOWN_RISK 예측을 위한 기반 데이터
"""
from django.db import models
from django.utils import timezone
from decimal import Decimal


class OperationActual(models.Model):
    """
    작업 실적 데이터

    계획(Plan) 대비 실제(Actual) 실행 결과 추적
    DOWN_RISK 예측의 주요 데이터 소스
    """
    actual_id = models.AutoField(primary_key=True)

    # 작업 식별
    wo_no = models.CharField(max_length=30, verbose_name="작업지시번호", db_index=True)
    op_seq = models.IntegerField(verbose_name="공정순서")
    operation_nm = models.CharField(max_length=200, verbose_name="공정명")

    # 설비 정보
    resource_code = models.CharField(max_length=20, verbose_name="설비코드", db_index=True)

    # 계획 시간
    planned_start_dt = models.DateTimeField(verbose_name="계획시작일시")
    planned_end_dt = models.DateTimeField(verbose_name="계획종료일시")
    planned_duration_minutes = models.IntegerField(verbose_name="계획소요시간(분)")

    # 실제 시간
    actual_start_dt = models.DateTimeField(null=True, blank=True, verbose_name="실제시작일시")
    actual_end_dt = models.DateTimeField(null=True, blank=True, verbose_name="실제종료일시")
    actual_duration_minutes = models.IntegerField(null=True, blank=True, verbose_name="실제소요시간(분)")

    # 작업 시간 (시간 단위) - DOWN_RISK 계산 핵심
    proc_time_hr = models.FloatField(
        null=True,
        blank=True,
        verbose_name="실제작업시간(시간)",
        help_text="DOWN_RISK 계산에 사용"
    )

    # 수량
    planned_qty = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="계획수량"
    )
    actual_qty = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="실제수량"
    )
    good_qty = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="양품수량"
    )
    defect_qty = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="불량수량"
    )

    # 상태
    STATUS_CHOICES = [
        ('PLANNED', '계획'),
        ('STARTED', '시작'),
        ('PAUSED', '일시중지'),
        ('COMPLETED', '완료'),
        ('CANCELLED', '취소'),
        ('DELAYED', '지연'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PLANNED',
        verbose_name="상태",
        db_index=True
    )

    # DOWN 관련 (비정상 작업 탐지)
    is_abnormal = models.BooleanField(
        default=False,
        verbose_name="비정상여부",
        help_text="계획 대비 크게 지연된 작업"
    )
    delay_minutes = models.IntegerField(
        default=0,
        verbose_name="지연시간(분)",
        help_text="actual - planned"
    )
    delay_reason = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="지연사유"
    )

    # DOWN 이벤트 연결 (optional)
    down_events = models.JSONField(
        default=list,
        blank=True,
        verbose_name="다운타임이벤트",
        help_text="[{type, start, end, reason}]"
    )

    # 비고
    remarks = models.TextField(null=True, blank=True, verbose_name="비고")

    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        app_label = 'aps'
        db_table = "operation_actual"
        verbose_name = "작업실적"
        verbose_name_plural = "작업실적"
        ordering = ["-actual_start_dt"]
        indexes = [
            models.Index(fields=["resource_code", "actual_start_dt"], name="ix_actual_res_dt"),
            models.Index(fields=["wo_no", "op_seq"], name="ix_actual_wo_seq"),
            models.Index(fields=["status", "is_abnormal"], name="ix_actual_status_abn"),
            models.Index(fields=["actual_start_dt"], name="ix_actual_start"),
        ]

    def __str__(self):
        return f"{self.wo_no}-{self.op_seq} @ {self.resource_code} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """저장 시 자동 계산"""
        # 실제 소요시간 계산
        if self.actual_start_dt and self.actual_end_dt:
            duration = (self.actual_end_dt - self.actual_start_dt).total_seconds() / 60
            self.actual_duration_minutes = int(duration)
            self.proc_time_hr = duration / 60.0

            # 지연 시간 계산
            self.delay_minutes = self.actual_duration_minutes - self.planned_duration_minutes

            # 비정상 작업 판단 (계획 대비 50% 이상 지연)
            if self.delay_minutes > self.planned_duration_minutes * 0.5:
                self.is_abnormal = True

        super().save(*args, **kwargs)

    def calculate_efficiency(self):
        """작업 효율 계산 (%)"""
        if not self.actual_duration_minutes or self.actual_duration_minutes == 0:
            return None
        return (self.planned_duration_minutes / self.actual_duration_minutes) * 100

    def is_delayed(self):
        """지연 여부"""
        return self.delay_minutes > 0


class ExecutionEvent(models.Model):
    """
    실행 이벤트 (Down, Setup, Quality Issue 등)

    작업 중 발생하는 각종 이벤트 추적
    """
    event_id = models.AutoField(primary_key=True)

    # 이벤트 유형
    EVENT_TYPES = [
        ('DOWN_BREAKDOWN', '고장'),
        ('DOWN_MAINTENANCE', '정비'),
        ('DOWN_MATERIAL', '자재부족'),
        ('DOWN_QUALITY', '품질이슈'),
        ('DOWN_CHANGEOVER', '전환'),
        ('DOWN_OTHER', '기타'),
        ('SETUP', '준비'),
        ('IDLE', '유휴'),
        ('RUNNING', '가동'),
    ]
    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPES,
        verbose_name="이벤트유형",
        db_index=True
    )

    # 설비
    resource_code = models.CharField(max_length=20, verbose_name="설비코드", db_index=True)

    # 시간
    start_dt = models.DateTimeField(verbose_name="시작일시", db_index=True)
    end_dt = models.DateTimeField(null=True, blank=True, verbose_name="종료일시")
    duration_minutes = models.IntegerField(null=True, blank=True, verbose_name="소요시간(분)")

    # 연관 작업 (optional)
    operation_actual = models.ForeignKey(
        OperationActual,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
        verbose_name="연관작업"
    )
    wo_no = models.CharField(max_length=30, null=True, blank=True, verbose_name="작업지시번호")

    # 상세 정보
    reason = models.CharField(max_length=200, null=True, blank=True, verbose_name="사유")
    description = models.TextField(null=True, blank=True, verbose_name="상세설명")

    # 영향도
    SEVERITY_CHOICES = [
        ('LOW', '낮음'),
        ('MEDIUM', '보통'),
        ('HIGH', '높음'),
        ('CRITICAL', '심각'),
    ]
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='MEDIUM',
        verbose_name="심각도"
    )

    # 조치
    action_taken = models.TextField(null=True, blank=True, verbose_name="조치내용")
    is_resolved = models.BooleanField(default=False, verbose_name="해결여부")

    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reported_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        app_label = 'aps'
        db_table = "execution_event"
        verbose_name = "실행이벤트"
        verbose_name_plural = "실행이벤트"
        ordering = ["-start_dt"]
        indexes = [
            models.Index(fields=["resource_code", "start_dt"], name="ix_event_res_dt"),
            models.Index(fields=["event_type", "severity"], name="ix_event_type_sev"),
            models.Index(fields=["start_dt"], name="ix_event_start"),
        ]

    def __str__(self):
        return f"{self.resource_code} - {self.get_event_type_display()} ({self.start_dt})"

    def save(self, *args, **kwargs):
        """저장 시 자동 계산"""
        if self.start_dt and self.end_dt:
            duration = (self.end_dt - self.start_dt).total_seconds() / 60
            self.duration_minutes = int(duration)

        super().save(*args, **kwargs)

    def is_downtime(self):
        """다운타임 이벤트 여부"""
        return self.event_type.startswith('DOWN_')
