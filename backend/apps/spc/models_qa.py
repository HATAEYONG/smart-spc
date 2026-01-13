"""
QA (Quality Assurance) Models
품질보증 시스템을 위한 Django 모델
ERD 1-5: QA(품질보증) 도메인
"""

from django.db import models
from django.utils import timezone
from apps.spc.models_qcost import OrganizationSite, OrganizationDepartment


class QAProcess(models.Model):
    """QA 프로세스 (qa_process)"""
    qa_proc_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='qa_processes')

    proc_name = models.CharField(max_length=200)
    rev_no = models.CharField(max_length=20, default='1.0')
    status = models.CharField(max_length=20, default='ACTIVE')

    owner_dept = models.ForeignKey(OrganizationDepartment, on_delete=models.PROTECT, related_name='qa_processes')
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'qa_process'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.proc_name} Rev.{self.rev_no}"


class QARequirement(models.Model):
    """QA 요구사항/체크포인트 (qa_requirement)"""
    REQ_TYPE_CHOICES = [
        ('ISO', 'ISO 표준'),
        ('IATF', 'IATF 표준'),
        ('INHOUSE', '사내 규정'),
        ('CUSTOMER', '고객 요구사항'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', '낮음'),
        ('MEDIUM', '보통'),
        ('HIGH', '높음'),
        ('CRITICAL', '매우 중요'),
    ]

    CONTROL_METHOD_CHOICES = [
        ('DOC', '문서'),
        ('RECORD', '기록'),
        ('SYSTEM', '시스템'),
    ]

    req_id = models.AutoField(primary_key=True)
    qa_process = models.ForeignKey(QAProcess, on_delete=models.CASCADE, related_name='requirements')

    req_type = models.CharField(max_length=20, choices=REQ_TYPE_CHOICES)
    clause = models.CharField(max_length=100, help_text='조항 번호')
    req_text = models.TextField(help_text='요구사항 내용')

    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    evidence_needed = models.BooleanField(default=True)
    control_method = models.CharField(max_length=20, choices=CONTROL_METHOD_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'qa_requirement'
        ordering = ['qa_process', 'clause']

    def __str__(self):
        return f"{self.req_type} {self.clause}"


class QAAssessment(models.Model):
    """QA 진단 (qa_assessment)"""
    assess_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='qa_assessments')
    qa_process = models.ForeignKey(QAProcess, on_delete=models.CASCADE, related_name='assessments')

    assess_dt = models.DateTimeField(default=timezone.now)
    assessor_id = models.IntegerField(help_text='진단자 ID')

    scope = models.TextField(help_text='진단 범위')
    overall_level = models.CharField(max_length=20, help_text='전체 등급 (예: Level 1~5)')

    # AI 요약
    ai_summary_id = models.IntegerField(null=True, blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'qa_assessment'
        ordering = ['-assess_dt']

    def __str__(self):
        return f"Assessment {self.ass_id} - {self.assess_dt}"


class QAGapFinding(models.Model):
    """QA GAP 분석 (qa_gap_finding)"""
    FINDING_TYPE_CHOICES = [
        ('MISSING', '미비'),
        ('UPDATE', '수정 필요'),
        ('IMPROVE', '개선 권고'),
    ]

    SEVERITY_CHOICES = [
        ('LOW', '낮음'),
        ('MEDIUM', '보통'),
        ('HIGH', '높음'),
        ('CRITICAL', '긴급'),
    ]

    STATUS_CHOICES = [
        ('OPEN', '미해결'),
        ('IN_PROGRESS', '진행중'),
        ('DONE', '완료'),
    ]

    finding_id = models.AutoField(primary_key=True)
    assessment = models.ForeignKey(QAAssessment, on_delete=models.CASCADE, related_name='findings')
    requirement = models.ForeignKey(QARequirement, on_delete=models.CASCADE, related_name='findings')

    finding_type = models.CharField(max_length=20, choices=FINDING_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)

    as_is = models.TextField(help_text='현재 상태')
    to_be = models.TextField(help_text='목표 상태')

    evidence = models.TextField(blank=True, help_text='증거 자료')
    due_dt = models.DateTimeField(help_text='목표 일정')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')

    # 담당자
    owner_user_id = models.IntegerField(help_text='담당자 ID')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'qa_gap_finding'
        ordering = ['-severity', '-created_at']

    def __str__(self):
        return f"[{self.severity}] {self.finding_type} - Req {self.requirement.req_id}"


class CAPACase(models.Model):
    """시정·예방조치 (capa_case)"""
    SOURCE_TYPE_CHOICES = [
        ('SPC_EVENT', 'SPC 이벤트'),
        ('INSPECTION_FAIL', '검사 불합격'),
        ('QA_FINDING', 'QA GAP 분석'),
        ('CUSTOMER_CLAIM', '고객 클레임'),
        ('INTERNAL_AUDIT', '내부 감사'),
    ]

    STATUS_CHOICES = [
        ('OPEN', '미해결'),
        ('IN_PROGRESS', '진행중'),
        ('VERIFICATION', '효과 확인중'),
        ('CLOSED', '종료'),
    ]

    capa_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='capa_cases')

    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES)
    source_id = models.IntegerField(help_text='원본 이벤트/문제 ID')

    problem_statement = models.TextField(help_text='문제 정의')

    # 8D 보고서 형식
    containment_action = models.TextField(help_text='잠시 조치')
    root_cause = models.TextField(help_text='근본 원인')
    corrective_action = models.TextField(help_text='시정 조치')
    preventive_action = models.TextField(help_text='예방 조치')

    # 담당자 및 일정
    owner_user_id = models.IntegerField(help_text='담당자 ID')
    due_dt = models.DateTimeField(help_text='목표 완료일')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')

    # 효과 확인
    effectiveness_check_dt = models.DateTimeField(null=True, blank=True)
    effectiveness_verified = models.BooleanField(null=True, blank=True)

    # AI 지원
    ai_recommendation = models.JSONField(null=True, blank=True, help_text='AI 추천 조치')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'capa_case'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['site', 'status']),
            models.Index(fields=['source_type', 'source_id']),
        ]

    def __str__(self):
        return f"CAPA {self.capa_id} - {self.source_type}"


