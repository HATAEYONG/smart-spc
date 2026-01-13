"""
SPC Master Data Models
SPC 기본정보 그룹 - ERP/MES 연계

품질 관리를 위한 기준 정보 마스터
- 품목/공정/검사특성 마스터 (ERP 연계)
- 측정시스템/검사기구 마스터
- 검사기준/규격 마스터
"""
from django.db import models
from decimal import Decimal


# ============================================================================
# 1. 품질 마스터 (ERP 연계)
# ============================================================================

class QualityItemMaster(models.Model):
    """
    품질 품목 마스터 (ERP/MES 연계)

    ERP 품목 마스터에서 품질 관리가 필요한 품목을 연계
    """
    quality_item_id = models.AutoField(primary_key=True)
    itm_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="품목코드",
        help_text="ERP 품목코드와 연계"
    )
    itm_nm = models.CharField(max_length=200, verbose_name="품목명")
    itm_type = models.CharField(
        max_length=20,
        choices=[
            ('RAW_MATERIAL', '원자재'),
            ('WIP', '재공품'),
            ('FINISHED_GOOD', '완제품'),
            ('COMPONENT', '부품'),
        ],
        verbose_name="품목유형"
    )
    itm_family = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="품목패밀리"
    )

    # 품질 등급
    quality_grade = models.CharField(
        max_length=20,
        choices=[
            ('A', 'A급 - 핵심'),
            ('B', 'B급 - 일반'),
            ('C', 'C급 - 일반'),
        ],
        default='B',
        verbose_name="품질등급"
    )

    # 검사 유형
    inspection_type = models.CharField(
        max_length=20,
        choices=[
            ('FULL', '전수검사'),
            ('SAMPLING', '샘플링검사'),
            ('SKIP', 'Skip 검사'),
            ('NONE', '검사안함'),
        ],
        default='SAMPLING',
        verbose_name="검사유형"
    )

    # 샘플링 기준
    sampling_plan = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="샘플링기준",
        help_text="예: MIL-STD-105E, AQL=1.5"
    )
    sample_size = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="샘플크기"
    )
    sampling_frequency = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="샘플링빈도",
        help_text="예: 2시간말, 100개말"
    )

    # 공급자 정보
    supplier_code = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="공급자코드"
    )
    supplier_nm = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="공급자명"
    )

    # 관리 정보
    quality_manager = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="품질담당자"
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="비고"
    )

    active_yn = models.CharField(
        max_length=1,
        default="Y",
        verbose_name="사용여부"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    erp_sync_ts = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="ERP동기화시각"
    )

    class Meta:
        db_table = "quality_item_master"
        verbose_name = "품질품목마스터"
        verbose_name_plural = "품질품목마스터"
        indexes = [
            models.Index(fields=["itm_type"], name="ix_qitem_type"),
            models.Index(fields=["itm_family"], name="ix_qitem_family"),
            models.Index(fields=["quality_grade"], name="ix_qitem_grade"),
        ]
        ordering = ["itm_id"]

    def __str__(self):
        return f"{self.itm_id} - {self.itm_nm} ({self.get_quality_grade_display()})"


class QualityProcessMaster(models.Model):
    """
    품질 공정 마스터 (MES 연계)

    MES 공정 정보에서 품질 관리가 필요한 공정을 연계
    """
    process_id = models.AutoField(primary_key=True)
    process_cd = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        verbose_name="공정코드",
        help_text="MES 공정코드와 연계"
    )
    process_nm = models.CharField(max_length=200, verbose_name="공정명")

    # 공정 분류
    process_type = models.CharField(
        max_length=20,
        choices=[
            ('INCOMING', '수입검사'),
            ('PROCESS', '공정검사'),
            ('FINAL', '최종검사'),
            ('OUTGOING', '출하검사'),
        ],
        verbose_name="공정유형"
    )

    # 소속 정보
    workcenter_cd = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="작업장코드"
    )
    workcenter_nm = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="작업장명"
    )
    line_cd = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="라인코드"
    )

    # 공정 순서
    process_seq = models.IntegerField(
        default=1,
        verbose_name="공정순서"
    )

    # 관리 특성 수
    total_characteristics = models.IntegerField(
        default=0,
        verbose_name="관리특성수"
    )

    # 관리 정보
    process_manager = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="공정담당자"
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="비고"
    )

    active_yn = models.CharField(
        max_length=1,
        default="Y",
        verbose_name="사용여부"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    mes_sync_ts = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="MES동기화시각"
    )

    class Meta:
        db_table = "quality_process_master"
        verbose_name = "품질공정마스터"
        verbose_name_plural = "품질공정마스터"
        indexes = [
            models.Index(fields=["process_type"], name="ix_qproc_type"),
            models.Index(fields=["workcenter_cd"], name="ix_qproc_wc"),
            models.Index(fields=["line_cd"], name="ix_qproc_line"),
        ]
        ordering = ["process_cd"]

    def __str__(self):
        return f"{self.process_cd} - {self.process_nm} ({self.get_process_type_display()})"


