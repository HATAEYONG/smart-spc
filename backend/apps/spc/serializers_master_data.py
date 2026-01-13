"""
SPC Master Data Serializers
품질 기본정보 시리얼라이저
"""
from rest_framework import serializers
from apps.spc.models_master_data import (
    QualityItemMaster,
    QualityProcessMaster,
    QualityCharacteristicMaster,
    MeasurementInstrumentMaster,
    MeasurementSystemMaster,
    MeasurementSystemComponent,
    InspectionStandardMaster,
    QualitySyncLog
)


# ============================================================================
# 1. 품질 마스터 시리얼라이저
# ============================================================================

class QualityItemMasterSerializer(serializers.ModelSerializer):
    """품질 품목 마스터 시리얼라이저"""

    class Meta:
        model = QualityItemMaster
        fields = [
            'quality_item_id',
            'itm_id',
            'itm_nm',
            'itm_type',
            'itm_family',
            'quality_grade',
            'inspection_type',
            'sampling_plan',
            'sample_size',
            'sampling_frequency',
            'supplier_code',
            'supplier_nm',
            'quality_manager',
            'notes',
            'active_yn',
            'created_at',
            'updated_at',
            'erp_sync_ts',
        ]
        read_only_fields = ['quality_item_id', 'created_at', 'updated_at']


class QualityItemMasterListSerializer(serializers.ModelSerializer):
    """품질 품목 마스터 목록 시리얼라이저"""

    itm_type_display = serializers.CharField(source='get_itm_type_display', read_only=True)
    quality_grade_display = serializers.CharField(source='get_quality_grade_display', read_only=True)
    inspection_type_display = serializers.CharField(source='get_inspection_type_display', read_only=True)
    total_characteristics = serializers.IntegerField(source='characteristics.count', read_only=True)

    class Meta:
        model = QualityItemMaster
        fields = [
            'quality_item_id',
            'itm_id',
            'itm_nm',
            'itm_type',
            'itm_type_display',
            'itm_family',
            'quality_grade',
            'quality_grade_display',
            'inspection_type',
            'inspection_type_display',
            'sampling_plan',
            'sample_size',
            'total_characteristics',
            'active_yn',
            'erp_sync_ts',
        ]


class QualityProcessMasterSerializer(serializers.ModelSerializer):
    """품질 공정 마스터 시리얼라이저"""

    class Meta:
        model = QualityProcessMaster
        fields = [
            'process_id',
            'process_cd',
            'process_nm',
            'process_type',
            'workcenter_cd',
            'workcenter_nm',
            'line_cd',
            'process_seq',
            'total_characteristics',
            'process_manager',
            'notes',
            'active_yn',
            'created_at',
            'updated_at',
            'mes_sync_ts',
        ]
        read_only_fields = ['process_id', 'created_at', 'updated_at']


class QualityProcessMasterListSerializer(serializers.ModelSerializer):
    """품질 공정 마스터 목록 시리얼라이저"""

    process_type_display = serializers.CharField(source='get_process_type_display', read_only=True)
    total_characteristics = serializers.IntegerField(source='characteristics.count', read_only=True)

    class Meta:
        model = QualityProcessMaster
        fields = [
            'process_id',
            'process_cd',
            'process_nm',
            'process_type',
            'process_type_display',
            'workcenter_cd',
            'workcenter_nm',
            'line_cd',
            'process_seq',
            'total_characteristics',
            'active_yn',
            'mes_sync_ts',
        ]