class ChangeControl(models.Model):
    """변경 관리 (change_control)"""
    OBJECT_TYPE_CHOICES = [
        ('PLAN', '검사 계획'),
        ('SPEC', '검사 규격'),
        ('PROCESS', '공정'),
        ('WORKINSTR', '작업 표준'),
        ('DOC', '문서'),
    ]

    chg_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='change_controls')

    object_type = models.CharField(max_length=20, choices=OBJECT_TYPE_CHOICES)
    object_id = models.IntegerField(help_text='변경 대상 ID')

    from_rev = models.CharField(max_length=20, help_text='이전 리비전')
    to_rev = models.CharField(max_length=20, help_text='새 리비전')

    reason = models.TextField(help_text='변경 사유')

    # 승인 정보
    requested_by = models.IntegerField(help_text='요청자 ID')
    approved_by = models.IntegerField(null=True, blank=True)
    approved_dt = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, default='PENDING')

    # 변경 내용
    changes_summary = models.TextField(help_text='변경 요약')
    impact_analysis = models.TextField(blank=True, help_text='영향 평가')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'change_control'
        ordering = ['-created_at']

    def __str__(self):
        return f"Change {self.chg_id}: {self.from_rev} → {self.to_rev}"


class DocFile(models.Model):
    """문서 파일 (doc_file)"""
    file_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='doc_files')

    file_name = models.CharField(max_length=255)
    mime = models.CharField(max_length=100)
    uri = models.CharField(max_length=500, help_text='파일 경로 또는 URL')

    # 연계 정보
    linked_type = models.CharField(max_length=50, help_text='연계된 모델 타입')
    linked_id = models.IntegerField(help_text='연계된 모델 ID')

    uploaded_by = models.IntegerField()
    uploaded_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'doc_file'
        ordering = ['-uploaded_dt']

    def __str__(self):
        return self.file_name


class AIOutput(models.Model):
    """AI 결과 저장 (ai_output)"""
    USE_CASE_CHOICES = [
        ('CHECKLIST', '체크리스트 생성'),
        ('CRITERIA', '판정 기준 생성'),
        ('REPORT', '보고서 생성'),
        ('ROOTCAUSE', '근본 원인 분석'),
        ('QC_PLAN', 'QC 계획 생성'),
        ('RECOMMENDATION', '개선 추천'),
    ]

    ai_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(OrganizationSite, on_delete=models.CASCADE, related_name='ai_outputs')

    use_case = models.CharField(max_length=50, choices=USE_CASE_CHOICES)

    # 입력 해시 (중복 방지)
    input_hash = models.CharField(max_length=64, unique=True)

    # 모델 정보
    model_name = models.CharField(max_length=100)
    prompt_version = models.CharField(max_length=20)

    # 출력
    output_json = models.JSONField()
    confidence = models.FloatField(help_text='신뢰도 (0~1)')

    created_dt = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField()

    class Meta:
        db_table = 'ai_output'
        ordering = ['-created_dt']
        indexes = [
            models.Index(fields=['site', 'use_case']),
            models.Index(fields=['input_hash']),
        ]

    def __str__(self):
        return f"AI {self.use_case} - {self.confidence:.2f}"
