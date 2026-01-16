"""
ERP/MES 연계 시스템 모델
외부 시스템 연결, 동기화 이력, 자체 입력
"""
from django.db import models
from django.contrib.auth.models import User


class ERPIntegration(models.Model):
    """ERP 연계 관리 모델"""

    class SystemType(models.TextChoices):
        ERP = 'ERP', 'ERP'
        MES = 'MES', 'MES'
        PLM = 'PLM', 'PLM'
        WMS = 'WMS', 'WMS'
        QMS = 'QMS', 'QMS'

    class Status(models.TextChoices):
        CONNECTED = 'CONNECTED', '연결됨'
        DISCONNECTED = 'DISCONNECTED', '연결안됨'
        ERROR = 'ERROR', '에러'
        TESTING = 'TESTING', '테스트중'

    class AuthMethod(models.TextChoices):
        API_KEY = 'API_KEY', 'API Key'
        OAUTH = 'OAUTH', 'OAuth 2.0'
        BASIC_AUTH = 'BASIC_AUTH', 'Basic Auth'
        BEARER_TOKEN = 'BEARER_TOKEN', 'Bearer Token'

    name = models.CharField(max_length=200, verbose_name='시스템명')
    system_type = models.CharField(max_length=20, choices=SystemType.choices, verbose_name='시스템 유형')
    description = models.TextField(blank=True, verbose_name='설명')

    # 연결 정보
    endpoint_url = models.URLField(max_length=500, verbose_name='API Endpoint URL')
    auth_method = models.CharField(max_length=20, choices=AuthMethod.choices, verbose_name='인증 방식')
    api_key = models.CharField(max_length=500, blank=True, verbose_name='API Key')
    username = models.CharField(max_length=100, blank=True, verbose_name='사용자명')
    password = models.CharField(max_length=500, blank=True, verbose_name='비밀번호')
    access_token = models.CharField(max_length=500, blank=True, verbose_name='Access Token')
    refresh_token = models.CharField(max_length=500, blank=True, verbose_name='Refresh Token')

    # 동기화 설정
    sync_frequency_minutes = models.IntegerField(default=60, verbose_name='동기화 주기(분)')
    auto_sync = models.BooleanField(default=True, verbose_name='자동 동기화')
    last_sync = models.DateTimeField(null=True, blank=True, verbose_name='마지막 동기화')
    next_sync = models.DateTimeField(null=True, blank=True, verbose_name='다음 동기화')

    # 동기화할 데이터 유형
    data_types = models.JSONField(
        default=list,
        verbose_name='데이터 유형',
        help_text='예: ["생산주문", "자재정보", "BOM", "작업지시"]'
    )

    # 상태
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DISCONNECTED, verbose_name='상태')
    last_error = models.TextField(blank=True, verbose_name='마지막 에러')

    is_active = models.BooleanField(default=True, verbose_name='활성화')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'erp_integrations'
        verbose_name = 'ERP 연계'
        verbose_name_plural = 'ERP 연계'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_system_type_display()})"


class IntegrationHistory(models.Model):
    """연계 이력 모델"""

    class SyncType(models.TextChoices):
        FULL = 'FULL', '전체'
        INCREMENTAL = 'INCREMENTAL', '증분'
        MANUAL = 'MANUAL', '수동'

    class Status(models.TextChoices):
        SUCCESS = 'SUCCESS', '성공'
        FAILED = 'FAILED', '실패'
        IN_PROGRESS = 'IN_PROGRESS', '진행중'
        PARTIAL = 'PARTIAL', '부분 성공'

    sync_id = models.CharField(max_length=50, unique=True, verbose_name='동기화 ID')
    integration = models.ForeignKey(
        ERPIntegration,
        on_delete=models.CASCADE,
        related_name='sync_histories',
        verbose_name='연계 시스템'
    )
    sync_type = models.CharField(max_length=20, choices=SyncType.choices, verbose_name='동기화 유형')

    # 시간 정보
    start_time = models.DateTimeField(verbose_name='시작 시간')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='종료 시간')
    duration_seconds = models.IntegerField(null=True, blank=True, verbose_name='소요 시간(초)')

    # 처리 결과
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS, verbose_name='상태')
    records_processed = models.IntegerField(default=0, verbose_name='처리 건수')
    records_success = models.IntegerField(default=0, verbose_name='성공 건수')
    records_failed = models.IntegerField(default=0, verbose_name='실패 건수')

    # 데이터 유형
    data_types = models.JSONField(default=list, verbose_name='데이터 유형')

    # 에러 정보
    error_message = models.TextField(blank=True, verbose_name='에러 메시지')
    error_details = models.JSONField(default=dict, verbose_name='에러 상세')

    # 기타
    triggered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='실행자'
    )
    notes = models.TextField(blank=True, verbose_name='비고')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')

    class Meta:
        db_table = 'integration_histories'
        verbose_name = '연계 이력'
        verbose_name_plural = '연계 이력'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.sync_id} - {self.integration.name}"


class ManualQualityInput(models.Model):
    """자체 입력 모델 (품질 검사 데이터)"""

    class InspectionType(models.TextChoices):
        INCOMING = 'INCOMING', '입고 검사'
        PROCESS = 'PROCESS', '공정 검사'
        FINAL = 'FINAL', '최종 검사'
        OUTGOING = 'OUTGOING', '출하 검사'

    class Status(models.TextChoices):
        PENDING = 'PENDING', '대기'
        APPROVED = 'APPROVED', '승인'
        REJECTED = 'REJECTED', '반려'

    record_number = models.CharField(max_length=50, unique=True, verbose_name='기록 번호')
    inspection_type = models.CharField(max_length=20, choices=InspectionType.choices, verbose_name='검사 유형')
    inspection_date = models.DateField(verbose_name='검사일')

    # 제품 정보
    product_code = models.CharField(max_length=50, verbose_name='제품 코드')
    product_name = models.CharField(max_length=200, verbose_name='제품명')
    batch_number = models.CharField(max_length=50, blank=True, verbose_name='배치 번호')
    lot_number = models.CharField(max_length=50, blank=True, verbose_name='LOT 번호')

    # 검사 데이터
    sample_size = models.IntegerField(verbose_name='표본 수')
    defect_count = models.IntegerField(default=0, verbose_name='불량 수')
    defect_rate = models.FloatField(default=0, verbose_name='불량률(%)')

    # 검사 항목별 결과
    characteristics = models.JSONField(
        default=list,
        verbose_name='특성별 검사 결과',
        help_text='예: [{"name": "길이", "target": 100, "tolerance": 0.5, "measured": 100.1, "status": "OK"}]'
    )

    # 불량 상세
    defect_details = models.JSONField(
        default=list,
        verbose_name='불량 상세',
        help_text='예: [{"type": "긁힘", "count": 5, "description": "표면 긁힘"}]'
    )

    # 검사자 정보
    inspector = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='inspections',
        verbose_name='검사자'
    )
    department = models.CharField(max_length=100, verbose_name='부서')

    # 승인
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name='상태')
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_inspections',
        verbose_name='승인자'
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='승인일')

    # 비고
    notes = models.TextField(blank=True, verbose_name='비고')
    attachments = models.JSONField(default=list, verbose_name='첨부파일')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'manual_quality_inputs'
        verbose_name = '자체 입력'
        verbose_name_plural = '자체 입력'
        ordering = ['-inspection_date']

    def __str__(self):
        return f"{self.record_number} - {self.product_name}"