class QualityCharacteristicMasterSerializer(serializers.ModelSerializer):
    """품질 특성 마스터 시리얼라이저"""

    item_nm = serializers.CharField(source='item.itm_nm', read_only=True)
    process_nm = serializers.CharField(source='process.process_nm', read_only=True)
    characteristic_type_display = serializers.CharField(source='get_characteristic_type_display', read_only=True)
    data_type_display = serializers.CharField(source='get_data_type_display', read_only=True)
    control_chart_type_display = serializers.CharField(source='get_control_chart_type_display', read_only=True)

    class Meta:
        model = QualityCharacteristicMaster
        fields = [
            'characteristic_id',
            'characteristic_cd',
            'characteristic_nm',
            'item',
            'item_nm',
            'process',
            'process_nm',
            'characteristic_type',
            'characteristic_type_display',
            'data_type',
            'data_type_display',
            'unit',
            'lsl',
            'target',
            'usl',
            'cpk_target',
            'cpk_minimum',
            'control_chart_type',
            'control_chart_type_display',
            'subgroup_size',
            'measurement_method',
            'measurement_location',
            'quality_manager',
            'notes',
            'active_yn',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['characteristic_id', 'created_at', 'updated_at']


class QualityCharacteristicMasterListSerializer(serializers.ModelSerializer):
    """품질 특성 마스터 목록 시리얼라이저"""

    itm_id = serializers.CharField(source='item.itm_id', read_only=True)
    itm_nm = serializers.CharField(source='item.itm_nm', read_only=True)
    process_cd = serializers.CharField(source='process.process_cd', read_only=True)
    process_nm = serializers.CharField(source='process.process_nm', read_only=True)
    characteristic_type_display = serializers.CharField(source='get_characteristic_type_display', read_only=True)
    data_type_display = serializers.CharField(source='get_data_type_display', read_only=True)

    class Meta:
        model = QualityCharacteristicMaster
        fields = [
            'characteristic_id',
            'characteristic_cd',
            'characteristic_nm',
            'itm_id',
            'itm_nm',
            'process_cd',
            'process_nm',
            'characteristic_type',
            'characteristic_type_display',
            'data_type',
            'data_type_display',
            'unit',
            'lsl',
            'target',
            'usl',
            'cpk_target',
            'control_chart_type',
            'subgroup_size',
            'active_yn',
        ]


# ============================================================================
# 2. 측정 시스템 시리얼라이저
# ============================================================================

class MeasurementInstrumentMasterSerializer(serializers.ModelSerializer):
    """측정기구 마스터 시리얼라이저"""

    instrument_type_display = serializers.CharField(source='get_instrument_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    gage_rr_result_display = serializers.CharField(source='get_gage_rr_result_display', read_only=True)
    is_calibration_due = serializers.SerializerMethodField()

    class Meta:
        model = MeasurementInstrumentMaster
        fields = [
            'instrument_id',
            'instrument_cd',
            'instrument_nm',
            'instrument_type',
            'instrument_type_display',
            'manufacturer',
            'model_no',
            'serial_no',
            'measurement_range_min',
            'measurement_range_max',
            'resolution',
            'unit',
            'accuracy',
            'calibration_cycle',
            'last_calibration_date',
            'next_calibration_date',
            'calibration_institution',
            'status',
            'status_display',
            'location',
            'responsible_person',
            'gage_rr_required',
            'gage_rr_last_date',
            'gage_rr_result',
            'gage_rr_result_display',
            'notes',
            'active_yn',
            'created_at',
            'updated_at',
            'is_calibration_due',
        ]
        read_only_fields = ['instrument_id', 'created_at', 'updated_at']

    def get_is_calibration_due(self, obj):
        """보정 만료 여부"""
        return obj.is_calibration_due()


class MeasurementInstrumentMasterListSerializer(serializers.ModelSerializer):
    """측정기구 마스터 목록 시리얼라이저"""

    instrument_type_display = serializers.CharField(source='get_instrument_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_calibration_due = serializers.SerializerMethodField()

    class Meta:
        model = MeasurementInstrumentMaster
        fields = [
            'instrument_id',
            'instrument_cd',
            'instrument_nm',
            'instrument_type',
            'instrument_type_display',
            'manufacturer',
            'model_no',
            'serial_no',
            'unit',
            'status',
            'status_display',
            'next_calibration_date',
            'location',
            'gage_rr_result',
            'is_calibration_due',
            'active_yn',
        ]

    def get_is_calibration_due(self, obj):
        return obj.is_calibration_due()


class MeasurementSystemComponentSerializer(serializers.ModelSerializer):
    """측정 시스템 구성 시리얼라이저"""

    instrument_cd = serializers.CharField(source='instrument.instrument_cd', read_only=True)
    instrument_nm = serializers.CharField(source='instrument.instrument_nm', read_only=True)

    class Meta:
        model = MeasurementSystemComponent
        fields = [
            'component_id',
            'system',
            'instrument',
            'instrument_cd',
            'instrument_nm',
            'component_role',
            'seq',
            'ev_contribution',
        ]


class MeasurementSystemMasterSerializer(serializers.ModelSerializer):
    """측정 시스템 마스터 시리얼라이저"""

    msa_method_display = serializers.CharField(source='get_msa_method_display', read_only=True)
    components = MeasurementSystemComponentSerializer(
        source='system_components',
        many=True,
        read_only=True
    )
    instrument_count = serializers.IntegerField(source='instruments.count', read_only=True)

    class Meta:
        model = MeasurementSystemMaster
        fields = [
            'system_id',
            'system_cd',
            'system_nm',
            'instrument_count',
            'components',
            'measurement_process',
            'temperature_min',
            'temperature_max',
            'humidity_min',
            'humidity_max',
            'system_manager',
            'location',
            'msa_method',
            'msa_method_display',
            'notes',
            'active_yn',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['system_id', 'created_at', 'updated_at']


class MeasurementSystemMasterListSerializer(serializers.ModelSerializer):
    """측정 시스템 마스터 목록 시리얼라이저"""

    msa_method_display = serializers.CharField(source='get_msa_method_display', read_only=True)
    instrument_count = serializers.IntegerField(source='instruments.count', read_only=True)

    class Meta:
        model = MeasurementSystemMaster
        fields = [
            'system_id',
            'system_cd',
            'system_nm',
            'instrument_count',
            'system_manager',
            'location',
            'msa_method',
            'msa_method_display',
            'active_yn',
            'created_at',
        ]


# ============================================================================
# 3. 검사 기준 시리얼라이저
# ============================================================================

class InspectionStandardMasterSerializer(serializers.ModelSerializer):
    """검사 기준 마스터 시리얼라이저"""

    itm_id = serializers.CharField(source='item.itm_id', read_only=True)
    itm_nm = serializers.CharField(source='item.itm_nm', read_only=True)
    characteristic_cd = serializers.CharField(source='characteristic.characteristic_cd', read_only=True)
    characteristic_nm = serializers.CharField(source='characteristic.characteristic_nm', read_only=True)
    standard_type_display = serializers.CharField(source='get_standard_type_display', read_only=True)

    class Meta:
        model = InspectionStandardMaster
        fields = [
            'standard_id',
            'standard_cd',
            'standard_nm',
            'item',
            'itm_id',
            'itm_nm',
            'characteristic',
            'characteristic_cd',
            'characteristic_nm',
            'standard_type',
            'standard_type_display',
            'inspection_condition',
            'acceptance_criteria',
            'rejection_criteria',
            'sampling_method',
            'sample_size',
            'aql',
            'test_method',
            'test_equipment',
            'reference_doc',
            'revision',
            'effective_date',
            'notes',
            'active_yn',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['standard_id', 'created_at', 'updated_at']


class InspectionStandardMasterListSerializer(serializers.ModelSerializer):
    """검사 기준 마스터 목록 시리얼라이저"""

    itm_id = serializers.CharField(source='item.itm_id', read_only=True)
    itm_nm = serializers.CharField(source='item.itm_nm', read_only=True)
    characteristic_cd = serializers.CharField(source='characteristic.characteristic_cd', read_only=True)
    characteristic_nm = serializers.CharField(source='characteristic.characteristic_nm', read_only=True)
    standard_type_display = serializers.CharField(source='get_standard_type_display', read_only=True)

    class Meta:
        model = InspectionStandardMaster
        fields = [
            'standard_id',
            'standard_cd',
            'standard_nm',
            'itm_id',
            'itm_nm',
            'characteristic_cd',
            'characteristic_nm',
            'standard_type',
            'standard_type_display',
            'sample_size',
            'aql',
            'effective_date',
            'active_yn',
        ]


# ============================================================================
# 4. 동기화 로그 시리얼라이저
# ============================================================================

class QualitySyncLogSerializer(serializers.ModelSerializer):
    """품질 데이터 동기화 로그 시리얼라이저"""

    sync_type_display = serializers.CharField(source='get_sync_type_display', read_only=True)
    sync_source_display = serializers.CharField(source='get_sync_source_display', read_only=True)
    sync_status_display = serializers.CharField(source='get_sync_status_display', read_only=True)
    duration_seconds = serializers.FloatField(read_only=True)

    class Meta:
        model = QualitySyncLog
        fields = [
            'sync_id',
            'sync_type',
            'sync_type_display',
            'sync_source',
            'sync_source_display',
            'sync_status',
            'sync_status_display',
            'records_total',
            'records_success',
            'records_failed',
            'error_message',
            'sync_details',
            'source_system',
            'source_file',
            'sync_start_ts',
            'sync_end_ts',
            'duration_seconds',
            'sync_ts',
        ]
        read_only_fields = ['sync_id', 'sync_ts']


# ============================================================================
# 5. ERP/MES 연계 시리얼라이저 (Import용)
# ============================================================================

class ERPItemImportSerializer(serializers.Serializer):
    """ERP 품목 데이터 Import 시리얼라이저"""

    itm_id = serializers.CharField(max_length=50, help_text="품목코드")
    itm_nm = serializers.CharField(max_length=200, help_text="품목명")
    itm_type = serializers.CharField(required=False, default="FINISHED_GOOD", help_text="품목유형")
    itm_family = serializers.CharField(required=False, allow_blank=True, help_text="품목패밀리")
    quality_grade = serializers.CharField(required=False, default="B", help_text="품질등급")
    inspection_type = serializers.CharField(required=False, default="SAMPLING", help_text="검사유형")
    sampling_plan = serializers.CharField(required=False, allow_blank=True, help_text="샘플링기준")
    sample_size = serializers.IntegerField(required=False, help_text="샘플크기")
    sampling_frequency = serializers.CharField(required=False, allow_blank=True, help_text="샘플링빈도")
    supplier_code = serializers.CharField(required=False, allow_blank=True, help_text="공급자코드")
    supplier_nm = serializers.CharField(required=False, allow_blank=True, help_text="공급자명")
    quality_manager = serializers.CharField(required=False, allow_blank=True, help_text="품질담당자")
    notes = serializers.CharField(required=False, allow_blank=True, help_text="비고")


class MESProcessImportSerializer(serializers.Serializer):
    """MES 공정 데이터 Import 시리얼라이저"""

    process_cd = serializers.CharField(max_length=20, help_text="공정코드")
    process_nm = serializers.CharField(max_length=200, help_text="공정명")
    process_type = serializers.CharField(required=False, default="PROCESS", help_text="공정유형")
    workcenter_cd = serializers.CharField(required=False, allow_blank=True, help_text="작업장코드")
    workcenter_nm = serializers.CharField(required=False, allow_blank=True, help_text="작업장명")
    line_cd = serializers.CharField(required=False, allow_blank=True, help_text="라인코드")
    process_seq = serializers.IntegerField(required=False, default=1, help_text="공정순서")
    process_manager = serializers.CharField(required=False, allow_blank=True, help_text="공정담당자")
    notes = serializers.CharField(required=False, allow_blank=True, help_text="비고")


class ERPItemBatchImportSerializer(serializers.Serializer):
    """ERP 품목 일괄 Import 시리얼라이저"""

    items = ERPItemImportSerializer(many=True, help_text="품목 데이터 리스트")


class MESProcessBatchImportSerializer(serializers.Serializer):
    """MES 공정 일괄 Import 시리얼라이저"""

    processes = MESProcessImportSerializer(many=True, help_text="공정 데이터 리스트")
