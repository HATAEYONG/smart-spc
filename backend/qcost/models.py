"""
Q-COST Models - QCOST-01/02
"""
from django.db import models


class QCostCategory(models.Model):
    """Q-COST 카테고리 모델"""
    CATEGORY_TYPES = [
        ('PREVENTION', '예방 비용'),
        ('APPRAISAL', '평가 비용'),
        ('INTERNAL_FAILURE', '내부 실패 비용'),
        ('EXTERNAL_FAILURE', '외부 실패 비용'),
    ]

    category_id = models.CharField(max_length=50, unique=True, help_text="카테고리 ID")
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES, help_text="카테고리 유형")
    name = models.CharField(max_length=100, help_text="카테고리명")
    description = models.TextField(blank=True, help_text="설명")
    is_active = models.BooleanField(default=True, help_text="활성화 여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'qcost_category'
        verbose_name = 'Q-COST Category'
        verbose_name_plural = 'Q-COST Categories'
        ordering = ['category_type', 'name']

    def __str__(self):
        return f"{self.category_type} - {self.name}"


class QCostItem(models.Model):
    """Q-COST 아이템 모델"""
    item_id = models.CharField(max_length=50, unique=True, help_text="아이템 ID")
    category = models.ForeignKey(QCostCategory, on_delete=models.CASCADE, related_name='items', help_text="카테고리")
    code = models.CharField(max_length=20, help_text="아이템 코드")
    name = models.CharField(max_length=100, help_text="아이템명")
    unit = models.CharField(max_length=20, blank=True, help_text="단위")
    is_active = models.BooleanField(default=True, help_text="활성화 여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'qcost_item'
        verbose_name = 'Q-COST Item'
        verbose_name_plural = 'Q-COST Items'
        ordering = ['category', 'code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class QCostEntry(models.Model):
    """Q-COST 엔트리 모델"""
    entry_id = models.CharField(max_length=50, unique=True, help_text="엔트리 ID")
    item = models.ForeignKey(QCostItem, on_delete=models.CASCADE, related_name='entries', help_text="아이템")
    occurred_at = models.DateTimeField(help_text="발생 일시")
    quantity = models.FloatField(help_text="수량")
    unit_cost = models.IntegerField(help_text="단가")
    total_cost = models.IntegerField(help_text="총비용")
    reference_id = models.CharField(max_length=50, blank=True, help_text="참조 ID")
    notes = models.TextField(blank=True, help_text="비고")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'qcost_entry'
        verbose_name = 'Q-COST Entry'
        verbose_name_plural = 'Q-COST Entries'
        ordering = ['-occurred_at']

    def __str__(self):
        return f"{self.entry_id} - {self.total_cost}"


class AIClassificationHistory(models.Model):
    """AI 분류 기록 모델"""
    classification_id = models.CharField(max_length=50, unique=True, help_text="분류 ID")
    description = models.TextField(help_text="비용 발생 상세 설명")
    amount = models.IntegerField(help_text="비용 금액")
    context = models.TextField(blank=True, help_text="추가 컨텍스트")
    suggested_category = models.ForeignKey(QCostCategory, on_delete=models.SET_NULL, null=True, related_name='ai_classifications', help_text="제안된 카테고리")
    suggested_item = models.ForeignKey(QCostItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_classifications', help_text="제안된 아이템")
    confidence = models.FloatField(help_text="신뢰도 (0-1)")
    reasoning = models.TextField(help_text="분류 사유")
    is_applied = models.BooleanField(default=False, help_text="적용 여부")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_classification_history'
        verbose_name = 'AI Classification History'
        verbose_name_plural = 'AI Classification Histories'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.classification_id} - {self.confidence}"
