"""
품질 이슈 시스템 Serializers
"""
from rest_framework import serializers
from .models import QualityIssue, IssueAnalysis4M, ProblemSolvingStep
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """사용자 정보 간직 시리얼라이저"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class IssueAnalysis4MSerializer(serializers.ModelSerializer):
    """4M 분석 시리얼라이저"""
    class Meta:
        model = IssueAnalysis4M
        fields = ['id', 'category', 'description', 'created_at']


class ProblemSolvingStepSerializer(serializers.ModelSerializer):
    """8단계 문제 해결 시리얼라이저"""
    class Meta:
        model = ProblemSolvingStep
        fields = [
            'id', 'step_number', 'step_name', 'content',
            'completed', 'completed_at', 'created_at', 'updated_at'
        ]


class QualityIssueListSerializer(serializers.ModelSerializer):
    """품질 이슈 목록 조회용 시리얼라이저"""
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = QualityIssue
        fields = [
            'id', 'issue_number', 'title', 'product_code', 'product_name',
            'defect_type', 'severity', 'severity_display', 'status',
            'status_display', 'reported_date', 'reporter', 'reporter_name',
            'department', 'defect_quantity', 'cost_impact'
        ]


class QualityIssueDetailSerializer(serializers.ModelSerializer):
    """품질 이슈 상세 조회용 시리얼라이저"""
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    analyses_4m = IssueAnalysis4MSerializer(many=True, read_only=True)
    solving_steps = ProblemSolvingStepSerializer(many=True, read_only=True)

    class Meta:
        model = QualityIssue
        fields = [
            'id', 'issue_number', 'title', 'description', 'product_code',
            'product_name', 'defect_type', 'severity', 'severity_display',
            'status', 'status_display', 'reported_date', 'reporter',
            'reporter_name', 'department', 'defect_quantity', 'cost_impact',
            'responsible_person', 'target_resolution_date',
            'actual_resolution_date', 'completion_notes',
            'analyses_4m', 'solving_steps', 'created_at', 'updated_at'
        ]


class QualityIssueCreateSerializer(serializers.ModelSerializer):
    """품질 이슈 생성용 시리얼라이저"""
    class Meta:
        model = QualityIssue
        fields = [
            'issue_number', 'title', 'description', 'product_code',
            'product_name', 'defect_type', 'severity', 'department',
            'defect_quantity', 'cost_impact', 'responsible_person',
            'target_resolution_date'
        ]

    def create(self, validated_data):
        # reporter는 현재 로그인한 사용자로 자동 설정
        validated_data['reporter'] = self.context['request'].user
        return super().create(validated_data)


class QualityIssueUpdateSerializer(serializers.ModelSerializer):
    """품질 이슈 수정용 시리얼라이저"""
    class Meta:
        model = QualityIssue
        fields = [
            'title', 'description', 'severity', 'status',
            'responsible_person', 'target_resolution_date',
            'actual_resolution_date', 'completion_notes',
            'defect_quantity', 'cost_impact'
        ]