class QualityCharacteristicMaster(models.Model):
    """
    품질 특성 마스터 (검사 항목)

    품질 관리를 위한 측정 특성(항목) 정의
    """
    characteristic_id = models.AutoField(primary_key=True)
    characteristic_cd = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        verbose_name="특성코드"
    )
    characteristic_nm = models.CharField(max_length=200, verbose_name="특성명")

    # 품목/공정 연계
    item = models.ForeignKey(
        QualityItemMaster,
        on_delete=models.CASCADE,
        related_name='characteristics',
        null=True,
        blank=True,
        verbose_name="품목"
    )
    process = models.ForeignKey(
        QualityProcessMaster,
        on_delete=models.CASCADE,
        related_name='characteristics',
        null=True,
        blank=True,
        verbose_name="공정"
    )

    # 특성 분류
    characteristic_type = models.CharField(
        max_length=20,
        choices=[
            ('DIMENSION', '치수'),
            ('WEIGHT', '중량'),
            ('VOLTAGE', '전압'),
            ('CURRENT', '전류'),
            ('TEMPERATURE', '온도'),
            ('PRESSURE', '압력'),
            ('VISUAL', '외관'),
            ('FUNCTIONAL', '기능'),
            ('OTHER', '기타'),
        ],
        verbose_name="특성유형"
    )

    data_type = models.CharField(
        max_length=20,
        choices=[
            ('CONTINUOUS', '연속형'),
            ('DISCRETE', '이산형'),
            ('ATTRIBUTE', '속성형'),
        ],
        default='CONTINUOUS',
        verbose_name="데이터유형"
    )

    # 측정 단위
    unit = models.CharField(
        max_length=20,
        verbose_name="측정단위",
        help_text="예: mm, g, V, A, ℃"
    )

    # 규격
    lsl = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="하한규격(LSL)"
    )
    target = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="목표치(Target)"
    )
    usl = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="상한규격(USL)"
    )

    # 공정능력 목표
    cpk_target = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.33'),
        verbose_name="Cpk목표"
    )
    cpk_minimum = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.00'),
        verbose_name="Cpk최소"
    )

    # 관리도 설정
    control_chart_type = models.CharField(
        max_length=20,
        choices=[
            ('XBAR_R', 'Xbar-R 관리도'),
            ('XBAR_S', 'Xbar-S 관리도'),
            ('I_MR', 'I-MR 관리도'),
            ('P', 'P 관리도'),
            ('NP', 'NP 관리도'),
            ('C', 'C 관리도'),
            ('U', 'U 관리도'),
        ],
        default='XBAR_R',
        verbose_name="관리도유형"
    )

    subgroup_size = models.IntegerField(
        default=5,
        verbose_name="부분군크기",
        help_text="Xbar-R: 일반적으로 3-5, I-MR: 1"
    )

    # 측정 방법
    measurement_method = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="측정방법"
    )
    measurement_location = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="측정위치"
    )

    # 관리 정보
    quality_manager = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="품질담당자"
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="비고"
    )

    active_yn = models.CharField(
        max_length=1,
        default="Y",
        verbose_name="사용여부"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "quality_characteristic_master"
        verbose_name = "품질특성마스터"
        verbose_name_plural = "품질특성마스터"
        indexes = [
            models.Index(fields=["item", "process"], name="ix_qchar_item_proc"),
            models.Index(fields=["characteristic_type"], name="ix_qchar_type"),
        ]
        ordering = ["characteristic_cd"]

    def __str__(self):
        return f"{self.characteristic_cd} - {self.characteristic_nm} ({self.unit})"


# ============================================================================
# 2. 측정 시스템 마스터
# ============================================================================

class MeasurementInstrumentMaster(models.Model):
    """
    측정기구 마스터

    품질 검사에 사용되는 모든 측정기구/장비 관리
    """
    instrument_id = models.AutoField(primary_key=True)
    instrument_cd = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        verbose_name="기구코드"
    )
    instrument_nm = models.CharField(max_length=200, verbose_name="기구명")

    # 기구 분류
    instrument_type = models.CharField(
        max_length=20,
        choices=[
            ('CALIPER', '노규자'),
            ('MICROMETER', '마이크로미터'),
            ('CMM', '3차원측정기'),
            ('SCALE', '저울'),
            ('MULTIMETER', '멀티미터'),
            ('OSCILLOSCOPE', '오실로스코프'),
            ('VISUAL', '육안검사'),
            ('OTHER', '기타'),
        ],
        verbose_name="기구유형"
    )

    # 제조사/모델
    manufacturer = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="제조사"
    )
    model_no = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="모델번호"
    )
    serial_no = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="일련번호"
    )

    # 측정 범위
    measurement_range_min = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="측정범위최소"
    )
    measurement_range_max = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="측정범위최대"
    )
    resolution = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="분해능"
    )
    unit = models.CharField(
        max_length=20,
        verbose_name="단위"
    )

    # 정밀도
    accuracy = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="정밀도",
        help_text="예: ±0.001mm"
    )

    # 보정 정보
    calibration_cycle = models.IntegerField(
        default=365,
        verbose_name="보정주기(일)"
    )
    last_calibration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="최종보정일"
    )
    next_calibration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="다음보정일"
    )
    calibration_institution = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="보정기관"
    )

    # 상태
    status = models.CharField(
        max_length=20,
        choices=[
            ('ACTIVE', '사용가능'),
            ('CALIBRATION_DUE', '보정만료'),
            ('MAINTENANCE', '정비중'),
            ('SCRAPPED', '폐기'),
        ],
        default='ACTIVE',
        verbose_name="상태"
    )

    # 소속 정보
    location = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="보관위치"
    )
    responsible_person = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="담당자"
    )

    # MSA 정보
    gage_rr_required = models.BooleanField(
        default=True,
        verbose_name="Gage R&R 필수"
    )
    gage_rr_last_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Gage R&R 실시일"
    )
    gage_rr_result = models.CharField(
        max_length=20,
        choices=[
            ('PASS', '적합'),
            ('FAIL', '부적합'),
            ('PENDING', '미실시'),
        ],
        default='PENDING',
        verbose_name="Gage R&R 결과"
    )

    # 비고
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="비고"
    )

    active_yn = models.CharField(
        max_length=1,
        default="Y",
        verbose_name="사용여부"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "measurement_instrument_master"
        verbose_name = "측정기구마스터"
        verbose_name_plural = "측정기구마스터"
        indexes = [
            models.Index(fields=["instrument_type"], name="ix_inst_type"),
            models.Index(fields=["status"], name="ix_inst_status"),
            models.Index(fields=["next_calibration_date"], name="ix_inst_cal"),
        ]
        ordering = ["instrument_cd"]

    def __str__(self):
        return f"{self.instrument_cd} - {self.instrument_nm} ({self.get_status_display()})"

    def is_calibration_due(self):
        """보정 만료 여부 확인"""
        from django.utils import timezone
        if self.next_calibration_date:
            return self.next_calibration_date <= timezone.now().date()
        return False


class MeasurementSystemMaster(models.Model):
    """
    측정 시스템 마스터

    여러 측정기구로 구성된 측정 시스템 정의
    """
    system_id = models.AutoField(primary_key=True)
    system_cd = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        verbose_name="시스템코드"
    )
    system_nm = models.CharField(max_length=200, verbose_name="시스템명")

    # 시스템 구성
    instruments = models.ManyToManyField(
        MeasurementInstrumentMaster,
        through='MeasurementSystemComponent',
        related_name='systems',
        verbose_name="구성기구"
    )

    # 측정 프로세스
    measurement_process = models.TextField(
        verbose_name="측정프로세스",
        help_text="측정 절차 및 방법"
    )

    # 환경 조건
    temperature_min = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="온도범위최소(℃)"
    )
    temperature_max = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="온도범위최대(℃)"
    )
    humidity_min = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="습도범위최소(%)"
    )
    humidity_max = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="습도범위최대(%)"
    )

    # 관리 정보
    system_manager = models.CharField(
        max_length=100,
        verbose_name="시스템담당자"
    )
    location = models.CharField(
        max_length=200,
        verbose_name="설치위치"
    )

    # MSA
    msa_method = models.CharField(
        max_length=20,
        choices=[
            ('GAGE_RR', 'Gage R&R'),
            ('GAGE_LINEARITY', 'Gage 선형성'),
            ('GAGE_STABILITY', 'Gage 안정성'),
            ('GAGE_BIAS', 'Gage 편향'),
        ],
        default='GAGE_RR',
        verbose_name="MSA 방법"
    )

    # 비고
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="비고"
    )

    active_yn = models.CharField(
        max_length=1,
        default="Y",
        verbose_name="사용여부"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "measurement_system_master"
        verbose_name = "측정시스템마스터"
        verbose_name_plural = "측정시스템마스터"
        ordering = ["system_cd"]

    def __str__(self):
        return f"{self.system_cd} - {self.system_nm}"


class MeasurementSystemComponent(models.Model):
    """
    측정 시스템 구성

    시스템별 구성 기구 및 역할
    """
    component_id = models.AutoField(primary_key=True)
    system = models.ForeignKey(
        MeasurementSystemMaster,
        on_delete=models.CASCADE,
        related_name='components',
        verbose_name="시스템"
    )
    instrument = models.ForeignKey(
        MeasurementInstrumentMaster,
        on_delete=models.CASCADE,
        related_name='system_components',
        verbose_name="기구"
    )

    component_role = models.CharField(
        max_length=50,
        verbose_name="구성역할",
        help_text="예: 주측정기, 보조측정기"
    )
    seq = models.IntegerField(
        default=1,
        verbose_name="순번"
    )

    # MSA 기여도
    ev_contribution = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="EV 기여도(%)",
        help_text="Equipment Variation 기여도"
    )

    class Meta:
        db_table = "measurement_system_component"
        verbose_name = "측정시스템구성"
        verbose_name_plural = "측정시스템구성"
        unique_together = (("system", "instrument"),)
        ordering = ["system", "seq"]

    def __str__(self):
        return f"{self.system.system_cd} - {self.instrument.instrument_nm}"


