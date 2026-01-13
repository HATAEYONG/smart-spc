from django.db import models
from django.utils import timezone


class ChatConversation(models.Model):
    """AI 챗봇 대화 세션"""
    session_id = models.CharField(max_length=100, unique=True)
    user_name = models.CharField(max_length=100, default='admin')
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'chat_conversation'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat {self.session_id} - {self.title or 'Untitled'}"


class ChatMessage(models.Model):
    """AI 챗봇 메시지"""
    ROLE_CHOICES = [
        ('USER', '사용자'),
        ('ASSISTANT', 'AI 어시스턴트'),
        ('SYSTEM', '시스템'),
    ]

    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    tokens_used = models.IntegerField(default=0)

    # 컨텍스트 정보
    referenced_jobs = models.JSONField(default=list, blank=True)
    referenced_machines = models.JSONField(default=list, blank=True)
    referenced_data = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'chat_message'
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class PredictiveModel(models.Model):
    """예측 모델 정보"""
    MODEL_TYPES = [
        ('DEMAND_FORECAST', '수요 예측'),
        ('MAINTENANCE_PREDICTION', '고장 예측'),
        ('QUALITY_PREDICTION', '품질 예측'),
        ('DELIVERY_PREDICTION', '납기 예측'),
        ('RESOURCE_OPTIMIZATION', '리소스 최적화'),
    ]

    STATUS_CHOICES = [
        ('TRAINING', '학습중'),
        ('ACTIVE', '활성'),
        ('DEPRECATED', '사용중지'),
    ]

    model_name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPES)
    description = models.TextField(blank=True)
    algorithm = models.CharField(max_length=100)  # Random Forest, LSTM, XGBoost, etc.

    # 모델 성능 지표
    accuracy = models.FloatField(default=0.0)
    precision = models.FloatField(default=0.0)
    recall = models.FloatField(default=0.0)
    f1_score = models.FloatField(default=0.0)
    mae = models.FloatField(default=0.0)  # Mean Absolute Error
    rmse = models.FloatField(default=0.0)  # Root Mean Square Error

    # 학습 정보
    training_data_size = models.IntegerField(default=0)
    last_trained_at = models.DateTimeField(null=True, blank=True)
    version = models.CharField(max_length=20, default='1.0')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TRAINING')

    # 모델 파일 경로
    model_file_path = models.CharField(max_length=500, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'predictive_model'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.model_name} ({self.model_type})"


class Prediction(models.Model):
    """AI 예측 결과"""
    # Prediction Types
    PRED_TYPES = [
        ('PROC_TIME', 'Process Time'),
        ('SETUP_TIME', 'Setup Time'),
        ('DOWN_RISK', 'Downtime Risk'),  # ← STEP 2 추가
        ('DEMAND', 'Demand Forecast'),
        ('QUALITY', 'Quality Prediction'),
        ('DELIVERY', 'Delivery Prediction'),
    ]

    model = models.ForeignKey(PredictiveModel, on_delete=models.CASCADE, related_name='predictions')
    prediction_type = models.CharField(max_length=50, choices=PRED_TYPES)
    target_entity = models.CharField(max_length=100, blank=True)  # Job, Machine, "RES:<code>", etc.
    target_id = models.IntegerField(null=True, blank=True)

    # 예측 결과
    predicted_value = models.FloatField()
    confidence_score = models.FloatField(default=0.0)  # 0.0 ~ 1.0
    predicted_date = models.DateTimeField(null=True, blank=True)

    # 실제 결과 (검증용)
    actual_value = models.FloatField(null=True, blank=True)
    is_accurate = models.BooleanField(null=True, blank=True)

    # 상세 정보
    features_used = models.JSONField(default=dict, blank=True)
    explanation = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prediction'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.prediction_type}: {self.predicted_value} (confidence: {self.confidence_score})"


class SmartRecommendation(models.Model):
    """AI 스마트 추천"""
    RECOMMENDATION_TYPES = [
        ('SCHEDULE_OPTIMIZATION', '스케줄 최적화'),
        ('RESOURCE_ALLOCATION', '리소스 할당'),
        ('MAINTENANCE_TIMING', '유지보수 시기'),
        ('PRIORITY_ADJUSTMENT', '우선순위 조정'),
        ('BOTTLENECK_RESOLUTION', '병목 해소'),
        ('QUALITY_IMPROVEMENT', '품질 개선'),
    ]

    PRIORITY_CHOICES = [
        (1, '낮음'),
        (2, '보통'),
        (3, '높음'),
        (4, '긴급'),
    ]

    STATUS_CHOICES = [
        ('PENDING', '대기'),
        ('ACCEPTED', '수락'),
        ('REJECTED', '거부'),
        ('APPLIED', '적용됨'),
    ]

    recommendation_type = models.CharField(max_length=50, choices=RECOMMENDATION_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()

    # 추천 근거
    reasoning = models.TextField()
    expected_benefit = models.TextField(blank=True)
    confidence_score = models.FloatField(default=0.0)

    # 영향 받는 대상
    affected_jobs = models.JSONField(default=list, blank=True)
    affected_machines = models.JSONField(default=list, blank=True)

    # 추천 액션
    suggested_action = models.JSONField(default=dict, blank=True)

    # 우선순위 및 상태
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    # 적용 결과
    applied_at = models.DateTimeField(null=True, blank=True)
    applied_by = models.CharField(max_length=100, blank=True)
    actual_benefit = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'smart_recommendation'
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"{self.recommendation_type}: {self.title}"


class KnowledgeBase(models.Model):
    """AI 학습용 지식 베이스"""
    CATEGORY_CHOICES = [
        ('BEST_PRACTICE', '모범 사례'),
        ('TROUBLESHOOTING', '문제 해결'),
        ('OPTIMIZATION', '최적화 기법'),
        ('MAINTENANCE', '유지보수'),
        ('QUALITY', '품질 관리'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    tags = models.JSONField(default=list, blank=True)

    # 메타데이터
    source = models.CharField(max_length=200, blank=True)
    author = models.CharField(max_length=100, blank=True)

    # 사용 통계
    view_count = models.IntegerField(default=0)
    helpful_count = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'knowledge_base'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.category}: {self.title}"


class AIInsight(models.Model):
    """AI 인사이트 (자동 생성되는 통찰)"""
    INSIGHT_TYPES = [
        ('ANOMALY', '이상 징후'),
        ('TREND', '트렌드 분석'),
        ('PATTERN', '패턴 발견'),
        ('OPPORTUNITY', '개선 기회'),
        ('RISK', '리스크 경고'),
    ]

    insight_type = models.CharField(max_length=50, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()

    # 근거 데이터
    supporting_data = models.JSONField(default=dict, blank=True)
    data_source = models.CharField(max_length=100, blank=True)
    analysis_period_start = models.DateTimeField(null=True, blank=True)
    analysis_period_end = models.DateTimeField(null=True, blank=True)

    # 중요도
    severity = models.CharField(max_length=20, choices=[
        ('LOW', '낮음'),
        ('MEDIUM', '보통'),
        ('HIGH', '높음'),
        ('CRITICAL', '긴급'),
    ], default='MEDIUM')

    # 사용자 피드백
    is_read = models.BooleanField(default=False)
    is_helpful = models.BooleanField(null=True, blank=True)
    user_feedback = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_insight'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.insight_type}: {self.title}"
