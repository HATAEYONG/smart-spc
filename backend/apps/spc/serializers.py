from rest_framework import serializers
from .models import (
    Product, InspectionPlan, QualityMeasurement, ControlChart,
    ProcessCapability, RunRuleViolation, QualityAlert, QualityReport
)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class InspectionPlanSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_code = serializers.CharField(source='product.product_code', read_only=True)

    class Meta:
        model = InspectionPlan
        fields = '__all__'


class QualityMeasurementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_code = serializers.CharField(source='product.product_code', read_only=True)

    class Meta:
        model = QualityMeasurement
        fields = '__all__'


class QualityMeasurementCreateSerializer(serializers.ModelSerializer):
    """측정 데이터 생성용 Serializer (자동 판정 포함)"""

    class Meta:
        model = QualityMeasurement
        fields = '__all__'

    def create(self, validated_data):
        product = validated_data['product']

        # 규격 내 판정
        value = validated_data['measurement_value']
        validated_data['is_within_spec'] = product.lsl <= value <= product.usl

        # 관리 한계 판정은 나중에 SPC 서비스에서 수행
        validated_data['is_within_control'] = True

        return super().create(validated_data)


class ControlChartSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_code = serializers.CharField(source='product.product_code', read_only=True)

    class Meta:
        model = ControlChart
        fields = '__all__'


class ProcessCapabilitySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_code = serializers.CharField(source='product.product_code', read_only=True)

    class Meta:
        model = ProcessCapability
        fields = '__all__'


class RunRuleViolationSerializer(serializers.ModelSerializer):
    product_code = serializers.CharField(source='measurement.product.product_code', read_only=True)
    chart_type = serializers.CharField(source='control_chart.chart_type', read_only=True)
    measurement_value = serializers.FloatField(source='measurement.measurement_value', read_only=True)

    class Meta:
        model = RunRuleViolation
        fields = '__all__'


class QualityAlertSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_code = serializers.CharField(source='product.product_code', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)

    class Meta:
        model = QualityAlert
        fields = '__all__'


class QualityAlertUpdateSerializer(serializers.ModelSerializer):
    """경고 상태 업데이트용 Serializer"""

    class Meta:
        model = QualityAlert
        fields = ['status', 'assigned_to', 'acknowledged_by', 'resolved_by',
                  'resolution_notes', 'root_cause', 'corrective_action', 'preventive_action']


class QualityReportSerializer(serializers.ModelSerializer):
    products_data = ProductSerializer(source='products', many=True, read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)

    class Meta:
        model = QualityReport
        fields = '__all__'


class ControlChartDataSerializer(serializers.Serializer):
    """관리도 시각화 데이터 직렬화"""
    subgroup_number = serializers.IntegerField()
    xbar = serializers.FloatField(required=False)
    r = serializers.FloatField(required=False)
    s = serializers.FloatField(required=False)
    individual = serializers.FloatField(required=False)
    moving_range = serializers.FloatField(required=False)
    p = serializers.FloatField(required=False)
    np_value = serializers.FloatField(required=False)
    c = serializers.FloatField(required=False)
    u = serializers.FloatField(required=False)
    measured_at = serializers.DateTimeField()


class ProcessCapabilityAnalysisSerializer(serializers.Serializer):
    """공정능력 분석 요청 Serializer"""
    product_id = serializers.IntegerField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    chart_type = serializers.ChoiceField(choices=['XBAR_R', 'XBAR_S', 'I_MR'])


class ChatRequestSerializer(serializers.Serializer):
    """AI 챗봇 요청 Serializer"""
    message = serializers.CharField(help_text="사용자 메시지")
    product_id = serializers.IntegerField(required=False, help_text="제품 ID (선택)")
    session_id = serializers.CharField(required=False, help_text="세션 ID (선택)")


class ChatResponseSerializer(serializers.Serializer):
    """AI 챗봇 응답 Serializer"""
    response = serializers.CharField(help_text="챗봇 응답 메시지")
    intent = serializers.CharField(help_text="감지된 의도")
    context = serializers.JSONField(help_text="추가 컨텍스트 데이터")
    suggestions = serializers.ListField(
        child=serializers.CharField(),
        help_text="추천 질문/액션",
        required=False
    )


# Time Series Analysis Serializers
class TimeSeriesAnalysisRequestSerializer(serializers.Serializer):
    """시계열 분석 요청 Serializer"""
    product_id = serializers.IntegerField(help_text="제품 ID")
    days = serializers.IntegerField(default=30, help_text="분석 기간 (일)")
    forecast_steps = serializers.IntegerField(default=5, help_text="예측 스텝 수")


