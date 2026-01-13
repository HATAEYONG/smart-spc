from rest_framework import serializers
from apps.core.models import StageFactPlanOut
from .models import AlgorithmComparison, BottleneckAnalysis, MachineLoadHistory
from .ai_llm_models import ChatConversation, ChatMessage, PredictiveModel as AILLMPredictiveModel, Prediction as AILLMPrediction, SmartRecommendation, KnowledgeBase, AIInsight


class StageFactPlanOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = StageFactPlanOut
        fields = "__all__"


class AlgorithmComparisonSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlgorithmComparison
        fields = "__all__"
        read_only_fields = ["comparison_id", "created_at"]


class ComparisonRequestSerializer(serializers.Serializer):
    """Request to run algorithm comparison"""
    job_count = serializers.IntegerField(min_value=5, max_value=100, default=20)
    machine_count = serializers.IntegerField(min_value=2, max_value=10, default=5)
    use_real_data = serializers.BooleanField(default=False)


class BottleneckAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = BottleneckAnalysis
        fields = "__all__"
        read_only_fields = ["analysis_id", "created_at"]


class MachineLoadHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineLoadHistory
        fields = "__all__"
        read_only_fields = ["history_id"]


class BottleneckAnalysisRequestSerializer(serializers.Serializer):
    """Request to run bottleneck analysis"""
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    threshold = serializers.FloatField(default=80.0, min_value=0, max_value=100)  # utilization threshold


# ==================== AI LLM Serializers ====================

class ChatConversationSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatConversation
        fields = '__all__'

    def get_message_count(self, obj):
        return obj.messages.count()


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'


class AILLMPredictiveModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AILLMPredictiveModel
        fields = '__all__'


class AILLMPredictionSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(source='model.model_name', read_only=True)

    class Meta:
        model = AILLMPrediction
        fields = '__all__'


class SmartRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmartRecommendation
        fields = '__all__'


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBase
        fields = '__all__'


class AIInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIInsight
        fields = '__all__'
