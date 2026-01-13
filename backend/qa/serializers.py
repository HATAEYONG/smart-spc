"""
QA Serializers
"""
from rest_framework import serializers


class QaProcessSerializer(serializers.Serializer):
    """QA Process Data Transfer Object"""
    qa_process_id = serializers.CharField(required=False)
    process_type = serializers.CharField(help_text="프로세스 유형 (AUDIT | ASSESSMENT | REVIEW)")
    title = serializers.CharField(help_text="제목")
    description = serializers.CharField(required=False, help_text="설명")
    scheduled_at = serializers.DateTimeField(required=False, help_text="예정일시")
    status = serializers.CharField(required=False, help_text="상태 (PLANNED | IN_PROGRESS | COMPLETED)")


class QaChecklistItemSerializer(serializers.Serializer):
    """QA Checklist Item Data Transfer Object"""
    item_id = serializers.CharField(required=False)
    qa_process_id = serializers.CharField(help_text="QA 프로세스 ID")
    check_point = serializers.CharField(help_text="체크포인트")
    requirement = serializers.CharField(help_text="요구사항")
    verification_method = serializers.CharField(required=False, help_text="검증 방법")


class QaAssessmentSerializer(serializers.Serializer):
    """QA Assessment Data Transfer Object"""
    assessment_id = serializers.CharField(required=False)
    qa_process_id = serializers.CharField(help_text="QA 프로세스 ID")
    assessed_at = serializers.DateTimeField(help_text="평가일시")
    assessed_by = serializers.CharField(help_text="평가자 ID")
    overall_score = serializers.FloatField(required=False, help_text="종합 점수")
    conclusion = serializers.CharField(required=False, help_text="결론")


class QaFindingSerializer(serializers.Serializer):
    """QA Finding Data Transfer Object"""
    finding_id = serializers.CharField(required=False)
    qa_process_id = serializers.CharField(help_text="QA 프로세스 ID")
    severity = serializers.CharField(help_text="심각도 (CRITICAL | MAJOR | MINOR)")
    description = serializers.CharField(help_text="설명")
    root_cause = serializers.CharField(required=False, help_text="근본 원인")
    corrective_action = serializers.CharField(required=False, help_text="시정 조치")


class CapaSerializer(serializers.Serializer):
    """CAPA Data Transfer Object"""
    capa_id = serializers.CharField(required=False)
    source_type = serializers.CharField(help_text="출처 유형 (COMPLAINT | AUDIT | OOS | SPD_EVENT)")
    source_id = serializers.CharField(help_text="출처 ID")
    title = serializers.CharField(help_text="제목")
    description = serializers.CharField(help_text="설명")
    severity = serializers.CharField(help_text="심각도 (CRITICAL | MAJOR | MINOR)")
    opened_at = serializers.DateTimeField(required=False, help_text="개설일")
    status = serializers.CharField(required=False, help_text="상태 (OPEN | IN_PROGRESS | VERIFICATION | CLOSED)")


class CapaActionSerializer(serializers.Serializer):
    """CAPA Action Data Transfer Object"""
    action_id = serializers.CharField(required=False)
    capa_id = serializers.CharField(help_text="CAPA ID")
    action_type = serializers.CharField(help_text="조치 유형 (CORRECTIVE | PREVENTIVE)")
    description = serializers.CharField(help_text="조치 설명")
    assignee = serializers.CharField(help_text="담당자 ID")
    due_date = serializers.DateField(help_text="목표일")
    status = serializers.CharField(required=False, help_text="상태 (PENDING | IN_PROGRESS | COMPLETED)")


class AIRootCauseCAPARequestSerializer(serializers.Serializer):
    """AI Root Cause Analysis Request"""
    problem_description = serializers.CharField(help_text="문제 설명")
    defect_details = serializers.CharField(help_text="불량 상세")
    context = serializers.CharField(required=False, help_text="추가 컨텍스트")


class AIRootCauseCAPAResponseSerializer(serializers.Serializer):
    """AI Root Cause Analysis Response"""
    root_cause = serializers.CharField(help_text="근본 원인")
    confidence = serializers.FloatField(help_text="신뢰도 (0-1)")
    recommended_corrective_actions = serializers.ListField(help_text="권장 시정 조치")
    recommended_preventive_actions = serializers.ListField(help_text="권장 예방 조치")
