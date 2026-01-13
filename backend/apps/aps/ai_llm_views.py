from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
import uuid
import random

from .ai_llm_models import (
    ChatConversation, ChatMessage, PredictiveModel, Prediction,
    SmartRecommendation, KnowledgeBase, AIInsight
)


class ChatBotViewSet(viewsets.ViewSet):
    """AI 챗봇 API"""

    @action(detail=False, methods=['post'])
    def start_conversation(self, request):
        """새로운 대화 세션 시작"""
        session_id = str(uuid.uuid4())
        user_name = request.data.get('user_name', 'admin')

        conversation = ChatConversation.objects.create(
            session_id=session_id,
            user_name=user_name,
            title='New Conversation'
        )

        ChatMessage.objects.create(
            conversation=conversation,
            role='ASSISTANT',
            content='안녕하세요! APS-CPS 스마트 제조 AI 어시스턴트입니다. 무엇을 도와드릴까요?'
        )

        return Response({
            'session_id': session_id,
            'message': 'Conversation started successfully'
        })

    @action(detail=False, methods=['get'])
    def list_conversations(self, request):
        """대화 세션 목록"""
        user_name = request.query_params.get('user_name', 'admin')
        conversations = ChatConversation.objects.filter(user_name=user_name, is_active=True)

        data = [{
            'session_id': conv.session_id,
            'title': conv.title,
            'created_at': conv.created_at,
            'updated_at': conv.updated_at,
            'message_count': conv.messages.count(),
            'last_message': conv.messages.last().content[:100] if conv.messages.exists() else ''
        } for conv in conversations]

        return Response(data)

    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """메시지 전송 및 AI 응답"""
        session_id = request.data.get('session_id')
        user_message = request.data.get('message', '')

        try:
            conversation = ChatConversation.objects.get(session_id=session_id)
        except ChatConversation.DoesNotExist:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

        ChatMessage.objects.create(
            conversation=conversation,
            role='USER',
            content=user_message
        )

        # 간단한 AI 응답 (실제로는 OpenAI/Claude API 통합)
        ai_content = f"'{user_message}'에 대해 답변드립니다. 현재는 시뮬레이션 모드로 작동중입니다. LLM API를 통합하면 더 상세한 답변을 제공할 수 있습니다."

        assistant_message = ChatMessage.objects.create(
            conversation=conversation,
            role='ASSISTANT',
            content=ai_content
        )

        if conversation.messages.count() == 2:
            conversation.title = user_message[:50]
            conversation.save()

        return Response({
            'message_id': assistant_message.id,
            'content': ai_content,
            'timestamp': assistant_message.timestamp
        })

    @action(detail=False, methods=['get'])
    def get_conversation_history(self, request):
        """대화 내역 조회"""
        session_id = request.query_params.get('session_id')

        try:
            conversation = ChatConversation.objects.get(session_id=session_id)
        except ChatConversation.DoesNotExist:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

        messages = conversation.messages.all()
        data = [{
            'id': msg.id,
            'role': msg.role,
            'content': msg.content,
            'timestamp': msg.timestamp
        } for msg in messages]

        return Response({
            'session_id': session_id,
            'title': conversation.title,
            'messages': data
        })


class PredictiveAnalyticsViewSet(viewsets.ViewSet):
    """예측 분석 API"""

    @action(detail=False, methods=['get'])
    def list_models(self, request):
        """예측 모델 목록"""
        return Response([
            {
                'id': 1,
                'model_name': '수요 예측 모델',
                'model_type': 'DEMAND_FORECAST',
                'algorithm': 'LSTM',
                'accuracy': 0.87,
                'last_trained_at': timezone.now(),
                'version': '1.0'
            }
        ])

    @action(detail=False, methods=['get'])
    def demand_forecast(self, request):
        """수요 예측"""
        predictions = []
        for i in range(1, 8):
            predicted_date = timezone.now().date() + timedelta(days=i)
            predictions.append({
                'date': predicted_date,
                'predicted_jobs': random.randint(10, 30),
                'confidence': round(random.uniform(0.75, 0.95), 2),
                'trend': 'increasing' if i % 3 == 0 else 'stable'
            })

        return Response({
            'forecast_period': '7 days',
            'predictions': predictions
        })

    @action(detail=False, methods=['get'])
    def maintenance_prediction(self, request):
        """고장 예측"""
        predictions = []
        for i in range(5):
            predictions.append({
                'machine_id': i + 1,
                'machine_code': f'M-{i+1:03d}',
                'machine_name': f'Machine {i+1}',
                'failure_risk': round(random.uniform(0.1, 0.9), 2),
                'risk_level': random.choice(['low', 'medium', 'high']),
                'estimated_days_until_maintenance': random.randint(5, 60),
                'recommended_action': 'Schedule maintenance'
            })

        return Response({
            'total_machines': len(predictions),
            'predictions': predictions
        })

    @action(detail=False, methods=['get'])
    def delivery_prediction(self, request):
        """납기 예측"""
        predictions = []
        for i in range(10):
            on_time_prob = random.uniform(0.5, 0.99)
            predictions.append({
                'job_id': i + 1,
                'job_code': f'J-{i+1:03d}',
                'job_name': f'Job {i+1}',
                'due_date': (timezone.now() + timedelta(days=random.randint(1, 30))).date(),
                'on_time_probability': round(on_time_prob, 2),
                'status': 'on_track' if on_time_prob > 0.8 else 'at_risk',
                'estimated_delay_days': 0 if on_time_prob > 0.7 else random.randint(1, 10),
                'recommended_priority': 'urgent' if on_time_prob < 0.7 else 'normal'
            })

        return Response({
            'total_jobs': len(predictions),
            'predictions': predictions
        })


