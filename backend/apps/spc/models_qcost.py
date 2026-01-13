"""
Q-COST (Quality Cost) Models
품질코스트 관리를 위한 Django 모델
ERD 1-4: Q-COST / COPQ 도메인
"""

from django.db import models
from django.utils import timezone


class OrganizationSite(models.Model):
    """공장/사이트 정보 (org_site)"""
    site_id = models.AutoField(primary_key=True)
    site_name = models.CharField(max_length=200, unique=True)
    timezone = models.CharField(max_length=50, default='Asia/Seoul')
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'org_site'
        ordering = ['site_name']

    def __str__(self):
        return self.site_name


class OrganizationDepartment(models.Model):
    """부서 정보 (org_dept)"""
    dept_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='departments')
    dept_name = models.CharField(max_length=100)
    owner_user_id = models.IntegerField(null=True, blank=True)  # User 테이블과 연계 예정

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'org_dept'
        ordering = ['site', 'dept_name']

    def __str__(self):
        return f"{self.site.site_name} - {self.dept_name}"


class QCostCategory(models.Model):
    """품질코스트 분류체계 (qcost_category)"""
    LVL1_CHOICES = [
        ('PREVENTION', '예방비용'),
        ('APPRAISAL', '평가비용'),
        ('INTERNAL_FAILURE', '내부 실패비용'),
        ('EXTERNAL_FAILURE', '외부 실패비용'),
    ]

    qcat_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='qcost_categories')

    # 3단계 계층 구조
    lvl1 = models.CharField(max_length=50, choices=LVL1_CHOICES)  # 대분류
    lvl2 = models.CharField(max_length=100, blank=True)  # 중분류
    lvl3 = models.CharField(max_length=100, blank=True)  # 소분류

    code = models.CharField(max_length=20, unique=True)  # 예: P-01-001
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'qcost_category'
        ordering = ['lvl1', 'lvl2', 'lvl3']
        unique_together = [['site', 'code']]

    def __str__(self):
        return f"{self.code} - {self.name}"


class QCostItemMaster(models.Model):
    """품질코스트 항목 마스터 (qcost_item_master)"""
    UNIT_COST_RULE_CHOICES = [
        ('FIXED', '고정단가'),
        ('RATE', '율적용'),
        ('MANUAL', '수동입력'),
    ]

    qitem_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='qcost_items')
    category = models.ForeignKey(QCostCategory, on_delete=models.CASCADE, related_name='items')

    item_name = models.CharField(max_length=200)
    unit_cost_rule = models.CharField(max_length=20, choices=UNIT_COST_RULE_CHOICES)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    # 재무 연계
    gl_account = models.CharField(max_length=50, blank=True)  # 원가 계정
    dept = models.ForeignKey(OrganizationDepartment, on_delete=models.SET_NULL, null=True, blank=True)

    # COPQ 여부
    copq_flag = models.BooleanField(default=False, help_text='COPQ 대상 여부')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'qcost_item_master'
        ordering = ['category', 'item_name']

    def __str__(self):
        return f"{self.category.code} - {self.item_name}"


class QCostEntry(models.Model):
    """품질코스트 발생/수집 (qcost_entry)"""
    CURRENCY_CHOICES = [
        ('KRW', '원화'),
        ('USD', '달러'),
        ('EUR', '유로'),
        ('JPY', '엔'),
    ]

    entry_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='qcost_entries')
    item = models.ForeignKey(QCostItemMaster, on_delete=models.PROTECT, related_name='entries')
    dept = models.ForeignKey(OrganizationDepartment, on_delete=models.SET_NULL, null=True, blank=True)

    # 발생 정보
    occur_dt = models.DateTimeField(help_text='비용 발생일')
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default='KRW')
    qty = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='수량')

    # 연계 정보 (느슨한 연계)
    lot_id = models.IntegerField(null=True, blank=True, help_text='생산 LOT 연계')
    run_id = models.IntegerField(null=True, blank=True, help_text='검사 실행 연계')
    spc_event_id = models.IntegerField(null=True, blank=True, help_text='SPC 이벤트 연계')
    capa_id = models.IntegerField(null=True, blank=True, help_text='CAPA 연계')
    vendor_id = models.IntegerField(null=True, blank=True, help_text='협력사 연계')

    # 증빙 자료
    evidence_file_id = models.IntegerField(null=True, blank=True)
    memo = models.TextField(blank=True)

    # AI 자동분류
    ai_classification = models.JSONField(null=True, blank=True, help_text='AI 분류 결과: {category_id, confidence, reason}')
    ai_confidence = models.FloatField(null=True, blank=True, help_text='AI 분류 신뢰도 (0~1)')

    entered_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'qcost_entry'
        ordering = ['-occur_dt']
        indexes = [
            models.Index(fields=['site', 'occur_dt']),
            models.Index(fields=['item']),
            models.Index(fields=['dept']),
        ]

    def __str__(self):
        return f"{self.item.item_name}: {self.amount} {self.currency} ({self.occur_dt})"


class COPQSummary(models.Model):
    """COPQ 기간 집계 (copq_summary)"""
    copq_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='copq_summaries')

    # 집계 기간
    period_yyyymm = models.CharField(max_length=7, help_text='집계 기간 (YYYY-MM)')

    # 집계 데이터
    total_qcost = models.DecimalField(max_digits=18, decimal_places=2, help_text='총 품질비용')
    total_copq = models.DecimalField(max_digits=18, decimal_places=2, help_text='총 COPQ')
    sales_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    copq_rate = models.FloatField(help_text='COPQ율 (COPQ/매출액)')

    # 상세 내역 (JSON)
    by_category = models.JSONField(default=dict, help_text='카테고리별 집계')
    by_dept = models.JSONField(default=dict, help_text='부서별 집계')
    top_drivers = models.JSONField(default=list, help_text='주요 원인 항목')

    # AI 인사이트
    ai_insight_id = models.IntegerField(null=True, blank=True)
    ai_recommendation = models.TextField(blank=True)

    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'copq_summary'
        ordering = ['-period_yyyymm']
        unique_together = [['site', 'period_yyyymm']]

    def __str__(self):
        return f"{self.site.site_name} - {self.period_yyyymm}: COPQ {self.copq_rate}%"