# ============================================================================
# 3. 검사 기준 마스터
# ============================================================================

class InspectionStandardMaster(models.Model):
    """
    검사 기준 마스터

    품목/특성별 검사 기준서
    """
    standard_id = models.AutoField(primary_key=True)
    standard_cd = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        verbose_name="기준코드"
    )
    standard_nm = models.CharField(max_length=200, verbose_name="기준명")

    # 적용 범위
    item = models.ForeignKey(
        QualityItemMaster,
        on_delete=models.CASCADE,
        related_name='standards',
        null=True,
        blank=True,
        verbose_name="품목"
    )
    characteristic = models.ForeignKey(
        QualityCharacteristicMaster,
        on_delete=models.CASCADE,
        related_name='standards',
        null=True,
        blank=True,
        verbose_name="특성"
    )

    # 기준 분류
    standard_type = models.CharField(
        max_length=20,
        choices=[
            ('INSPECTION', '검사기준'),
            ('TEST', '시험기준'),
            ('SPECIFICATION', '규격기준'),
            ('ACCEPTANCE', '합격판정기준'),
        ],
        verbose_name="기준유형"
    )

    # 검사 조건
    inspection_condition = models.TextField(
        null=True,
        blank=True,
        verbose_name="검사조건",
        help_text="온도, 습도, 전압 등 검사 환경 조건"
    )

    # 판정 기준
    acceptance_criteria = models.TextField(
        verbose_name="합격판정기준"
    )
    rejection_criteria = models.TextField(
        null=True,
        blank=True,
        verbose_name="불합격판정기준"
    )

    # 샘플링
    sampling_method = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="샘플링방법"
    )
    sample_size = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="샘플크기"
    )
    aql = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="AQL(%)"
    )

    # 시험 방법
    test_method = models.TextField(
        null=True,
        blank=True,
        verbose_name="시험방법"
    )
    test_equipment = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="시험장비"
    )

    # 참조 문서
    reference_doc = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="참조문서"
    )
    revision = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="개정번호"
    )
    effective_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="시행일자"
    )

    # 비고
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="비고"
    )

    active_yn = models.CharField(
        max_length=1,
        default="Y",
        verbose_name="사용여부"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inspection_standard_master"
        verbose_name = "검사기준마스터"
        verbose_name_plural = "검사기준마스터"
        indexes = [
            models.Index(fields=["item", "characteristic"], name="ix_std_item_char"),
            models.Index(fields=["standard_type"], name="ix_std_type"),
        ]
        ordering = ["standard_cd"]

    def __str__(self):
        return f"{self.standard_cd} - {self.standard_nm}"


# ============================================================================
# 4. ERP/MES 동기화 로그
# ============================================================================

class QualitySyncLog(models.Model):
    """
    품질 데이터 동기화 로그

    ERP/MES로부터 수신한 데이터 동기화 이력 관리
    """
    sync_id = models.AutoField(primary_key=True)
    sync_type = models.CharField(
        max_length=50,
        choices=[
            ('ITEM', '품목마스터'),
            ('PROCESS', '공정마스터'),
            ('CHARACTERISTIC', '특성마스터'),
            ('INSTRUMENT', '측정기구'),
            ('STANDARD', '검사기준'),
            ('MEASUREMENT', '측정데이터'),
        ],
        verbose_name="동기화유형"
    )
    sync_source = models.CharField(
        max_length=20,
        choices=[
            ('ERP', 'ERP'),
            ('MES', 'MES'),
            ('LEGACY', '레거시'),
            ('MANUAL', '수동입력'),
        ],
        verbose_name="데이터원천"
    )
    sync_status = models.CharField(
        max_length=20,
        choices=[
            ('SUCCESS', '성공'),
            ('FAILED', '실패'),
            ('PARTIAL', '부분성공'),
        ],
        verbose_name="동기화상태"
    )

    # 건수
    records_total = models.IntegerField(default=0, verbose_name="총건수")
    records_success = models.IntegerField(default=0, verbose_name="성공건수")
    records_failed = models.IntegerField(default=0, verbose_name="실패건수")

    # 상세 정보
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name="오류메시지"
    )
    sync_details = models.JSONField(
        null=True,
        blank=True,
        verbose_name="동기화상세",
        help_text="성공/실패 레코드 상세 정보"
    )

    # 소스 시스템 정보
    source_system = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="소스시스템"
    )
    source_file = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="소스파일"
    )

    # 시간
    sync_start_ts = models.DateTimeField(verbose_name="동기화시작시각")
    sync_end_ts = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="동기화종료시각"
    )
    sync_ts = models.DateTimeField(auto_now_add=True, verbose_name="동기화시각")

    class Meta:
        db_table = "quality_sync_log"
        verbose_name = "품질데이터동기화로그"
        verbose_name_plural = "품질데이터동기화로그"
        indexes = [
            models.Index(fields=["sync_type", "-sync_ts"], name="ix_qsync_type_ts"),
            models.Index(fields=["sync_source", "-sync_ts"], name="ix_qsync_src_ts"),
            models.Index(fields=["sync_status"], name="ix_qsync_status"),
        ]
        ordering = ["-sync_ts"]

    def __str__(self):
        return f"[{self.sync_type}] {self.sync_status} - {self.sync_ts}"

    @property
    def duration_seconds(self):
        """동기화 소요 시간 (초)"""
        if self.sync_end_ts and self.sync_start_ts:
            return (self.sync_end_ts - self.sync_start_ts).total_seconds()
        return None
