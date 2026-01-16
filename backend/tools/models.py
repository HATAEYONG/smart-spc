"""
치공구 관리 시스템 모델
치공구 마스터, 수리 이력
"""
from django.db import models
from django.contrib.auth.models import User


class Tool(models.Model):
    """치공구 마스터 모델"""

    class Status(models.TextChoices):
        AVAILABLE = 'AVAILABLE', '사용 가능'
        IN_USE = 'IN_USE', '사용중'
        MAINTENANCE = 'MAINTENANCE', '정비중'
        DAMAGED = 'DAMAGED', '고장'
        RETIRED = 'RETIRED', '폐기'

    code = models.CharField(max_length=50, unique=True, verbose_name='치공구 코드')
    name = models.CharField(max_length=200, verbose_name='치공구명')
    type = models.CharField(max_length=100, verbose_name='치공구 유형')
    manufacturer = models.CharField(max_length=100, verbose_name='제조사')
    model = models.CharField(max_length=100, verbose_name='모델')
    serial_number = models.CharField(max_length=100, unique=True, verbose_name='시리얼 번호')
    location = models.CharField(max_length=100, verbose_name='보관 위치')
    purchase_date = models.DateField(verbose_name='구입일')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE, verbose_name='상태')
    department = models.CharField(max_length=100, verbose_name='담당 부서')
    cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='취득 비용')
    specifications = models.JSONField(default=dict, verbose_name='사양')

    # 수명 관리
    expected_life_days = models.IntegerField(verbose_name='예상 수명(일)')
    predicted_remaining_days = models.IntegerField(null=True, blank=True, verbose_name='예상 잔존 수명(일)')
    usage_count = models.IntegerField(default=0, verbose_name='사용 횟수')
    total_usage_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='총 사용 시간(시간)')

    # 교체 관리
    optimal_replacement_date = models.DateField(null=True, blank=True, verbose_name='최적 교체일')
    last_replacement_date = models.DateField(null=True, blank=True, verbose_name='마지막 교체일')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'tools'
        verbose_name = '치공구'
        verbose_name_plural = '치공구'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def usage_percentage(self):
        """사용률 계산"""
        if self.expected_life_days > 0:
            return (self.usage_count / self.expected_life_days) * 100
        return 0

    @property
    def replacement_urgency(self):
        """교체 시급성"""
        usage_pct = self.usage_percentage
        if usage_pct >= 97:
            return 'CRITICAL'
        elif usage_pct >= 90:
            return 'URGENT'
        elif usage_pct >= 70:
            return 'WARNING'
        else:
            return 'NORMAL'


class ToolRepairHistory(models.Model):
    """치공구 수리 이력 모델"""

    class RepairType(models.TextChoices):
        CORRECTIVE = 'CORRECTIVE', '고장 수리'
        PREVENTIVE = 'PREVENTIVE', '예방 정비'
        REPLACEMENT = 'REPLACEMENT', '교체'
        REFURBISHMENT = 'REFURBISHMENT', '재생'

    class Status(models.TextChoices):
        PENDING = 'PENDING', '대기'
        IN_PROGRESS = 'IN_PROGRESS', '진행중'
        COMPLETED = 'COMPLETED', '완료'
        CANCELLED = 'CANCELLED', '취소'

    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name='repair_histories', verbose_name='치공구')
    repair_date = models.DateField(verbose_name='수리일')
    repair_type = models.CharField(max_length=20, choices=RepairType.choices, verbose_name='수리 유형')
    description = models.TextField(verbose_name='설명')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name='상태')
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_tool_repairs', verbose_name='보고자')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_tool_repairs', verbose_name='담당자')
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='인건비')
    parts_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='부품비')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='총비용')
    downtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='다운타임(시간)')
    notes = models.TextField(blank=True, verbose_name='비고')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'tool_repair_histories'
        verbose_name = '치공구 수리 이력'
        verbose_name_plural = '치공구 수리 이력'
        ordering = ['-repair_date']

    def __str__(self):
        return f"{self.tool.code} - {self.repair_date}"