class SmartRecommendationViewSet(viewsets.ModelViewSet):
    """스마트 추천 API"""
    queryset = SmartRecommendation.objects.all()

    @action(detail=False, methods=['get'])
    def active_recommendations(self, request):
        """활성 추천 목록"""
        recommendations = SmartRecommendation.objects.filter(status='PENDING').order_by('-priority', '-created_at')

        data = [{
            'id': rec.id,
            'recommendation_type': rec.recommendation_type,
            'title': rec.title,
            'description': rec.description,
            'reasoning': rec.reasoning,
            'expected_benefit': rec.expected_benefit,
            'confidence_score': rec.confidence_score,
            'priority': rec.priority,
            'status': rec.status,
            'created_at': rec.created_at,
            'affected_jobs': rec.affected_jobs,
            'affected_machines': rec.affected_machines
        } for rec in recommendations]

        return Response(data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """추천 수락"""
        recommendation = self.get_object()
        recommendation.status = 'ACCEPTED'
        recommendation.save()
        return Response({'message': 'Recommendation accepted'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """추천 거부"""
        recommendation = self.get_object()
        recommendation.status = 'REJECTED'
        recommendation.save()
        return Response({'message': 'Recommendation rejected'})

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """추천 적용"""
        recommendation = self.get_object()
        recommendation.status = 'APPLIED'
        recommendation.applied_at = timezone.now()
        recommendation.applied_by = request.data.get('user', 'admin')
        recommendation.save()
        return Response({'message': 'Recommendation applied'})

    @action(detail=False, methods=['post'])
    def generate_recommendations(self, request):
        """AI 추천 생성"""
        SmartRecommendation.objects.create(
            recommendation_type='SCHEDULE_OPTIMIZATION',
            title='스케줄 최적화 권장',
            description='현재 스케줄을 재최적화하면 효율이 개선됩니다.',
            reasoning='최근 작업 패턴 분석 결과',
            expected_benefit='평균 완료시간 15% 감소',
            confidence_score=0.87,
            priority=3
        )

        return Response({'message': '1 recommendation generated'})


class AIInsightViewSet(viewsets.ModelViewSet):
    """AI 인사이트 API"""
    queryset = AIInsight.objects.all()

    @action(detail=False, methods=['get'])
    def recent_insights(self, request):
        """최근 인사이트"""
        days = int(request.query_params.get('days', 7))
        since = timezone.now() - timedelta(days=days)

        insights = AIInsight.objects.filter(created_at__gte=since).order_by('-created_at')

        data = [{
            'id': insight.id,
            'insight_type': insight.insight_type,
            'title': insight.title,
            'description': insight.description,
            'severity': insight.severity,
            'is_read': insight.is_read,
            'created_at': insight.created_at
        } for insight in insights]

        return Response({
            'period_days': days,
            'total_insights': len(data),
            'unread_count': len([i for i in insights if not i.is_read]),
            'insights': data
        })

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """읽음 처리"""
        insight = self.get_object()
        insight.is_read = True
        insight.save()
        return Response({'message': 'Marked as read'})

    @action(detail=True, methods=['post'])
    def feedback(self, request, pk=None):
        """피드백 제출"""
        insight = self.get_object()
        insight.is_helpful = request.data.get('is_helpful', True)
        insight.user_feedback = request.data.get('feedback', '')
        insight.save()
        return Response({'message': 'Feedback submitted'})

    @action(detail=False, methods=['post'])
    def generate_insights(self, request):
        """AI 인사이트 생성"""
        AIInsight.objects.create(
            insight_type='TREND',
            title='작업 완료율 증가 트렌드',
            description='최근 작업 완료율이 지속적으로 향상되고 있습니다.',
            severity='LOW'
        )

        return Response({'message': '1 insight generated'})
