"""
품질 이슈 추적 시스템 모델
4M 분석 및 8단계 문제 해결
"""
from django.db import models
from django.contrib.auth.models import User


class QualityIssue(models.Model):
    """품질 이슈 모델"""

    class Status(models.TextChoices):
        OPEN = 'OPEN', '접수'
        INVESTIGATING = 'INVESTIGATING', '조사중'
        IN_PROGRESS = 'IN_PROGRESS', '진행중'
        RESOLVED = 'RESOLVED', '해결'
        CLOSED = 'CLOSED', '종결'

    class Severity(models.TextChoices):
        LOW = 'LOW', '낮음'
        MEDIUM = 'MEDIUM', '중간'
        HIGH = 'HIGH', '높음'
        CRITICAL = 'CRITICAL', '긴급'

    issue_number = models.CharField(max_length=50, unique=True, verbose_name='이슈 번호')
    title = models.CharField(max_length=200, verbose_name='제목')
    description = models.TextField(verbose_name='설명')
    product_code = models.CharField(max_length=50, verbose_name='제품 코드')
    product_name = models.CharField(max_length=200, verbose_name='제품명')
    defect_type = models.CharField(max_length=100, verbose_name='불량 유형')
    severity = models.CharField(max_length=20, choices=Severity.choices, verbose_name='중요도')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, verbose_name='상태')
    reported_date = models.DateTimeField(auto_now_add=True, verbose_name='보고일')
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_issues', verbose_name='보고자')
    department = models.CharField(max_length=100, verbose_name='부서')
    defect_quantity = models.IntegerField(default=0, verbose_name='불량 수량')
    cost_impact = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='비용 영향')
    responsible_person = models.CharField(max_length=100, blank=True, verbose_name='담당자')
    target_resolution_date = models.DateField(verbose_name='목표 해결일')
    actual_resolution_date = models.DateField(null=True, blank=True, verbose_name='실제 해결일')
    completion_notes = models.TextField(blank=True, verbose_name='완료 메모')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'quality_issues'
        verbose_name = '품질 이슈'
        verbose_name_plural = '품질 이슈'
        ordering = ['-reported_date']

    def __str__(self):
        return f"{self.issue_number} - {self.title}"


class IssueAnalysis4M(models.Model):
    """4M 분석 모델"""

    class Category(models.TextChoices):
        MAN = 'MAN', '사람'
        MACHINE = 'MACHINE', '설비'
        MATERIAL = 'MATERIAL', '자재'
        METHOD = 'METHOD', '방법'

    issue = models.ForeignKey(QualityIssue, on_delete=models.CASCADE, related_name='analyses_4m', verbose_name='품질 이슈')
    category = models.CharField(max_length=20, choices=Category.choices, verbose_name='카테고리')
    description = models.TextField(verbose_name='분석 내용')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')

    class Meta:
        db_table = 'issue_analysis_4m'
        verbose_name = '4M 분석'
        verbose_name_plural = '4M 분석'

    def __str__(self):
        return f"{self.issue.issue_number} - {self.get_category_display()}"


class ProblemSolvingStep(models.Model):
    """8단계 문제 해결 모델"""

    issue = models.ForeignKey(QualityIssue, on_delete=models.CASCADE, related_name='solving_steps', verbose_name='품질 이슈')
    step_number = models.IntegerField(verbose_name='단계')
    step_name = models.CharField(max_length=100, verbose_name='단계명')
    content = models.TextField(verbose_name='내용')
    completed = models.BooleanField(default=False, verbose_name='완료 여부')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='완료일')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'problem_solving_steps'
        verbose_name = '문제 해결 단계'
        verbose_name_plural = '문제 해결 단계'
        ordering = ['step_number']

    def __str__(self):
        return f"{self.issue.issue_number} - {self.step_number}. {self.step_name}"
