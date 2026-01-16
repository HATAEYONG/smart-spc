"""
설비 관리 시스템 모델
설비 마스터, 부품, 매뉴얼, 수리 이력, 예방 보전
"""
from django.db import models
from django.contrib.auth.models import User


class Equipment(models.Model):
    """설비 마스터 모델"""

    class Status(models.TextChoices):
        OPERATIONAL = 'OPERATIONAL', '가동중'
        MAINTENANCE = 'MAINTENANCE', '정비중'
        DAMAGED = 'DAMAGED', '고장'
        RETIRED = 'RETIRED', '폐기'

    code = models.CharField(max_length=50, unique=True, verbose_name='설비 코드')
    name = models.CharField(max_length=200, verbose_name='설비명')
    type = models.CharField(max_length=100, verbose_name='설비 유형')
    manufacturer = models.CharField(max_length=100, verbose_name='제조사')
    model = models.CharField(max_length=100, verbose_name='모델')
    serial_number = models.CharField(max_length=100, unique=True, verbose_name='시리얼 번호')
    location = models.CharField(max_length=100, verbose_name='설치 위치')
    installation_date = models.DateField(verbose_name='설치일')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPERATIONAL, verbose_name='상태')
    department = models.CharField(max_length=100, verbose_name='담당 부서')
    cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='취득 비용')
    specifications = models.JSONField(default=dict, verbose_name='사양')
    health_score = models.IntegerField(default=100, verbose_name='건강 점수')
    predicted_failure_days = models.IntegerField(null=True, blank=True, verbose_name='예상 잔존 수명(일)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'equipment'
        verbose_name = '설비'
        verbose_name_plural = '설비'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class EquipmentPart(models.Model):
    """설비 부품 모델"""

    code = models.CharField(max_length=50, unique=True, verbose_name='부품 코드')
    name = models.CharField(max_length=200, verbose_name='부품명')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='parts', verbose_name='설비')
    part_number = models.CharField(max_length=100, verbose_name='부품 번호')
    specifications = models.TextField(verbose_name='사양')
    stock_quantity = models.IntegerField(default=0, verbose_name='재고 수량')
    min_stock = models.IntegerField(default=10, verbose_name='최소 재고')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='단가')
    supplier = models.CharField(max_length=100, verbose_name='공급사')
    location = models.CharField(max_length=100, verbose_name='보관 위치')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'equipment_parts'
        verbose_name = '설비 부품'
        verbose_name_plural = '설비 부품'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class EquipmentManual(models.Model):
    """설비 매뉴얼 모델"""

    class FileType(models.TextChoices):
        PDF = 'PDF', 'PDF'
        WORD = 'WORD', 'Word'
        EXCEL = 'EXCEL', 'Excel'
        IMAGE = 'IMAGE', '이미지'

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='manuals', verbose_name='설비')
    title = models.CharField(max_length=200, verbose_name='제목')
    file_type = models.CharField(max_length=20, choices=FileType.choices, verbose_name='파일 유형')
    file_path = models.CharField(max_length=500, verbose_name='파일 경로')
    file_size = models.IntegerField(verbose_name='파일 크기(bytes)')
    version = models.CharField(max_length=20, verbose_name='버전')
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name='업로드일')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='업로더')
    description = models.TextField(blank=True, verbose_name='설명')
    tags = models.JSONField(default=list, verbose_name='태그')

    class Meta:
        db_table = 'equipment_manuals'
        verbose_name = '설비 매뉴얼'
        verbose_name_plural = '설비 매뉴얼'
        ordering = ['-upload_date']

    def __str__(self):
        return f"{self.equipment.code} - {self.title}"


class EquipmentRepairHistory(models.Model):
    """설비 수리 이력 모델"""

    class RepairType(models.TextChoices):
        CORRECTIVE = 'CORRECTIVE', '고장 수리'
        PREVENTIVE = 'PREVENTIVE', '예방 정비'
        PREDICTIVE = 'PREDICTIVE', '예지 보전'
        EMERGENCY = 'EMERGENCY', '긴급 수리'

    class Status(models.TextChoices):
        PENDING = 'PENDING', '대기'
        IN_PROGRESS = 'IN_PROGRESS', '진행중'
        COMPLETED = 'COMPLETED', '완료'
        CANCELLED = 'CANCELLED', '취소'

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='repair_histories', verbose_name='설비')
    repair_date = models.DateField(verbose_name='수리일')
    repair_type = models.CharField(max_length=20, choices=RepairType.choices, verbose_name='수리 유형')
    description = models.TextField(verbose_name='설명')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name='상태')
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_repairs', verbose_name='보고자')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_repairs', verbose_name='담당자')
    parts_used = models.JSONField(default=list, verbose_name='사용 부품')
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='인건비')
    parts_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='부품비')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='총비용')
    downtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='다운타임(시간)')
    notes = models.TextField(blank=True, verbose_name='비고')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'equipment_repair_histories'
        verbose_name = '설비 수리 이력'
        verbose_name_plural = '설비 수리 이력'
        ordering = ['-repair_date']

    def __str__(self):
        return f"{self.equipment.code} - {self.repair_date}"


class PreventiveMaintenance(models.Model):
    """예방 보전 모델"""

    class Frequency(models.TextChoices):
        DAILY = 'DAILY', '일일'
        WEEKLY = 'WEEKLY', '주간'
        MONTHLY = 'MONTHLY', '월간'
        QUARTERLY = 'QUARTERLY', '분기'
        YEARLY = 'YEARLY', '연간'
        CUSTOM = 'CUSTOM', '사용자'

    class Status(models.TextChoices):
        PENDING = 'PENDING', '대기'
        ASSIGNED = 'ASSIGNED', '할당'
        IN_PROGRESS = 'IN_PROGRESS', '진행중'
        COMPLETED = 'COMPLETED', '완료'
        OVERDUE = 'OVERDUE', '지연'

    class Priority(models.TextChoices):
        LOW = 'LOW', '낮음'
        MEDIUM = 'MEDIUM', '중간'
        HIGH = 'HIGH', '높음'
        CRITICAL = 'CRITICAL', '긴급'

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='pm_tasks', verbose_name='설비')
    task_number = models.CharField(max_length=50, unique=True, verbose_name='작업 번호')
    task_name = models.CharField(max_length=200, verbose_name='작업명')
    description = models.TextField(verbose_name='설명')
    frequency = models.CharField(max_length=20, choices=Frequency.choices, verbose_name='주기')
    scheduled_date = models.DateField(verbose_name='예정일')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name='상태')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pm_tasks', verbose_name='담당자')
    estimated_duration = models.IntegerField(verbose_name='예상 소요시간(분)')
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM, verbose_name='우선순위')
    last_completed = models.DateField(null=True, blank=True, verbose_name='마지막 완료일')
    next_due = models.DateField(verbose_name='다음 예정일')
    completion_notes = models.TextField(blank=True, verbose_name='완료 메모')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'preventive_maintenances'
        verbose_name = '예방 보전'
        verbose_name_plural = '예방 보전'
        ordering = ['scheduled_date']

    def __str__(self):
        return f"{self.task_number} - {self.task_name}"
