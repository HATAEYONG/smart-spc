from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Equipment(models.Model):
    """설비 정보 모델"""

    CATEGORY_CHOICES = [
        ('CNC', 'CNC 가공기'),
        ('PRESS', '프레스'),
        ('WELDING', '용접기'),
        ('HEAT_TREAT', '열처리로'),
        ('MEASUREMENT', '측정기'),
        ('OTHER', '기타'),
    ]

    STATUS_CHOICES = [
        ('OPERATIONAL', '가동 중'),
        ('IDLE', '대기 중'),
        ('MAINTENANCE', '점검 중'),
        ('BREAKDOWN', '고장'),
        ('RETIRED', '퇴역'),
    ]

    code = models.CharField(max_length=50, unique=True, verbose_name='설비 코드')
    name = models.CharField(max_length=200, verbose_name='설비명')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='설비 유형')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPERATIONAL', verbose_name='상태')
    location = models.CharField(max_length=100, blank=True, verbose_name='설치 위치')
    manufacturer = models.CharField(max_length=100, blank=True, verbose_name='제조사')
    model_number = models.CharField(max_length=100, blank=True, verbose_name='모델명')
    serial_number = models.CharField(max_length=100, blank=True, verbose_name='일련번호')
    installation_date = models.DateField(verbose_name='설치일')
    warranty_expiry = models.DateField(blank=True, null=True, verbose_name='보증 만료일')
    rated_capacity = models.FloatField(blank=True, null=True, verbose_name='정격 용량')
    current_capacity = models.FloatField(blank=True, null=True, verbose_name='현재 용량')

    # 예지 보전 관련 필드
    mtbf_mean_time = models.FloatField(blank=True, null=True, verbose_name='MTBF (평균 고장 간격)')
    mttr_mean_time = models.FloatField(blank=True, null=True, verbose_name='MTTR (평균 수리 시간)')
    availability_target = models.FloatField(default=95.0, verbose_name='가동률 목표 (%)')
    availability_current = models.FloatField(blank=True, null=True, verbose_name='현재 가동률 (%)')

    last_maintenance_date = models.DateField(blank=True, null=True, verbose_name='마지막 점검일')
    next_maintenance_date = models.DateField(blank=True, null=True, verbose_name='다음 점검예정일')

    failure_probability = models.FloatField(default=0.0, verbose_name='고장 확률 (%)')
    health_score = models.FloatField(default=100.0, verbose_name='건전도 점수')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'pm_equipment'
        verbose_name = '설비'
        verbose_name_plural = '설비'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.name}"


class SensorData(models.Model):
    """센서 데이터 모델"""

    SENSOR_TYPE_CHOICES = [
        ('VIBRATION', '진동'),
        ('TEMPERATURE', '온도'),
        ('PRESSURE', '압력'),
        ('CURRENT', '전류'),
        ('VOLTAGE', '전압'),
        ('SPEED', '속도'),
        ('FLOW', '유량'),
        ('NOISE', '소음'),
        ('OTHER', '기타'),
    ]

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='sensor_data', verbose_name='설비')
    sensor_type = models.CharField(max_length=20, choices=SENSOR_TYPE_CHOICES, verbose_name='센서 유형')
    sensor_id = models.CharField(max_length=100, verbose_name='센서 ID')

    # 측정값
    value = models.FloatField(verbose_name='측정값')
    unit = models.CharField(max_length=20, blank=True, verbose_name='단위')

    # 임계값
    threshold_min = models.FloatField(blank=True, null=True, verbose_name='최소 임계값')
    threshold_max = models.FloatField(blank=True, null=True, verbose_name='최대 임계값')

    # 상태
    is_normal = models.BooleanField(default=True, verbose_name='정상 여부')
    anomaly_score = models.FloatField(default=0.0, verbose_name='이상 점수')

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='측정 시간')

    class Meta:
        db_table = 'pm_sensor_data'
        verbose_name = '센서 데이터'
        verbose_name_plural = '센서 데이터'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['equipment', '-timestamp']),
            models.Index(fields=['sensor_type', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.equipment.code} - {self.sensor_type}: {self.value} {self.unit}"


class MaintenanceRecord(models.Model):
    """점검/수리 이력 모델"""

    TYPE_CHOICES = [
        ('PREVENTIVE', '예방 점검'),
        ('PREDICTIVE', '예지 보전'),
        ('CORRECTIVE', '고장 수리'),
        ('EMERGENCY', '긴급 수리'),
        ('OVERHAUL', '오버홀'),
    ]

    STATUS_CHOICES = [
        ('SCHEDULED', '예정됨'),
        ('IN_PROGRESS', '진행 중'),
        ('COMPLETED', '완료'),
        ('CANCELLED', '취소됨'),
    ]

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_records', verbose_name='설비')
    record_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='점검 유형')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED', verbose_name='상태')

    title = models.CharField(max_length=200, verbose_name='제목')
    description = models.TextField(blank=True, verbose_name='설명')

    scheduled_date = models.DateTimeField(verbose_name='예정일')
    started_at = models.DateTimeField(blank=True, null=True, verbose_name='시작일')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='완료일')

    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='기술자')

    # 비용
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='인건비')
    parts_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='부품비')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='총비용')

    # 결과
    work_performed = models.TextField(blank=True, verbose_name='수행 작업')
    parts_replaced = models.TextField(blank=True, verbose_name='교체 부품')
    root_cause = models.TextField(blank=True, verbose_name='근본 원인')
    recommendations = models.TextField(blank=True, verbose_name='권장사항')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'pm_maintenance_records'
        verbose_name = '점검 이력'
        verbose_name_plural = '점검 이력'
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.equipment.code} - {self.title}"


