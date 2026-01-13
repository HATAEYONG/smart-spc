from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Avg, Count
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

        # 시스템 환영 메시지
        ChatMessage.objects.create(
            conversation=conversation,
            role='ASSISTANT',
            content='안녕하세요! APS-CPS 스마트 제조 AI 어시스턴트입니다. 생산 스케줄링, 기계 모니터링, 성과 분석 등에 대해 무엇이든 물어보세요.'
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

        data = []
        for conv in conversations:
            last_message = conv.messages.last()
            data.append({
                'session_id': conv.session_id,
                'title': conv.title,
                'created_at': conv.created_at,
                'updated_at': conv.updated_at,
                'message_count': conv.messages.count(),
                'last_message': last_message.content[:100] if last_message else ''
            })

        return Response(data)

    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """메시지 전송 및 AI 응답 생성"""
        session_id = request.data.get('session_id')
        user_message = request.data.get('message', '')

        try:
            conversation = ChatConversation.objects.get(session_id=session_id)
        except ChatConversation.DoesNotExist:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

        # 사용자 메시지 저장
        ChatMessage.objects.create(
            conversation=conversation,
            role='USER',
            content=user_message
        )

        # AI 응답 생성 (실제로는 LLM API 호출)
        ai_response = self._generate_ai_response(user_message, conversation)

        # AI 응답 저장
        assistant_message = ChatMessage.objects.create(
            conversation=conversation,
            role='ASSISTANT',
            content=ai_response['content'],
            referenced_jobs=ai_response.get('referenced_jobs', []),
            referenced_machines=ai_response.get('referenced_machines', []),
            referenced_data=ai_response.get('referenced_data', {})
        )

        # 대화 제목 자동 생성 (첫 메시지인 경우)
        if conversation.messages.count() == 2:  # Welcome + User's first message
            conversation.title = user_message[:50]
            conversation.save()

        return Response({
            'message_id': assistant_message.id,
            'content': ai_response['content'],
            'referenced_jobs': ai_response.get('referenced_jobs', []),
            'referenced_machines': ai_response.get('referenced_machines', []),
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
            'timestamp': msg.timestamp,
            'referenced_jobs': msg.referenced_jobs,
            'referenced_machines': msg.referenced_machines
        } for msg in messages]

        return Response({
            'session_id': session_id,
            'title': conversation.title,
            'messages': data
        })

    def _generate_ai_response(self, user_message, conversation):
        """AI 응답 생성 (LLM 통합 지점)"""
        # 실제 구현에서는 OpenAI API, Claude API 등을 호출
        # 여기서는 키워드 기반 간단한 응답 생성

        message_lower = user_message.lower()
        response = {
            'content': '',
            'referenced_jobs': [],
            'referenced_machines': [],
            'referenced_data': {}
        }

        # 작업 관련 질문
        if any(keyword in message_lower for keyword in ['작업', 'job', '진행', '완료']):
            jobs = Job.objects.all()[:5]
            total_jobs = Job.objects.count()
            completed = Job.objects.filter(status='COMPLETED').count()
            in_progress = Job.objects.filter(status='IN_PROGRESS').count()

            response['content'] = f"""현재 시스템에 등록된 작업은 총 {total_jobs}개입니다.

📊 작업 현황:
- 완료: {completed}개
- 진행중: {in_progress}개
- 대기: {total_jobs - completed - in_progress}개

최근 작업 5건:
"""
            for job in jobs:
                response['content'] += f"\n- [{job.job_code}] {job.job_name} (상태: {job.status})"
                response['referenced_jobs'].append(job.job_id)

        # 기계 관련 질문
        elif any(keyword in message_lower for keyword in ['기계', 'machine', '설비', '가동률']):
            machines = Machine.objects.all()[:5]
            total_machines = Machine.objects.count()
            available = Machine.objects.filter(status='AVAILABLE').count()
            busy = Machine.objects.filter(status='BUSY').count()

            response['content'] = f"""현재 등록된 기계는 총 {total_machines}대입니다.

🏭 기계 현황:
- 가동 가능: {available}대
- 작업중: {busy}대
- 기타: {total_machines - available - busy}대

주요 기계 목록:
"""
            for machine in machines:
                response['content'] += f"\n- [{machine.machine_code}] {machine.machine_name} (상태: {machine.status})"
                response['referenced_machines'].append(machine.machine_id)

        # 스케줄링 관련 질문
        elif any(keyword in message_lower for keyword in ['스케줄', 'schedule', '최적화', '알고리즘']):
            recent_schedule = ScheduleResult.objects.order_by('-created_at').first()

            if recent_schedule:
                response['content'] = f"""최근 스케줄링 결과를 안내해드리겠습니다.

📅 스케줄 정보:
- 알고리즘: {recent_schedule.algorithm}
- 생성일시: {recent_schedule.created_at.strftime('%Y-%m-%d %H:%M')}
- 총 작업 수: {recent_schedule.total_jobs}
- 완료 작업 수: {recent_schedule.completed_jobs}
- 평균 완료시간: {recent_schedule.average_completion_time:.1f}분

💡 추천:
- CP-SAT 알고리즘은 최적해를 찾지만 시간이 오래 걸립니다.
- Genetic Algorithm은 빠르면서도 좋은 해를 찾습니다.
- Dispatching Rules(SPT, EDD)는 실시간 대응에 적합합니다.
"""
            else:
                response['content'] = "아직 생성된 스케줄이 없습니다. 'APS 핵심 기능 > 스케줄 관리'에서 새 스케줄을 생성해보세요."

        # 성과 분석 관련 질문
        elif any(keyword in message_lower for keyword in ['성과', '분석', '통계', 'kpi']):
            total_jobs = Job.objects.count()
            completed = Job.objects.filter(status='COMPLETED').count()
            completion_rate = (completed / total_jobs * 100) if total_jobs > 0 else 0

            response['content'] = f"""현재 시스템 성과를 분석해드리겠습니다.

📈 주요 KPI:
- 작업 완료율: {completion_rate:.1f}%
- 총 등록 작업: {total_jobs}개
- 완료된 작업: {completed}개

💡 개선 제안:
1. 병목 공정 식별을 위해 '실시간 생산 모니터링' 메뉴를 확인하세요.
2. 기계 가동률 향상을 위해 유지보수 스케줄을 최적화하세요.
3. 우선순위가 높은 작업부터 처리하여 납기 준수율을 높이세요.
"""

        # 기본 응답
        else:
            response['content'] = f"""'{user_message}'에 대해 답변드리겠습니다.

다음과 같은 주제로 질문해주세요:
- 📦 작업 현황 및 진행 상태
- 🏭 기계 가동 현황 및 성능
- 📅 스케줄링 및 최적화
- 📊 성과 분석 및 KPI
- 🔔 알림 및 이슈 관리

구체적인 질문을 하시면 더 정확한 답변을 드릴 수 있습니다.
"""

        return response


class PredictiveAnalyticsViewSet(viewsets.ViewSet):
    """예측 분석 API"""

    @action(detail=False, methods=['get'])
    def list_models(self, request):
        """예측 모델 목록"""
        models = PredictiveModel.objects.filter(status='ACTIVE')

        data = [{
            'id': model.id,
            'model_name': model.model_name,
            'model_type': model.model_type,
            'algorithm': model.algorithm,
            'accuracy': model.accuracy,
            'last_trained_at': model.last_trained_at,
            'version': model.version
        } for model in models]

        return Response(data)

    @action(detail=False, methods=['get'])
    def demand_forecast(self, request):
        """수요 예측"""
        # 최근 30일 작업 데이터 기반 다음 7일 예측
        days = 7
        predictions = []

        for i in range(1, days + 1):
            predicted_date = timezone.now().date() + timedelta(days=i)
            # 실제로는 ML 모델 사용, 여기서는 간단한 시뮬레이션
            base_demand = random.randint(10, 30)
            predictions.append({
                'date': predicted_date,
                'predicted_jobs': base_demand,
                'confidence': round(random.uniform(0.75, 0.95), 2),
                'trend': 'increasing' if i % 3 == 0 else 'stable'
            })

        return Response({
            'forecast_period': f'{days} days',
            'predictions': predictions,
            'model_info': {
                'algorithm': 'LSTM',
                'accuracy': 0.87,
                'last_trained': '2024-01-15'
            }
        })

    @action(detail=False, methods=['get'])
    def maintenance_prediction(self, request):
        """고장 예측"""
        machines = Machine.objects.all()[:10]
        predictions = []

        for machine in machines:
            # 실제로는 센서 데이터 기반 ML 모델 사용
            risk_score = random.uniform(0.1, 0.9)
            days_until_maintenance = random.randint(5, 60)

            predictions.append({
                'machine_id': machine.machine_id,
                'machine_code': machine.machine_code,
                'machine_name': machine.machine_name,
                'failure_risk': round(risk_score, 2),
                'risk_level': 'high' if risk_score > 0.7 else 'medium' if risk_score > 0.4 else 'low',
                'estimated_days_until_maintenance': days_until_maintenance,
                'recommended_action': 'Immediate inspection' if risk_score > 0.7 else 'Schedule maintenance'
            })

        # 리스크 높은 순으로 정렬
        predictions.sort(key=lambda x: x['failure_risk'], reverse=True)

        return Response({
            'total_machines': len(predictions),
            'high_risk_count': len([p for p in predictions if p['risk_level'] == 'high']),
            'predictions': predictions
        })

    @action(detail=False, methods=['get'])
    def delivery_prediction(self, request):
        """납기 예측"""
        jobs = Job.objects.filter(status__in=['PENDING', 'IN_PROGRESS'])[:20]
        predictions = []

        for job in jobs:
            # 실제로는 과거 데이터 및 현재 진행 상황 기반 ML 예측
            on_time_probability = random.uniform(0.5, 0.99)
            delay_days = random.randint(0, 10) if on_time_probability < 0.7 else 0

            predictions.append({
                'job_id': job.job_id,
                'job_code': job.job_code,
                'job_name': job.job_name,
                'due_date': job.due_date,
                'on_time_probability': round(on_time_probability, 2),
                'status': 'on_track' if on_time_probability > 0.8 else 'at_risk' if on_time_probability > 0.6 else 'delayed',
                'estimated_delay_days': delay_days,
                'recommended_priority': 'urgent' if on_time_probability < 0.7 else 'normal'
            })

        return Response({
            'total_jobs': len(predictions),
            'at_risk_count': len([p for p in predictions if p['status'] == 'at_risk']),
            'delayed_count': len([p for p in predictions if p['status'] == 'delayed']),
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

        return Response({'message': 'Recommendation applied successfully'})

    @action(detail=False, methods=['post'])
    def generate_recommendations(self, request):
        """AI 추천 생성 (시뮬레이션)"""
        # 실제로는 ML 모델 및 규칙 엔진 사용
        recommendations_created = []

        # 1. 스케줄 최적화 추천
        if random.random() > 0.5:
            rec = SmartRecommendation.objects.create(
                recommendation_type='SCHEDULE_OPTIMIZATION',
                title='유전 알고리즘으로 스케줄 재최적화 권장',
                description='현재 스케줄 대비 평균 완료시간을 15% 단축할 수 있습니다.',
                reasoning='최근 작업 패턴 분석 결과, GA 알고리즘이 현재 상황에 더 적합합니다.',
                expected_benefit='평균 완료시간 15% 감소, 기계 가동률 8% 향상',
                confidence_score=0.87,
                priority=3,
                suggested_action={'algorithm': 'GA', 'parameters': {'population': 100, 'generations': 50}}
            )
            recommendations_created.append(rec.id)

        # 2. 유지보수 시기 추천
        if random.random() > 0.5:
            rec = SmartRecommendation.objects.create(
                recommendation_type='MAINTENANCE_TIMING',
                title='M-001 기계 예방 유지보수 필요',
                description='고장 위험도가 높아지고 있습니다. 3일 이내 유지보수를 권장합니다.',
                reasoning='진동 센서 데이터 이상 패턴 감지, 유사 케이스 분석 결과',
                expected_benefit='예상 고장 방지, 가동 중단 최소화',
                confidence_score=0.92,
                priority=4,
                affected_machines=['M-001']
            )
            recommendations_created.append(rec.id)

        # 3. 병목 해소 추천
        if random.random() > 0.5:
            rec = SmartRecommendation.objects.create(
                recommendation_type='BOTTLENECK_RESOLUTION',
                title='CNC 가공 공정 병목 해소 방안',
                description='CNC 기계의 작업 대기 시간이 과도합니다.',
                reasoning='실시간 모니터링 데이터 분석 결과, CNC 공정에서 평균 대기시간 45분',
                expected_benefit='전체 생산 처리량 20% 향상',
                confidence_score=0.85,
                priority=3,
                suggested_action={'action': 'add_shift', 'details': 'CNC 작업에 추가 근무조 투입'}
            )
            recommendations_created.append(rec.id)

        return Response({
            'message': f'{len(recommendations_created)} recommendations generated',
            'recommendation_ids': recommendations_created
        })


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
            'unread_count': len([i for i in data if not i['is_read']]),
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
        """AI 인사이트 자동 생성"""
        insights_created = []

        # 1. 이상 징후 감지
        if random.random() > 0.5:
            insight = AIInsight.objects.create(
                insight_type='ANOMALY',
                title='기계 M-005 비정상 진동 패턴 감지',
                description='최근 24시간 동안 평균 진동값이 정상 범위를 20% 초과했습니다.',
                severity='HIGH',
                supporting_data={'machine_id': 'M-005', 'avg_vibration': 4.2, 'threshold': 3.5}
            )
            insights_created.append(insight.id)

        # 2. 트렌드 분석
        if random.random() > 0.5:
            insight = AIInsight.objects.create(
                insight_type='TREND',
                title='주간 작업 완료율 지속 증가',
                description='최근 4주 동안 작업 완료율이 매주 평균 3%씩 향상되고 있습니다.',
                severity='LOW',
                supporting_data={'week1': 78, 'week2': 81, 'week3': 84, 'week4': 87}
            )
            insights_created.append(insight.id)

        # 3. 패턴 발견
        if random.random() > 0.5:
            insight = AIInsight.objects.create(
                insight_type='PATTERN',
                title='화요일 오후 생산성 저하 패턴',
                description='매주 화요일 오후 2-4시에 평균 생산성이 15% 감소하는 패턴이 반복됩니다.',
                severity='MEDIUM',
                supporting_data={'pattern': 'weekly', 'day': 'Tuesday', 'time': '14:00-16:00', 'drop': 15}
            )
            insights_created.append(insight.id)

        return Response({
            'message': f'{len(insights_created)} insights generated',
            'insight_ids': insights_created
        })
