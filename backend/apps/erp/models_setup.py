"""
APS 기본정보 확장 모델 - Setup Time, Batch
Phase 3: Setup Time 최적화 지원
"""
from django.db import models
from decimal import Decimal


class ItemSetupTime(models.Model):
    """
    품목 전환 Setup Time

    품목 간 전환 시 필요한 setup 시간 정의
    동일 설비에서 품목 A → 품목 B 전환 시 소요 시간
    """
    setup_id = models.AutoField(primary_key=True)

    machine = models.ForeignKey(
        'MasterMachine',
        on_delete=models.CASCADE,
        related_name='setup_times',
        verbose_name="설비"
    )

    from_item = models.ForeignKey(
        'MasterItem',
        on_delete=models.CASCADE,
        related_name='setup_from',
        verbose_name="이전품목"
    )

    to_item = models.ForeignKey(
        'MasterItem',
        on_delete=models.CASCADE,
        related_name='setup_to',
        verbose_name="다음품목"
    )

    setup_minutes = models.IntegerField(verbose_name="Setup시간(분)")

    # Setup 비용 (선택)
    setup_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Setup비용"
    )

    # Setup 유형
    setup_type = models.CharField(
        max_length=20,
        choices=[
            ('STANDARD', '표준'),
            ('QUICK', '빠른전환'),
            ('COMPLEX', '복잡전환'),
            ('CLEANING', '세척'),
        ],
        default='STANDARD',
        verbose_name="Setup구분"
    )

    # 작업자 필요 여부
    requires_worker = models.BooleanField(default=True, verbose_name="작업자필요")
    required_workers = models.IntegerField(default=1, verbose_name="필요인원")

    # 비고
    description = models.TextField(null=True, blank=True, verbose_name="설명")

    active_yn = models.CharField(max_length=1, default="Y", verbose_name="사용여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "item_setup_time"
        verbose_name = "품목Setup시간"
        verbose_name_plural = "품목Setup시간"
        unique_together = (("machine", "from_item", "to_item"),)
        indexes = [
            models.Index(fields=["machine", "from_item"], name="ix_setup_mc_from"),
            models.Index(fields=["machine", "to_item"], name="ix_setup_mc_to"),
        ]
        ordering = ["machine", "from_item", "to_item"]

    def __str__(self):
        return f"{self.machine.mc_cd}: {self.from_item.itm_id} → {self.to_item.itm_id} ({self.setup_minutes}분)"


class ItemFamily(models.Model):
    """
    품목 패밀리

    유사한 품목들을 그룹화하여 setup time 최소화
    동일 패밀리 내 품목 간 전환 시 setup time 감소
    """
    family_cd = models.CharField(max_length=50, primary_key=True, verbose_name="패밀리코드")
    family_nm = models.CharField(max_length=200, verbose_name="패밀리명")

    # 패밀리 속성
    family_type = models.CharField(
        max_length=20,
        choices=[
            ('SIZE', '크기별'),
            ('COLOR', '색상별'),
            ('MATERIAL', '재질별'),
            ('SHAPE', '형태별'),
        ],
        verbose_name="패밀리구분"
    )

    # 동일 패밀리 내 setup time (일반 setup time보다 짧음)
    intra_family_setup_minutes = models.IntegerField(
        default=10,
        verbose_name="패밀리내Setup(분)"
    )

    # 패밀리 간 setup time
    inter_family_setup_minutes = models.IntegerField(
        default=30,
        verbose_name="패밀리간Setup(분)"
    )

    description = models.TextField(null=True, blank=True, verbose_name="설명")

    active_yn = models.CharField(max_length=1, default="Y", verbose_name="사용여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "item_family"
        verbose_name = "품목패밀리"
        verbose_name_plural = "품목패밀리"

    def __str__(self):
        return f"{self.family_cd} - {self.family_nm}"


class BatchConfig(models.Model):
    """
    Batch 작업 설정

    동일 품목 여러 개를 한번에 처리하는 batch 작업 설정
    """
    batch_config_id = models.AutoField(primary_key=True)

    machine = models.ForeignKey(
        'MasterMachine',
        on_delete=models.CASCADE,
        related_name='batch_configs',
        verbose_name="설비"
    )

    item = models.ForeignKey(
        'MasterItem',
        on_delete=models.CASCADE,
        related_name='batch_configs',
        verbose_name="품목"
    )

    # Batch size 설정
    min_batch_size = models.IntegerField(default=1, verbose_name="최소Batch크기")
    max_batch_size = models.IntegerField(default=10, verbose_name="최대Batch크기")
    optimal_batch_size = models.IntegerField(default=5, verbose_name="최적Batch크기")

    # Batch 처리 시간 (setup + 단위당 처리시간)
    batch_setup_minutes = models.IntegerField(verbose_name="Batch Setup시간(분)")
    unit_process_minutes = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="단위처리시간(분)"
    )

    # 예: batch_size=5, setup=30분, unit=10분
    # → 총 시간 = 30 + 5*10 = 80분
    # vs 개별 작업 5개: 5*(30+10) = 200분 → Batch가 훨씬 효율적!

    # Batch 제약
    allow_partial_batch = models.BooleanField(
        default=True,
        verbose_name="부분Batch허용"
    )  # False면 optimal_batch_size만 허용

    # Batch 우선순위
    batch_priority = models.IntegerField(
        default=1,
        verbose_name="Batch우선순위"
    )  # 높을수록 우선

    description = models.TextField(null=True, blank=True, verbose_name="설명")

    active_yn = models.CharField(max_length=1, default="Y", verbose_name="사용여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "batch_config"
        verbose_name = "Batch설정"
        verbose_name_plural = "Batch설정"
        unique_together = (("machine", "item"),)
        indexes = [
            models.Index(fields=["machine", "item"], name="ix_batch_mc_item"),
        ]

    def __str__(self):
        return f"{self.machine.mc_cd} - {self.item.itm_id} (Batch: {self.min_batch_size}~{self.max_batch_size})"

    def calculate_batch_duration(self, batch_size):
        """Batch 처리 시간 계산"""
        if batch_size < self.min_batch_size or batch_size > self.max_batch_size:
            return None
        return self.batch_setup_minutes + int(float(self.unit_process_minutes) * batch_size)
