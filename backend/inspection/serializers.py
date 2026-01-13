"""
Inspection Serializers
"""
from rest_framework import serializers


class ProcessStepSerializer(serializers.Serializer):
    """Process Step Data Transfer Object"""
    step_id = serializers.CharField(required=False)
    step_order = serializers.IntegerField(help_text="순서")
    step_name = serializers.CharField(help_text="공정명")
    inspection_type = serializers.CharField(help_text="검사 유형 (IQC, IPQC, FQC, OQC)")
    criteria = serializers.JSONField(help_text="검사 기준 (JSON)")


class ProcessFlowSerializer(serializers.Serializer):
    """Process Flow Data Transfer Object"""
    flow_id = serializers.CharField(required=False)
    product_id = serializers.CharField(help_text="제품 ID")
    version = serializers.CharField(help_text="버전")
    steps = ProcessStepSerializer(many=True, required=False, help_text="공정 단계들")
    is_active = serializers.BooleanField(default=True, help_text="활성화 여부")


class AIProcessDesignRequestSerializer(serializers.Serializer):
    """AI Process Design Request"""
    product_description = serializers.CharField(help_text="제품 설명")
    quality_requirements = serializers.CharField(help_text="품질 요구사항")
    production_volume = serializers.CharField(required=False, help_text="생산량 (대소구분)")


class AIProcessDesignResponseSerializer(serializers.Serializer):
    """AI Process Design Response"""
    proposed_flow = ProcessFlowSerializer(help_text="제안된 공정 흐름")
    confidence = serializers.FloatField(help_text="신뢰도 (0-1)")
    reasoning = serializers.CharField(help_text="설계 사유")


class AICriteriaChecklistRequestSerializer(serializers.Serializer):
    """AI Criteria Checklist Request"""
    process_step_description = serializers.CharField(help_text="공정 단계 설명")
    quality_standard = serializers.CharField(help_text="품질 표준")


class AICriteriaChecklistResponseSerializer(serializers.Serializer):
    """AI Criteria Checklist Response"""
    criteria = serializers.JSONField(help_text="생성된 검사 기준 (JSON)")
    confidence = serializers.FloatField(help_text="신뢰도 (0-1)")
    rationale = serializers.CharField(help_text="근거")


class InspectionRunSerializer(serializers.Serializer):
    """Inspection Run Data Transfer Object"""
    run_id = serializers.CharField(required=False)
    flow_id = serializers.CharField(help_text="공정 흐름 ID")
    run_type = serializers.CharField(help_text="실시 유형 (NORMAL | R&A | RED_TAG)")
    started_at = serializers.DateTimeField(required=False, help_text="시작일시")
    status = serializers.CharField(required=False, help_text="상태 (OPEN | CLOSED | JUDGED)")
    inspector_id = serializers.CharField(help_text="검사원 ID")


class BulkResultRequestSerializer(serializers.Serializer):
    """Bulk Inspection Results Request"""
    results = serializers.JSONField(help_text="검사 결과 목록 (JSON)")


class BulkResultResponseSerializer(serializers.Serializer):
    """Bulk Inspection Results Response"""
    inserted = serializers.IntegerField(help_text="입력 건수")
    oos_count = serializers.IntegerField(help_text="불합격 건수")


class InspectionJudgeResponseSerializer(serializers.Serializer):
    """Inspection Judge Response"""
    run_id = serializers.CharField(help_text="실시 ID")
    judgment = serializers.CharField(help_text="판정 (ACCEPT | REJECT | REWORK)")
    judged_at = serializers.DateTimeField(help_text="판정일시")
