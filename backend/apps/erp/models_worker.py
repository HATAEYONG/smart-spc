"""
APS 기본정보 확장 모델 - 작업조, 작업자, 숙련도
Phase 2: 단기
"""
from django.db import models
from decimal import Decimal


class MasterShift(models.Model):
    """
    작업조 마스터

    주간/야간, A조/B조/C조 등 교대 근무 관리
    """
    shift_cd = models.CharField(max_length=20, primary_key=True, verbose_name="작업조코드")
    shift_nm = models.CharField(max_length=200, verbose_name="작업조명")

    shift_type = models.CharField(
        max_length=20,
        choices=[
            ('DAY', '주간'),
            ('NIGHT', '야간'),
            ('SWING', '교대'),
        ],
        verbose_name="작업조구분"
    )

    start_time = models.TimeField(verbose_name="시작시간")
    end_time = models.TimeField(verbose_name="종료시간")
    break_time = models.IntegerField(default=60, verbose_name="휴게시간(분)")

    # 야간 근무 여부 (종료시간이 다음날인 경우)
    is_overnight = models.BooleanField(default=False, verbose_name="야간근무여부")

    active_yn = models.CharField(max_length=1, default="Y", verbose_name="사용여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "master_shift"
        verbose_name = "작업조마스터"
        verbose_name_plural = "작업조마스터"

    def __str__(self):
        return f"{self.shift_cd} - {self.shift_nm} ({self.get_shift_type_display()})"

    def get_work_hours(self):
        """근무 시간 계산 (시간 단위)"""
        from datetime import datetime, timedelta

        start_dt = datetime.combine(datetime.today(), self.start_time)
        end_dt = datetime.combine(datetime.today(), self.end_time)

        # 야간 근무인 경우
        if self.is_overnight or end_dt <= start_dt:
            end_dt += timedelta(days=1)

        total_minutes = (end_dt - start_dt).total_seconds() / 60
        total_minutes -= self.break_time

        return total_minutes / 60


class MasterWorker(models.Model):
    """
    작업자 마스터

    작업자 기본 정보 및 소속 관리
    """
    worker_cd = models.CharField(max_length=20, primary_key=True, verbose_name="작업자코드")
    worker_nm = models.CharField(max_length=200, verbose_name="작업자명")

    workcenter = models.ForeignKey(
        'MasterWorkCenter',
        on_delete=models.CASCADE,
        related_name='workers',
        verbose_name="소속작업장"
    )

    shift = models.ForeignKey(
        MasterShift,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workers',
        verbose_name="소속작업조"
    )

    worker_type = models.CharField(
        max_length=20,
        choices=[
            ('REGULAR', '정규직'),
            ('CONTRACT', '계약직'),
            ('TEMP', '임시직'),
            ('DISPATCH', '파견직'),
        ],
        default='REGULAR',
        verbose_name="작업자구분"
    )

    # 경력 정보
    hire_date = models.DateField(null=True, blank=True, verbose_name="입사일")
    experience_years = models.IntegerField(default=0, verbose_name="경력(년)")

    # 비용 정보
    cost_per_hour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('20000.00'),
        verbose_name="시간당인건비"
    )

    # 연락처
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="연락처"
    )
    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name="이메일"
    )

    active_yn = models.CharField(max_length=1, default="Y", verbose_name="사용여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "master_worker"
        verbose_name = "작업자마스터"
        verbose_name_plural = "작업자마스터"
        indexes = [
            models.Index(fields=["workcenter"], name="ix_worker_wc"),
            models.Index(fields=["shift"], name="ix_worker_shift"),
        ]

    def __str__(self):
        return f"{self.worker_cd} - {self.worker_nm} ({self.workcenter.wc_nm})"


class WorkerSkill(models.Model):
    """
    작업자 숙련도

    작업자별 공정별 숙련도 및 작업 효율
    """
    skill_id = models.AutoField(primary_key=True)

    worker = models.ForeignKey(
        MasterWorker,
        on_delete=models.CASCADE,
        related_name='skills',
        verbose_name="작업자"
    )

    operation_nm = models.CharField(max_length=200, verbose_name="공정명")

    skill_level = models.IntegerField(
        choices=[
            (1, '초급'),
            (2, '중급'),
            (3, '고급'),
            (4, '숙련'),
            (5, '전문가'),
        ],
        verbose_name="숙련도"
    )

    efficiency_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('100.00'),
        verbose_name="작업효율(%)"
    )
    # 초급(1): 70%, 중급(2): 85%, 고급(3): 100%, 숙련(4): 115%, 전문가(5): 130%

    # 자격증 정보
    certified_yn = models.CharField(max_length=1, default="N", verbose_name="자격증보유")
    certification_nm = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="자격증명"
    )
    certification_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="자격취득일"
    )

    # 교육 이수 정보
    training_hours = models.IntegerField(default=0, verbose_name="교육시간(시간)")
    last_training_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="최종교육일"
    )

    active_yn = models.CharField(max_length=1, default="Y", verbose_name="사용여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "worker_skill"
        verbose_name = "작업자숙련도"
        verbose_name_plural = "작업자숙련도"
        unique_together = (("worker", "operation_nm"),)
        indexes = [
            models.Index(fields=["operation_nm", "skill_level"], name="ix_skill_op_level"),
            models.Index(fields=["worker", "skill_level"], name="ix_skill_worker_level"),
        ]

    def __str__(self):
        return f"{self.worker.worker_nm} - {self.operation_nm} (Lv.{self.skill_level})"

    def save(self, *args, **kwargs):
        """저장 시 숙련도에 따른 효율 자동 설정"""
        if not self.efficiency_rate or self.efficiency_rate == 100:
            # 숙련도별 기본 효율
            efficiency_map = {
                1: Decimal('70.00'),   # 초급
                2: Decimal('85.00'),   # 중급
                3: Decimal('100.00'),  # 고급
                4: Decimal('115.00'),  # 숙련
                5: Decimal('130.00'),  # 전문가
            }
            self.efficiency_rate = efficiency_map.get(self.skill_level, Decimal('100.00'))

        super().save(*args, **kwargs)


class WorkAssignment(models.Model):
    """
    작업 할당

    작업지시에 작업자/작업조 할당 및 실적 관리
    """
    assignment_id = models.AutoField(primary_key=True)

    wo_no = models.CharField(max_length=30, verbose_name="작업지시번호", db_index=True)
    operation_seq = models.IntegerField(verbose_name="공정순서")
    operation_nm = models.CharField(max_length=200, verbose_name="공정명")

    worker = models.ForeignKey(
        MasterWorker,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name="담당작업자"
    )

    shift = models.ForeignKey(
        MasterShift,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name="작업조"
    )

    # 계획 시간
    assigned_start_dt = models.DateTimeField(verbose_name="할당시작시간")
    assigned_end_dt = models.DateTimeField(verbose_name="할당종료시간")
    assigned_duration = models.IntegerField(verbose_name="할당시간(분)")

    # 실제 시간
    actual_start_dt = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="실제시작시간"
    )
    actual_end_dt = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="실제종료시간"
    )
    actual_duration = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="실제시간(분)"
    )

    # 생산량
    target_qty = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="목표수량"
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
    status = models.CharField(
        max_length=20,
        choices=[
            ('ASSIGNED', '할당'),
            ('STARTED', '시작'),
            ('PAUSED', '일시중지'),
            ('COMPLETED', '완료'),
            ('CANCELLED', '취소'),
        ],
        default='ASSIGNED',
        verbose_name="상태"
    )

    # 비고
    remarks = models.TextField(null=True, blank=True, verbose_name="비고")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "work_assignment"
        verbose_name = "작업할당"
        verbose_name_plural = "작업할당"
        indexes = [
            models.Index(fields=["wo_no", "operation_seq"], name="ix_assign_wo_seq"),
            models.Index(fields=["worker", "assigned_start_dt"], name="ix_assign_worker_dt"),
            models.Index(fields=["shift", "assigned_start_dt"], name="ix_assign_shift_dt"),
            models.Index(fields=["status"], name="ix_assign_status"),
        ]
        ordering = ["assigned_start_dt"]

    def __str__(self):
        return f"{self.wo_no}-{self.operation_seq} → {self.worker.worker_nm} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """저장 시 자동 계산"""
        # 할당 시간 계산
        if self.assigned_start_dt and self.assigned_end_dt:
            duration = (self.assigned_end_dt - self.assigned_start_dt).total_seconds() / 60
            self.assigned_duration = int(duration)

        # 실제 시간 계산
        if self.actual_start_dt and self.actual_end_dt:
            duration = (self.actual_end_dt - self.actual_start_dt).total_seconds() / 60
            self.actual_duration = int(duration)

        super().save(*args, **kwargs)

    def start_work(self):
        """작업 시작"""
        from django.utils import timezone
        self.status = 'STARTED'
        self.actual_start_dt = timezone.now()
        self.save()

    def complete_work(self, good_qty, defect_qty=0):
        """작업 완료"""
        from django.utils import timezone
        self.status = 'COMPLETED'
        self.actual_end_dt = timezone.now()
        self.good_qty = good_qty
        self.defect_qty = defect_qty
        self.actual_qty = good_qty + defect_qty
        self.save()
