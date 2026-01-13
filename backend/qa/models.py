"""
QA Models - QA-01/02/03
"""
from django.db import models


class QaProcess(models.Model):
    """QA 프로세스 모델"""
    PROCESS_TYPES = [
        ('AUDIT', '심사'),
        ('ASSESSMENT', '평가'),
        ('REVIEW', '리뷰'),
    ]

    STATUS_CHOICES = [
        ('PLANNED', '계획됨'),
        ('IN_PROGRESS', '진행 중'),
        ('COMPLETED', '완료됨'),
    ]

    qa_process_id = models.CharField(max_length=50, unique=True, help_text="QA 프로세스 ID")
    process_type = models.CharField(max_length=20, choices=PROCESS_TYPES, help_text="프로세스 유형")
    title = models.CharField(max_length=200, help_text="제목")
    description = models.TextField(blank=True, help_text="설명")
    scheduled_at = models.DateTimeField(help_text="예정일시")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED', help_text="상태")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'qa_process'
        verbose_name = 'QA Process'
        verbose_name_plural = 'QA Processes'
        ordering = ['-scheduled_at']

    def __str__(self):
        return f"{self.qa_process_id} - {self.title}"


class QaChecklistItem(models.Model):
    """QA 체크리스트 아이템 모델"""
    item_id = models.CharField(max_length=50, unique=True, help_text="아이템 ID")
    qa_process = models.ForeignKey(QaProcess, on_delete=models.CASCADE, related_name='checklist_items', help_text="QA 프로세스")
    check_point = models.CharField(max_length=200, help_text="체크포인트")
    requirement = models.TextField(help_text="요구사항")
    verification_method = models.TextField(blank=True, help_text="검증 방법")
    is_compliant = models.BooleanField(null=True, blank=True, help_text="준수 여부")
    notes = models.TextField(blank=True, help_text="비고")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'qa_checklist_item'
        verbose_name = 'QA Checklist Item'
        verbose_name_plural = 'QA Checklist Items'
        ordering = ['qa_process', 'id']

    def __str__(self):
        return f"{self.qa_process.qa_process_id} - {self.check_point}"


class QaAssessment(models.Model):
    """QA 평가 모델"""
    assessment_id = models.CharField(max_length=50, unique=True, help_text="평가 ID")
    qa_process = models.ForeignKey(QaProcess, on_delete=models.CASCADE, related_name='assessments', help_text="QA 프로세스")
    assessed_at = models.DateTimeField(help_text="평가일시")
    assessed_by = models.CharField(max_length=50, help_text="평가자 ID")
    overall_score = models.FloatField(help_text="종합 점수")
    conclusion = models.TextField(help_text="결론")
    recommendations = models.TextField(blank=True, help_text="권고사항")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'qa_assessment'
        verbose_name = 'QA Assessment'
        verbose_name_plural = 'QA Assessments'
        ordering = ['-assessed_at']

    def __str__(self):
        return f"{self.assessment_id} - {self.overall_score}"


class QaFinding(models.Model):
    """QA 발견사항 모델"""
    SEVERITY_CHOICES = [
        ('CRITICAL', '중대'),
        ('MAJOR', '주요'),
        ('MINOR', '경미'),
    ]

    finding_id = models.CharField(max_length=50, unique=True, help_text="발견사항 ID")
    qa_process = models.ForeignKey(QaProcess, on_delete=models.CASCADE, related_name='findings', help_text="QA 프로세스")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, help_text="심각도")
    description = models.TextField(help_text="설명")
    root_cause = models.TextField(blank=True, help_text="근본 원인")
    corrective_action = models.TextField(blank=True, help_text="시정 조치")
    is_resolved = models.BooleanField(default=False, help_text="해결 여부")
    resolved_at = models.DateTimeField(null=True, blank=True, help_text="해결일시")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'qa_finding'
        verbose_name = 'QA Finding'
        verbose_name_plural = 'QA Findings'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.finding_id} - {self.severity}"


class Capa(models.Model):
    """CAPA 모델"""
    SOURCE_TYPES = [
        ('COMPLAINT', '고객 불만'),
        ('AUDIT', '심사'),
        ('OOS', '규격 이탈'),
        ('SPC_EVENT', 'SPC 이벤트'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('VERIFICATION', 'Verification'),
        ('CLOSED', 'Closed'),
    ]

    SEVERITY_CHOICES = [
        ('CRITICAL', '중대'),
        ('MAJOR', '주요'),
        ('MINOR', '경미'),
    ]

    capa_id = models.CharField(max_length=50, unique=True, help_text="CAPA ID")
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES, help_text="출처 유형")
    source_id = models.CharField(max_length=50, help_text="출처 ID")
    title = models.CharField(max_length=200, help_text="제목")
    description = models.TextField(help_text="설명")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, help_text="심각도")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN', help_text="상태")
    opened_at = models.DateTimeField(auto_now_add=True, help_text="개설일")
    target_date = models.DateTimeField(help_text="목표일")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="완료일")
    assigned_to = models.CharField(max_length=50, help_text="담당자")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'capa'
        verbose_name = 'CAPA'
        verbose_name_plural = 'CAPAs'
        ordering = ['-opened_at']

    def __str__(self):
        return f"{self.capa_id} - {self.title}"


class CapaAction(models.Model):
    """CAPA 조치 모델"""
    ACTION_TYPES = [
        ('CORRECTIVE', '시정 조치'),
        ('PREVENTIVE', '예방 조치'),
    ]

    STATUS_CHOICES = [
        ('PENDING', '대기 중'),
        ('IN_PROGRESS', '진행 중'),
        ('COMPLETED', '완료'),
    ]

    action_id = models.CharField(max_length=50, unique=True, help_text="조치 ID")
    capa = models.ForeignKey(Capa, on_delete=models.CASCADE, related_name='actions', help_text="CAPA")
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES, help_text="조치 유형")
    description = models.TextField(help_text="조치 설명")
    assignee = models.CharField(max_length=50, help_text="담당자 ID")
    due_date = models.DateField(help_text="목표일")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', help_text="상태")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="완료일시")
    verification_notes = models.TextField(blank=True, help_text="검증 비고")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'capa_action'
        verbose_name = 'CAPA Action'
        verbose_name_plural = 'CAPA Actions'
        ordering = ['due_date']

    def __str__(self):
        return f"{self.action_id} - {self.action_type}"


class AIRootCauseAnalysisHistory(models.Model):
    """AI 근본원인분석 기록 모델"""
    analysis_id = models.CharField(max_length=50, unique=True, help_text="분석 ID")
    problem_description = models.TextField(help_text="문제 설명")
    defect_details = models.TextField(help_text="불량 상세")
    context = models.TextField(blank=True, help_text="추가 컨텍스트")
    root_cause = models.TextField(help_text="근본 원인")
    confidence = models.FloatField(help_text="신뢰도 (0-1)")
    recommended_corrective_actions = models.JSONField(help_text="권장 시정 조치 (JSON)")
    recommended_preventive_actions = models.JSONField(help_text="권장 예방 조치 (JSON)")
    is_applied = models.BooleanField(default=False, help_text="적용 여부")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_root_cause_analysis_history'
        verbose_name = 'AI Root Cause Analysis History'
        verbose_name_plural = 'AI Root Cause Analysis Histories'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.analysis_id} - {self.confidence}"
