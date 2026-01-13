"""
SPC Serializers
"""
from rest_framework import serializers


class SamplingRuleSerializer(serializers.Serializer):
    """Sampling Rule Data Transfer Object"""
    standard = serializers.CharField(help_text="표준 (MIL-STD-105E, ISO 2859-1, etc.)")
    aql = serializers.FloatField(help_text="AQL 수준")
    lot_size = serializers.IntegerField(help_text="로트 크기")
    sample_size = serializers.IntegerField(help_text="표본 크기")
    accept_limit = serializers.IntegerField(help_text="합격 판정 개수")
    reject_limit = serializers.IntegerField(help_text="불합격 판정 개수")


class SpcChartDefSerializer(serializers.Serializer):
    """SPC Chart Definition Data Transfer Object"""
    chart_def_id = serializers.CharField(required=False)
    parameter_id = serializers.CharField(help_text="파라미터 ID")
    chart_type = serializers.CharField(help_text="관리도 종류 (XBAR_R, XBAR_S, I_MR, P, NP, U, C)")
    sample_size = serializers.IntegerField(required=False, help_text="표본 크기 (n)")
    ucl = serializers.FloatField(required=False, help_text="상한 (UCL)")
    cl = serializers.FloatField(required=False, help_text="중심선 (CL)")
    lcl = serializers.FloatField(required=False, help_text="하한 (LCL)")


class SpcPointSerializer(serializers.Serializer):
    """SPC Point Data Transfer Object"""
    point_id = serializers.CharField(required=False)
    chart_def_id = serializers.CharField(help_text="관리도 정의 ID")
    timestamp = serializers.DateTimeField(help_text="측정일시")
    sample_id = serializers.CharField(help_text="표본 ID")
    value = serializers.FloatField(help_text="측정값")
    mean = serializers.FloatField(required=False, help_text="평균 (Xbar)")
    range_val = serializers.FloatField(required=False, help_text="범위 (R)")
    violated_rules = serializers.JSONField(required=False, help_text="위반 규칙 목록 (JSON)")


class SpcEventSerializer(serializers.Serializer):
    """SPC Event Data Transfer Object"""
    event_id = serializers.CharField(required=False)
    chart_def_id = serializers.CharField(help_text="관리도 정의 ID")
    event_type = serializers.CharField(help_text="이벤트 유형 (OOS, RULE_1~RULE_8, TREND)")
    triggered_at = serializers.DateTimeField(help_text="발생일시")
    description = serializers.CharField(help_text="설명")
    severity = serializers.IntegerField(help_text="심각도 (1-5)")
    status = serializers.CharField(help_text="상태 (OPEN | INVESTIGATING | CLOSED)")


class SpcChartCreateRequestSerializer(serializers.Serializer):
    """SPC Chart Create Request"""
    parameter_id = serializers.CharField(help_text="파라미터 ID")
    chart_type = serializers.CharField(help_text="관리도 종류")
    sample_size = serializers.IntegerField(required=False)


class SpcRecalcResponseSerializer(serializers.Serializer):
    """SPC Recalculate Response"""
    chart_def_id = serializers.CharField(help_text="관리도 정의 ID")
    points_created = serializers.IntegerField(help_text="생성된 포인트 수")
    violations = serializers.IntegerField(help_text="발생한 위반 수")


class SpcEventCreateRequestSerializer(serializers.Serializer):
    """SPC Event Create Request"""
    chart_def_id = serializers.CharField(help_text="관리도 정의 ID")
    event_type = serializers.CharField(help_text="이벤트 유형")
    description = serializers.CharField(help_text="설명")
    severity = serializers.IntegerField(help_text="심각도 (1-5)")