class FailurePrediction(models.Model):
    """고장 예측 모델 결과"""

    SEVERITY_CHOICES = [
        ('LOW', '낮음'),
        ('MEDIUM', '중간'),
        ('HIGH', '높음'),
        ('CRITICAL', '매우 높음'),
    ]

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='failure_predictions', verbose_name='설비')

    # 예측 정보
    prediction_date = models.DateTimeField(auto_now_add=True, verbose_name='예측일')
    predicted_failure_date = models.DateTimeField(verbose_name='예측 고장일')
    failure_probability = models.FloatField(verbose_name='고장 확률 (%)')
    confidence = models.FloatField(verbose_name='신뢰도 (%)')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, verbose_name='심각도')

    # 원인 분석
    potential_causes = models.TextField(verbose_name='잠재적 원인')
    affected_components = models.TextField(blank=True, verbose_name='영향받는 부품')

    # 권장 조치
    recommended_actions = models.TextField(verbose_name='권장 조치')
    priority = models.IntegerField(default=1, verbose_name='우선순위')

    # 예측 모델 정보
    model_version = models.CharField(max_length=50, blank=True, verbose_name='모델 버전')
    model_type = models.CharField(max_length=50, blank=True, verbose_name='모델 유형')

    # 상태
    is_acknowledged = models.BooleanField(default=False, verbose_name='확인 여부')
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='확인자')
    acknowledged_at = models.DateTimeField(blank=True, null=True, verbose_name='확인일')

    # 실제 결과
    actual_failure = models.BooleanField(blank=True, null=True, verbose_name='실제 고장 여부')

    class Meta:
        db_table = 'pm_failure_predictions'
        verbose_name = '고장 예측'
        verbose_name_plural = '고장 예측'
        ordering = ['-prediction_date']
        indexes = [
            models.Index(fields=['equipment', '-prediction_date']),
            models.Index(fields=['severity', '-prediction_date']),
        ]

    def __str__(self):
        return f"{self.equipment.code} - {self.severity} ({self.failure_probability}%)"


class MaintenancePlan(models.Model):
    """예방 보전 계획 모델"""

    FREQUENCY_CHOICES = [
        ('DAILY', '일일'),
        ('WEEKLY', '주간'),
        ('MONTHLY', '월간'),
        ('QUARTERLY', '분기'),
        ('YEARLY', '연간'),
        ('CUSTOM', '사용자 정의'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', '활성'),
        ('INACTIVE', '비활성'),
        ('PAUSED', '일시중지'),
    ]

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_plans', verbose_name='설비')

    name = models.CharField(max_length=200, verbose_name='계획명')
    description = models.TextField(blank=True, verbose_name='설명')

    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name='빈도')
    frequency_days = models.IntegerField(blank=True, null=True, verbose_name='주기 (일)')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', verbose_name='상태')

    # 작업 내용
    tasks = models.TextField(verbose_name='작업 내용')
    required_parts = models.TextField(blank=True, verbose_name='필요 부품')
    estimated_duration = models.IntegerField(blank=True, null=True, verbose_name='예상 소요시간 (분)')
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='예상 비용')

    # 담당자
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='담당자')

    # 일정
    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(blank=True, null=True, verbose_name='종료일')
    last_performed_date = models.DateField(blank=True, null=True, verbose_name='마지막 수행일')
    next_due_date = models.DateField(verbose_name='다음 예정일')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'pm_maintenance_plans'
        verbose_name = '예방 보전 계획'
        verbose_name_plural = '예방 보전 계획'
        ordering = ['next_due_date']

    def __str__(self):
        return f"{self.equipment.code} - {self.name}"
