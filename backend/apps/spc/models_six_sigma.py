"""
Six Sigma DMAIC Models

Define, Measure, Analyze, Improve, Control 방법론을 기반으로 한 품질 개선 프로젝트 관리
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class DMAICProject(models.Model):
    """Six Sigma DMAIC 프로젝트"""

    PHASE_CHOICES = [
        ('DEFINE', 'Define - 정의'),
        ('MEASURE', 'Measure - 측정'),
        ('ANALYZE', 'Analyze - 분석'),
        ('IMPROVE', 'Improve - 개선'),
        ('CONTROL', 'Control - 관리'),
        ('CLOSED', 'Closed - 완료'),
    ]

    PRIORITY_CHOICES = [
        ('CRITICAL', 'Critical - 긴급'),
        ('HIGH', 'High - 높음'),
        ('MEDIUM', 'Medium - 보통'),
        ('LOW', 'Low - 낮음'),
    ]

    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('ON_HOLD', 'On Hold'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    # 기본 정보
    project_code = models.CharField(max_length=50, unique=True)
    project_name = models.CharField(max_length=200)
    description = models.TextField()

    # 프로젝트 관리
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES, default='DEFINE')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')

    # 담당자
    champion = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='champion_projects')
    process_owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_projects')
    team_members = models.ManyToManyField(User, related_name='dmaic_projects', blank=True)

    # 기간
    start_date = models.DateField()
    target_end_date = models.DateField()
    actual_end_date = models.DateField(null=True, blank=True)

    # 비용
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # 목표 및 성과
    problem_statement = models.TextField(blank=True)
    goal_statement = models.TextField(blank=True)
    benefit_target = models.CharField(max_length=200, blank=True)  # 예: "불량률 5% 감소"

    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'dmaic_project'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phase', 'status']),
            models.Index(fields=['priority', 'status']),
        ]

    def __str__(self):
        return f"{self.project_code} - {self.project_name}"

    @property
    def progress_percentage(self):
        """DMAIC 단계별 진행률 계산"""
        phase_weights = {
            'DEFINE': 0,
            'MEASURE': 20,
            'ANALYZE': 40,
            'IMPROVE': 60,
            'CONTROL': 80,
            'CLOSED': 100,
        }
        return phase_weights.get(self.phase, 0)


class DefinePhase(models.Model):
    """Define 단계: 문제 정의 및 프로젝트 범위 설정"""

    project = models.OneToOneField(DMAICProject, on_delete=models.CASCADE, related_name='define_phase')

    # 고객 목소리 (VOC - Voice of Customer)
    customer_requirements = models.TextField(blank=True, help_text="고객 요구사항")
    critical_to_quality = models.JSONField(default=list, help_text="CTQ 항목들")

    # 프로젝트 범위
    in_scope = models.TextField(help_text="프로젝트 범위에 포함되는 항목")
    out_of_scope = models.TextField(blank=True, help_text="프로젝트 범위에서 제외되는 항목")

    # SIPOC (Supplier, Input, Process, Output, Customer)
    sipoc_suppliers = models.TextField(blank=True)
    sipoc_inputs = models.TextField(blank=True)
    sipoc_process = models.TextField(blank=True)
    sipoc_outputs = models.TextField(blank=True)
    sipoc_customers = models.TextField(blank=True)

    # 타임라인 및 이해관계자
    stakeholders = models.TextField(blank=True)
    risks = models.TextField(blank=True)

    # 완료 여부
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dmaic_define_phase'

    def __str__(self):
        return f"Define Phase - {self.project.project_name}"


class MeasurePhase(models.Model):
    """Measure 단계: 현재 공정 성능 측정 및 데이터 수집 계획"""

    project = models.OneToOneField(DMAICProject, on_delete=models.CASCADE, related_name='measure_phase')

    # 측정 시스템 분석 (MSA)
    measurement_system_analysis = models.TextField(blank=True, help_text="Gage R&R 결과")
    measurement_system_capable = models.BooleanField(default=False)

    # 데이터 수집 계획
    data_collection_plan = models.TextField(blank=True)
    sample_size = models.IntegerField(null=True, blank=True)
    sampling_frequency = models.CharField(max_length=100, blank=True)

    # 기준선 성능 (Baseline Performance)
    current_process_performance = models.TextField(blank=True)
    baseline_yield = models.FloatField(null=True, blank=True, help_text="현재 수율 (%)")
    baseline_defect_rate = models.FloatField(null=True, blank=True, help_text="현재 불량률 (%)")
    baseline_dpmo = models.IntegerField(null=True, blank=True, help_text="백만회당 불격수")

    # 프로세스 매핑
    process_map_details = models.TextField(blank=True)

    # 완료 여부
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dmaic_measure_phase'

    def __str__(self):
        return f"Measure Phase - {self.project.project_name}"


class AnalyzePhase(models.Model):
    """Analyze 단계: 근본 원인 분석 및 데이터 분석"""

    project = models.OneToOneField(DMAICProject, on_delete=models.CASCADE, related_name='analyze_phase')

    # 데이터 분석
    statistical_analysis = models.TextField(blank=True, help_text="통계적 분석 결과")
    graphical_analysis = models.TextField(blank=True, help_text="그래프 분석 (Pareto, Histogram 등)")

    # 근본 원인 분석
    root_cause_analysis = models.TextField(blank=True, help_text="근본 원인 분석 결과")
    fishbone_diagram = models.JSONField(default=dict, blank=True, help_text="어류참(Fishbone) 다이어그램")
    five_whys = models.JSONField(default=list, blank=True, help_text="5-Why 분석")

    # 가설 검정
    hypothesis_tests = models.JSONField(default=list, blank=True, help_text="가설 검정 결과들")
    confirmed_root_causes = models.TextField(blank=True)

    # 공정 능력 분석
    process_capability_analysis = models.TextField(blank=True)
    cp_value = models.FloatField(null=True, blank=True)
    cpk_value = models.FloatField(null=True, blank=True)

    # 완료 여부
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dmaic_analyze_phase'

    def __str__(self):
        return f"Analyze Phase - {self.project.project_name}"


class ImprovePhase(models.Model):
    """Improve 단계: 해결책 개발 및 구현"""

    project = models.OneToOneField(DMAICProject, on_delete=models.CASCADE, related_name='improve_phase')

    # 해결책 발굴
    solution_brainstorming = models.TextField(blank=True)
    solution_selection_matrix = models.JSONField(default=dict, blank=True)

    # 선정된 해결책
    selected_solutions = models.TextField(help_text="채택된 해결책")
    implementation_plan = models.TextField(help_text="구현 계획")

    # 실험 계획 (DOE - Design of Experiments)
    doe_setup = models.TextField(blank=True, help_text="실험 계획법 설정")
    doe_results = models.TextField(blank=True, help_text="실험 결과")

    # 예상 성과
    estimated_improvement = models.CharField(max_length=200, blank=True)
    estimated_benefit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # 완료 여부
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dmaic_improve_phase'

    def __str__(self):
        return f"Improve Phase - {self.project.project_name}"


class ControlPhase(models.Model):
    """Control 단계: 개선 결과 유지 및 모니터링 계획"""

    project = models.OneToOneField(DMAICProject, on_delete=models.CASCADE, related_name='control_phase')

    # 관리 계획
    control_plan = models.TextField(help_text="관리 계획서")

    # 모니터링
    monitoring_plan = models.TextField(help_text="모니터링 계획")
    control_charts = models.TextField(blank=True, help_text="관리도 설정")

    # 표준화
    sop_updates = models.TextField(blank=True, help_text="SOP(표준 작업 절차) 업데이트")
    training_plan = models.TextField(blank=True, help_text="교육 계획")

    # 성과 확인
    verified_improvement = models.TextField(blank=True, help_text="검증된 개선 성과")
    sustained_results = models.TextField(blank=True, help_text="지속된 결과 확인")

    # 다음 단계
    lessons_learned = models.TextField(blank=True)
    next_steps = models.TextField(blank=True)

    # 완료 여부
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dmaic_control_phase'

    def __str__(self):
        return f"Control Phase - {self.project.project_name}"


class DMAICMilestone(models.Model):
    """DMAIC 프로젝트 마일스톤"""

    project = models.ForeignKey(DMAICProject, on_delete=models.CASCADE, related_name='milestones')

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    phase = models.CharField(max_length=20, choices=DMAICProject.PHASE_CHOICES)

    target_date = models.DateField()
    actual_date = models.DateField(null=True, blank=True)

    is_completed = models.BooleanField(default=False)
    is_on_track = models.BooleanField(default=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dmaic_milestone'
        ordering = ['target_date']

    def __str__(self):
        return f"{self.project.project_code} - {self.name}"


class DMAICDocument(models.Model):
    """DMAIC 프로젝트 관련 문서"""

    DOCUMENT_TYPE_CHOICES = [
        ('PROJECT_CHARTER', 'Project Charter'),
        ('SIPOC', 'SIPOC Diagram'),
        ('PROCESS_MAP', 'Process Map'),
        ('DATA_COLLECTION', 'Data Collection Plan'),
        ('MSA_REPORT', 'Measurement System Analysis Report'),
        ('STATISTICAL_ANALYSIS', 'Statistical Analysis Report'),
        ('ROOT_CAUSE', 'Root Cause Analysis'),
        ('SOLUTION', 'Solution Document'),
        ('CONTROL_PLAN', 'Control Plan'),
        ('SOP', 'Standard Operating Procedure'),
        ('FINAL_REPORT', 'Final Report'),
        ('OTHER', 'Other'),
    ]

    project = models.ForeignKey(DMAICProject, on_delete=models.CASCADE, related_name='documents')

    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # 파일
    file = models.FileField(upload_to='dmaic_documents/%Y/%m/', null=True, blank=True)
    file_url = models.URLField(blank=True)

    # 메타데이터
    version = models.CharField(max_length=20, default='1.0')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'dmaic_document'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.project.project_code} - {self.title}"


class DMAICRisk(models.Model):
    """DMAIC 프로젝트 리스크 관리"""

    project = models.ForeignKey(DMAICProject, on_delete=models.CASCADE, related_name='risks')

    RISK_LEVEL_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('MITIGATED', 'Mitigated'),
        ('CLOSED', 'Closed'),
    ]

    risk_description = models.CharField(max_length=500)
    impact = models.TextField(blank=True)
    probability = models.IntegerField(default=50, help_text="발생 확률 (%)")
    severity = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, default='MEDIUM')

    mitigation_plan = models.TextField(blank=True)
    contingency_plan = models.TextField(blank=True)

    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dmaic_risk'
        ordering = ['-severity', '-created_at']

    def __str__(self):
        return f"{self.project.project_code} - {self.risk_description}"


class StatisticalTool(models.Model):
    """Minitab 스타일 통계 도구 실행 결과"""

    TOOL_TYPE_CHOICES = [
        ('DESCRIPTIVE', '기술 통계 (Descriptive Statistics)'),
        ('HISTOGRAM', '히스토그램'),
        ('PARETO', '파레토도'),
        ('BOX_PLOT', '상자 수염 그림'),
        ('SCATTER_PLOT', '산점도'),
        ('RUN_CHART', '런 차트'),
        ('CORRELATION', '상관 분석'),
        ('REGRESSION', '회귀 분석'),
        ('T_TEST', 'T-검정'),
        ('ANOVA', '분산 분석 (ANOVA)'),
        ('CHI_SQUARE', '카이제곱 검정'),
        ('CAPABILITY', '공정능력 분석'),
        ('GAGE_RR', 'Gage R&R 분석'),
        ('DOE', '실험 계획법 (DOE)'),
    ]

    project = models.ForeignKey(DMAICProject, on_delete=models.CASCADE, related_name='statistical_tools', null=True, blank=True)

    tool_type = models.CharField(max_length=50, choices=TOOL_TYPE_CHOICES)
    tool_name = models.CharField(max_length=200)

    # 입력 데이터
    input_data = models.JSONField(help_text="분석에 사용된 데이터")

    # 분석 결과
    result_summary = models.TextField(help_text="결과 요약")
    result_data = models.JSONField(help_text="상세 결과 데이터")
    chart_data = models.JSONField(help_text="차트 데이터", null=True, blank=True)

    # 통계적 유의성
    p_value = models.FloatField(null=True, blank=True)
    confidence_interval = models.CharField(max_length=100, blank=True)

    # 해석
    interpretation = models.TextField(help_text="결과 해석")
    recommendations = models.TextField(blank=True, help_text="권장사항")

    # 메타데이터
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'dmaic_statistical_tool'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project.project_code if self.project else 'Standalone'} - {self.tool_name}"