class TimeSeriesAnalysisResponseSerializer(serializers.Serializer):
    """시계열 분석 응답 Serializer"""
    product_id = serializers.IntegerField()
    product_code = serializers.CharField()
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
    data_points = serializers.IntegerField()
    trend_analysis = serializers.DictField()
    seasonality = serializers.DictField(required=False)
    decomposition = serializers.DictField(required=False)
    forecast = serializers.DictField()
    anomalies = serializers.ListField(child=serializers.DictField())
    analyzed_at = serializers.DateTimeField()


class ForecastRequestSerializer(serializers.Serializer):
    """예측 요청 Serializer"""
    product_id = serializers.IntegerField(help_text="제품 ID")
    days = serializers.IntegerField(default=30, help_text="학습 데이터 기간 (일)")
    forecast_steps = serializers.IntegerField(default=5, help_text="예측 스텝 수")
    method = serializers.ChoiceField(
        choices=['MA', 'ES', 'LT', 'COMBINED'],
        default='COMBINED',
        help_text="예측 방법 ( MA=이동평균, ES=지수평활, LT=선형추세, COMBINED=앙상블 )"
    )


class ForecastResponseSerializer(serializers.Serializer):
    """예측 응답 Serializer"""
    product_id = serializers.IntegerField()
    product_code = serializers.CharField()
    method = serializers.CharField()
    forecast_steps = serializers.IntegerField()
    forecast_values = serializers.ListField(child=serializers.FloatField())
    forecast_dates = serializers.ListField()
    confidence_interval = serializers.DictField(required=False)
    accuracy_metrics = serializers.DictField()
    forecasted_at = serializers.DateTimeField()


class PredictiveMaintenanceRequestSerializer(serializers.Serializer):
    """예지 보전 요청 Serializer"""
    product_id = serializers.IntegerField(help_text="제품 ID")
    days = serializers.IntegerField(default=30, help_text="분석 기간 (일)")


class PredictiveMaintenanceResponseSerializer(serializers.Serializer):
    """예지 보전 응답 Serializer"""
    product_id = serializers.IntegerField()
    product_code = serializers.CharField()
    equipment_health = serializers.DictField()
    degradation_analysis = serializers.DictField()
    failure_prediction = serializers.DictField()
    recommendations = serializers.ListField(child=serializers.CharField())
    analyzed_at = serializers.DateTimeField()


class AnomalyDetectionRequestSerializer(serializers.Serializer):
    """이상 감지 요청 Serializer"""
    product_id = serializers.IntegerField(help_text="제품 ID")
    days = serializers.IntegerField(default=30, help_text="분석 기간 (일)")
    threshold = serializers.FloatField(default=3.0, help_text="Z-score 임계값")


class AnomalyDetectionResponseSerializer(serializers.Serializer):
    """이상 감지 응답 Serializer"""
    product_id = serializers.IntegerField()
    product_code = serializers.CharField()
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
    total_data_points = serializers.IntegerField()
    anomalies = serializers.ListField(child=serializers.DictField())
    anomaly_count = serializers.IntegerField()
    anomaly_rate = serializers.FloatField()
    detection_method = serializers.CharField()
    threshold = serializers.FloatField()
    detected_at = serializers.DateTimeField()


# AI Prompt System Serializers
class AIPromptRequestSerializer(serializers.Serializer):
    """AI 프롬프트 요청 Serializer"""
    use_case = serializers.ChoiceField(
        choices=['PROCESS_DESIGN', 'CRITERIA_CHECKLIST', 'QCOST_CLASSIFY', 'COPQ_REPORT'],
        help_text="사용 케이스"
    )
    inputs = serializers.JSONField(help_text="입력 데이터 (JSON)")
    language = serializers.CharField(default='ko', help_text="언어 (ko/en/zh)")


class AIPromptResponseSerializer(serializers.Serializer):
    """AI 프롬프트 응답 Serializer"""
    use_case = serializers.CharField()
    prompt_name = serializers.CharField()
    version = serializers.CharField()
    formatted_prompt = serializers.CharField()
    input_schema = serializers.JSONField()
    output_schema = serializers.JSONField()


class AIPromptExecuteSerializer(serializers.Serializer):
    """AI 실행 요청 Serializer"""
    use_case = serializers.ChoiceField(
        choices=['PROCESS_DESIGN', 'CRITERIA_CHECKLIST', 'QCOST_CLASSIFY', 'COPQ_REPORT'],
        help_text="사용 케이스"
    )
    inputs = serializers.JSONField(help_text="입력 데이터")
    language = serializers.CharField(default='ko', help_text="언어")
    model_name = serializers.CharField(default='gpt-4', help_text="모델 이름")


class AIPromptExecuteResponseSerializer(serializers.Serializer):
    """AI 실행 응답 Serializer"""
    use_case = serializers.CharField()
    ai_output_id = serializers.IntegerField()
    output_json = serializers.JSONField()
    confidence = serializers.FloatField()
    model_name = serializers.CharField()
    created_at = serializers.DateTimeField()
