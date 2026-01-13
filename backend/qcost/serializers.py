"""
Q-COST Serializers
"""
from rest_framework import serializers


class QCostCategorySerializer(serializers.Serializer):
    """Q-COST Category Data Transfer Object"""
    category_id = serializers.CharField(required=False)
    category_type = serializers.CharField(help_text="PREVENTION | APPRAISAL | INTERNAL_FAILURE | EXTERNAL_FAILURE")
    name = serializers.CharField(help_text="카테고리명")
    description = serializers.CharField(required=False, allow_blank=True, help_text="설명")


class QCostItemSerializer(serializers.Serializer):
    """Q-COST Item Data Transfer Object"""
    item_id = serializers.CharField(required=False)
    category_id = serializers.CharField(help_text="카테고리 ID")
    code = serializers.CharField(help_text="아이템 코드")
    name = serializers.CharField(help_text="아이템명")
    unit = serializers.CharField(required=False, help_text="단위")
    is_active = serializers.BooleanField(default=True, help_text="활성화 여부")


class QCostEntrySerializer(serializers.Serializer):
    """Q-COST Entry Data Transfer Object"""
    entry_id = serializers.CharField(required=False)
    item_id = serializers.CharField(help_text="아이템 ID")
    occurred_at = serializers.DateTimeField(help_text="발생 일시")
    quantity = serializers.FloatField(help_text="수량")
    unit_cost = serializers.IntegerField(help_text="단가")
    total_cost = serializers.IntegerField(help_text="총비용 (quantity * unit_cost)")
    reference_id = serializers.CharField(required=False, allow_blank=True, help_text="참조 ID (검사번호 등)")
    notes = serializers.CharField(required=False, allow_blank=True, help_text="비고")


class AIQCostClassifyRequestSerializer(serializers.Serializer):
    """AI Q-COST Classification Request"""
    description = serializers.CharField(help_text="비용 발생 상세 설명")
    amount = serializers.IntegerField(help_text="비용 금액")
    context = serializers.CharField(required=False, allow_blank=True, help_text="추가 컨텍스트 (공정, 제품 등)")


class AIQCostClassifyResponseSerializer(serializers.Serializer):
    """AI Q-COST Classification Response"""
    suggested_category_id = serializers.CharField(help_text="제안된 카테고리 ID")
    suggested_item_id = serializers.CharField(help_text="제안된 아이템 ID (존재하는 경우)")
    confidence = serializers.FloatField(help_text="신뢰도 (0-1)")
    reasoning = serializers.CharField(help_text="분류 사유")


class COPQReportRequestSerializer(serializers.Serializer):
    """COPQ Report Request"""
    from_date = serializers.DateField(help_text="시작일 (YYYY-MM-DD)")
    to_date = serializers.DateField(help_text="종료일 (YYYY-MM-DD)")
    group_by = serializers.CharField(required=False, default="category", help_text="그룹핑 기준 (category | item | defect_type)")


class COPQReportResponseSerializer(serializers.Serializer):
    """COPQ Report Response"""
    total_copq = serializers.IntegerField(help_text="총 COPQ")
    breakdown = serializers.ListField(help_text="상세 내역")
    trend = serializers.ListField(help_text="추세 데이터")
