from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg, StdDev, Count, Q
from datetime import timedelta
from typing import Dict, List, Any
import os
import logging

from .models import (
    Product, InspectionPlan, QualityMeasurement, ControlChart,
    ProcessCapability, RunRuleViolation, QualityAlert, QualityReport
)
from .serializers import (
    ProductSerializer, InspectionPlanSerializer, QualityMeasurementSerializer,
    QualityMeasurementCreateSerializer, ControlChartSerializer,
    ProcessCapabilitySerializer, RunRuleViolationSerializer,
    QualityAlertSerializer, QualityAlertUpdateSerializer,
    QualityReportSerializer, ControlChartDataSerializer,
    ProcessCapabilityAnalysisSerializer, ChatRequestSerializer,
    ChatResponseSerializer, TimeSeriesAnalysisRequestSerializer,
    TimeSeriesAnalysisResponseSerializer, ForecastRequestSerializer,
    ForecastResponseSerializer, PredictiveMaintenanceRequestSerializer,
    PredictiveMaintenanceResponseSerializer, AnomalyDetectionRequestSerializer,
    AnomalyDetectionResponseSerializer, AIPromptRequestSerializer,
    AIPromptResponseSerializer, AIPromptExecuteSerializer,
    AIPromptExecuteResponseSerializer
)

logger = logging.getLogger(__name__)


class ProductViewSet(viewsets.ModelViewSet):
    """제품 정보 API"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ['product_code', 'is_active']
    search_fields = ['product_code', 'product_name']

    def get_queryset(self):
        """Optimize queryset with select_related/prefetch_related"""
        queryset = super().get_queryset()
        # Prefetch related objects to avoid N+1 queries
        queryset = queryset.prefetch_related(
            'inspection_plans',
            'measurements',
            'alerts',
        )
        return queryset

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """제품 품질 요약 통계"""
        product = self.get_object()
        today = timezone.now()
        week_ago = today - timedelta(days=7)

        # Use aggregate for better performance
        measurements = QualityMeasurement.objects.filter(
            product=product,
            measured_at__gte=week_ago
        ).aggregate(
            total_count=Count('id'),
            out_of_spec=Count('id', filter=Q(is_within_spec=False)),
            out_of_control=Count('id', filter=Q(is_within_control=False)),
        )

        total_count = measurements['total_count'] or 0
        out_of_spec = measurements['out_of_spec'] or 0
        out_of_control = measurements['out_of_control'] or 0

        # 최근 공정능력 지수
        latest_capability = ProcessCapability.objects.filter(
            product=product
        ).order_by('-analyzed_at').first()

        return Response({
            'product_code': product.product_code,
            'product_name': product.product_name,
            'period': '최근 7일',
            'statistics': {
                'total_measurements': total_count,
                'out_of_spec_count': out_of_spec,
                'out_of_spec_rate': round(out_of_spec / total_count * 100, 2) if total_count > 0 else 0,
                'out_of_control_count': out_of_control,
                'out_of_control_rate': round(out_of_control / total_count * 100, 2) if total_count > 0 else 0,
            },
            'capability': {
                'cp': latest_capability.cp if latest_capability else None,
                'cpk': latest_capability.cpk if latest_capability else None,
                'analyzed_at': latest_capability.analyzed_at if latest_capability else None,
            }
        })


class InspectionPlanViewSet(viewsets.ModelViewSet):
    """검사 계획 API"""
    queryset = InspectionPlan.objects.all()
    serializer_class = InspectionPlanSerializer
    filterset_fields = ['product', 'frequency', 'is_active']


class QualityMeasurementViewSet(viewsets.ModelViewSet):
    """품질 측정 데이터 API"""
    queryset = QualityMeasurement.objects.all()
    filterset_fields = ['product', 'is_within_spec', 'is_within_control', 'measured_by']
    search_fields = ['lot_number', 'machine_id']

    def get_queryset(self):
        """Optimize queryset with select_related for ForeignKeys"""
        queryset = super().get_queryset()
        # Select related product to avoid N+1 queries
        queryset = queryset.select_related('product')
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return QualityMeasurementCreateSerializer
        return QualityMeasurementSerializer

    @action(detail=False, methods=['get'])
    def chart_data(self, request):
        """관리도 시각화 데이터 조회"""
        product_id = request.query_params.get('product_id')
        chart_type = request.query_params.get('chart_type', 'XBAR_R')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not product_id:
            return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        measurements = QualityMeasurement.objects.filter(product_id=product_id)

        if start_date:
            measurements = measurements.filter(measured_at__gte=start_date)
        if end_date:
            measurements = measurements.filter(measured_at__lte=end_date)

        # 부분군별 집계
        from django.db.models import Avg, Max, Min, StdDev
        chart_data = []

        if chart_type == 'XBAR_R':
            subgroups = measurements.values('subgroup_number').annotate(
                xbar=Avg('measurement_value'),
                r=Max('measurement_value') - Min('measurement_value'),
                measured_at=Max('measured_at')
            ).order_by('subgroup_number')

            chart_data = list(subgroups)

        elif chart_type == 'XBAR_S':
            subgroups = measurements.values('subgroup_number').annotate(
                xbar=Avg('measurement_value'),
                s=StdDev('measurement_value'),
                measured_at=Max('measured_at')
            ).order_by('subgroup_number')

            chart_data = list(subgroups)

        # 관리 한계선 조회
        control_chart = ControlChart.objects.filter(
            product_id=product_id,
            chart_type=chart_type,
            is_active=True
        ).first()

        limits = {}
        if control_chart:
            if chart_type == 'XBAR_R':
                limits = {
                    'xbar': {
                        'ucl': control_chart.xbar_ucl,
                        'cl': control_chart.xbar_cl,
                        'lcl': control_chart.xbar_lcl
                    },
                    'r': {
                        'ucl': control_chart.r_ucl,
                        'cl': control_chart.r_cl,
                        'lcl': control_chart.r_lcl
                    }
                }
            elif chart_type == 'XBAR_S':
                limits = {
                    'xbar': {
                        'ucl': control_chart.xbar_ucl,
                        'cl': control_chart.xbar_cl,
                        'lcl': control_chart.xbar_lcl
                    },
                    's': {
                        'ucl': control_chart.s_ucl,
                        'cl': control_chart.s_cl,
                        'lcl': control_chart.s_lcl
                    }
                }

        return Response({
            'chart_type': chart_type,
            'data': chart_data,
            'limits': limits
        })

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """측정 데이터 일괄 등록"""
        measurements = request.data.get('measurements', [])

        if not measurements:
            return Response({'error': 'measurements array is required'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = QualityMeasurementCreateSerializer(data=measurements, many=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'created': len(measurements)}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ControlChartViewSet(viewsets.ModelViewSet):
    """관리도 설정 API"""
    queryset = ControlChart.objects.all()
    serializer_class = ControlChartSerializer
    filterset_fields = ['product', 'chart_type', 'is_active']

    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """관리 한계선 계산 (SPC 통계 엔진 호출)"""
        product_id = request.data.get('product_id')
        chart_type = request.data.get('chart_type', 'XBAR_R')
        num_subgroups = request.data.get('num_subgroups', 25)

        if not product_id:
            return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # TODO: SPC 통계 엔진 호출 (Phase 2에서 구현)
        # from apps.spc.services.spc_calculator import SPCCalculator
        # calculator = SPCCalculator()
        # limits = calculator.calculate_control_limits(product_id, chart_type, num_subgroups)

        return Response({
            'message': 'SPC calculator will be implemented in Phase 2',
            'product_id': product_id,
            'chart_type': chart_type
        })


class ProcessCapabilityViewSet(viewsets.ModelViewSet):
    """공정능력 분석 API"""
    queryset = ProcessCapability.objects.all()
    serializer_class = ProcessCapabilitySerializer
    filterset_fields = ['product']

    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """공정능력 분석 실행"""
        serializer = ProcessCapabilityAnalysisSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # TODO: 공정능력 분석 실행 (Phase 2에서 구현)
        # from apps.spc.services.process_capability import ProcessCapabilityAnalyzer
        # analyzer = ProcessCapabilityAnalyzer()
        # result = analyzer.analyze(data['product_id'], data['start_date'], data['end_date'])

        return Response({
            'message': 'Process capability analyzer will be implemented in Phase 2',
            'product_id': data['product_id'],
            'period': f"{data['start_date']} ~ {data['end_date']}"
        })


class RunRuleViolationViewSet(viewsets.ReadOnlyModelViewSet):
    """Run Rule 위반 기록 API (읽기 전용)"""
    queryset = RunRuleViolation.objects.all()
    serializer_class = RunRuleViolationSerializer
    filterset_fields = ['control_chart', 'rule_type', 'is_resolved']

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """위반 해결 처리"""
        violation = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')

        violation.is_resolved = True
        violation.resolved_at = timezone.now()
        violation.resolution_notes = resolution_notes
        violation.save()

        return Response({'status': 'resolved'})

    @action(detail=False, methods=['post'])
    def predict(self, request):
        """AI 기반 Run Rule 위반 예측"""
        from apps.spc.services.runrule_predictor import RunRulePredictor

        product_id = request.data.get('product_id')
        measurement_values = request.data.get('measurement_values', [])

        if not product_id or not measurement_values:
            return Response({
                'error': 'product_id and measurement_values are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                'error': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # AI 예측 실행
        predictor = RunRulePredictor()
        predictions = predictor.predict_violations(product, measurement_values)

        return Response({
            'product_id': product_id,
            'product_code': product.product_code,
            'predictions': predictions,
            'total_measurements': len(measurement_values),
            'violations_detected': len([p for p in predictions if p['is_violation']]),
            'analysis_timestamp': timezone.now().isoformat()
        })


class QualityAlertViewSet(viewsets.ModelViewSet):
    """품질 경고 API"""
    queryset = QualityAlert.objects.all()
    serializer_class = QualityAlertSerializer
    filterset_fields = ['product', 'alert_type', 'priority', 'status']

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return QualityAlertUpdateSerializer
        return QualityAlertSerializer

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """경고 확인 처리"""
        alert = self.get_object()
        acknowledged_by = request.data.get('acknowledged_by', 'admin')

        alert.status = 'ACKNOWLEDGED'
        alert.acknowledged_at = timezone.now()
        alert.acknowledged_by = acknowledged_by
        alert.save()

        return Response({'status': 'acknowledged'})

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """경고 해결 처리"""
        alert = self.get_object()

        alert.status = 'RESOLVED'
        alert.resolved_at = timezone.now()
        alert.resolved_by = request.data.get('resolved_by', 'admin')
        alert.resolution_notes = request.data.get('resolution_notes', '')
        alert.root_cause = request.data.get('root_cause', '')
        alert.corrective_action = request.data.get('corrective_action', '')
        alert.preventive_action = request.data.get('preventive_action', '')
        alert.save()

        return Response({'status': 'resolved'})

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """경고 대시보드 요약"""
        today = timezone.now()
        week_ago = today - timedelta(days=7)

        alerts = QualityAlert.objects.filter(created_at__gte=week_ago)

        summary = {
            'total': alerts.count(),
            'by_priority': {
                'urgent': alerts.filter(priority=4).count(),
                'high': alerts.filter(priority=3).count(),
                'medium': alerts.filter(priority=2).count(),
                'low': alerts.filter(priority=1).count(),
            },
            'by_status': {
                'new': alerts.filter(status='NEW').count(),
                'acknowledged': alerts.filter(status='ACKNOWLEDGED').count(),
                'investigating': alerts.filter(status='INVESTIGATING').count(),
                'resolved': alerts.filter(status='RESOLVED').count(),
                'closed': alerts.filter(status='CLOSED').count(),
            },
            'by_type': {}
        }

        # 타입별 집계
        for alert_type, _ in QualityAlert.ALERT_TYPE_CHOICES:
            summary['by_type'][alert_type] = alerts.filter(alert_type=alert_type).count()

        return Response(summary)


class QualityReportViewSet(viewsets.ModelViewSet):
    """품질 보고서 API"""
    queryset = QualityReport.objects.all()
    serializer_class = QualityReportSerializer
    filterset_fields = ['report_type', 'generated_by']

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """품질 보고서 생성"""
        from .services.report_generator import QualityReportGenerator, ReportExporter
        from datetime import datetime

        report_type = request.data.get('report_type', 'DAILY')
        product_ids = request.data.get('product_ids', [])
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')
        export_format = request.data.get('format', 'json')  # json, markdown

        generator = QualityReportGenerator()
        report_data = None

        # 날짜 파싱
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        else:
            start_date = timezone.now()

        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        else:
            end_date = timezone.now()

        # 보고서 타입별 생성
        if report_type == 'DAILY':
            report_data = generator.generate_daily_report(start_date)
        elif report_type == 'WEEKLY':
            report_data = generator.generate_weekly_report(start_date)
        elif report_type == 'MONTHLY':
            report_data = generator.generate_monthly_report(start_date)
        elif report_type == 'CUSTOM':
            if not start_date_str or not end_date_str:
                return Response(
                    {'error': 'start_date and end_date are required for CUSTOM reports'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            report_data = generator.generate_custom_report(start_date, end_date, product_ids)
        else:
            return Response(
                {'error': f'Invalid report_type: {report_type}. Must be DAILY, WEEKLY, MONTHLY, or CUSTOM'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 포맷별 변환
        if export_format == 'markdown':
            exporter = ReportExporter()
            markdown_content = exporter.export_to_markdown(report_data)

            # DB에 보고서 저장
            report = QualityReport.objects.create(
                report_type=report_type,
                title=f"{report_type} Quality Report",
                description=report_data['period']['formatted'],
                products_data=report_data,
                generated_by=request.user if request.user.is_authenticated else 'system'
            )

            return Response({
                'id': report.id,
                'report_type': report_type,
                'format': 'markdown',
                'content': markdown_content,
                'data': report_data,
                'period': report_data['period']
            })

        # JSON 응답 (기본)
        report = QualityReport.objects.create(
            report_type=report_type,
            title=f"{report_type} Quality Report",
            description=report_data['period']['formatted'],
            products_data=report_data,
            generated_by=request.user if request.user.is_authenticated else 'system'
        )

        return Response({
            'id': report.id,
            'report_type': report_type,
            'format': 'json',
            'data': report_data,
            'period': report_data['period'],
            'generated_at': report_data['generated_at']
        })


class ChatbotViewSet(viewsets.GenericViewSet):
    """AI 챗봇 API with LLM Integration"""
    queryset = Product.objects.all()  # Dummy queryset

    @action(detail=False, methods=['post'])
    def chat(self, request):
        """AI 챗봇 질의응답 with LLM"""
        serializer = ChatRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        message = serializer.validated_data['message']
        product_id = serializer.validated_data.get('product_id')
        session_id = serializer.validated_data.get('session_id')

        # Import LLM-integrated chatbot service
        from .services.spc_chatbot import SPCQualityChatbot
        from .services.llm_service import get_spc_chatbot_service

        # Get intent using original chatbot
        original_chatbot = SPCQualityChatbot()
        intent = original_chatbot._detect_intent(message)

        # Prepare context data
        context_data = self._prepare_context_data(intent, product_id, message)

        # Get conversation history (if session_id provided)
        conversation_history = self._get_conversation_history(session_id) if session_id else None

        # Use LLM service for response generation
        llm_chatbot = get_spc_chatbot_service()
        result = llm_chatbot.chat(
            user_message=message,
            intent=intent,
            context_data=context_data,
            conversation_history=conversation_history
        )

        # Save message to history if session provided
        if session_id:
            self._save_conversation_message(session_id, message, result.get('response', ''))

        # Add context information
        result['intent'] = intent
        result['session_id'] = session_id

        return Response(result)

    def _prepare_context_data(self, intent: str, product_id: int, message: str) -> Dict[str, Any]:
        """Prepare context data for LLM prompt based on intent"""
        context = {}

        if not product_id:
            return context

        try:
            product = Product.objects.get(id=product_id)
            context['product_name'] = product.product_name
            context['product_code'] = product.product_code
        except Product.DoesNotExist:
            return context

        # Intent-specific context preparation
        if intent == 'capability_analysis':
            capability = ProcessCapability.objects.filter(
                product_id=product_id
            ).order_by('-analyzed_at').first()

            if capability:
                context.update({
                    'cp': capability.cp,
                    'cpk': capability.cpk,
                    'usl': capability.usl,
                    'lsl': capability.lsl,
                    'target': capability.target_value,
                    'mean': capability.mean,
                    'std_dev': capability.std_dev,
                    'sample_size': capability.sample_size,
                    'is_normal': 'Yes' if capability.is_normal else 'No',
                    'oos_rate': (capability.out_of_spec_count / capability.sample_size
                                if capability.sample_size > 0 else 0),
                })

        elif intent == 'troubleshooting':
            from datetime import timedelta
            from django.utils import timezone

            week_ago = timezone.now() - timedelta(days=7)

            alerts = QualityAlert.objects.filter(
                product_id=product_id,
                created_at__gte=week_ago
            )

            violations = RunRuleViolation.objects.filter(
                control_chart__product_id=product_id,
                detected_at__gte=week_ago
            )

            context['alert_count'] = alerts.count()
            context['violation_count'] = violations.count()

            # Format alert details
            alert_details = []
            for alert in alerts[:5]:
                alert_details.append(
                    f"- {alert.alert_type}: {alert.description} "
                    f"(Priority: {alert.get_priority_display()})"
                )
            context['alert_details'] = '\n'.join(alert_details) if alert_details else 'No recent alerts'

            # Format violation details
            violation_details = []
            for violation in violations[:5]:
                violation_details.append(
                    f"- {violation.rule_type}: {violation.description}"
                )
            context['violation_details'] = '\n'.join(violation_details) if violation_details else 'No recent violations'

        elif intent == 'trend_analysis':
            import numpy as np
            from datetime import timedelta
            from django.utils import timezone

            thirty_days_ago = timezone.now() - timedelta(days=30)
            measurements = QualityMeasurement.objects.filter(
                product_id=product_id,
                measured_at__gte=thirty_days_ago
            ).order_by('measured_at')

            if measurements.count() >= 30:
                values = list(measurements.values_list('measurement_value', flat=True))
                measurements_array = np.array(values)

                mean = np.mean(measurements_array)
                std = np.std(measurements_array)
                min_val = np.min(measurements_array)
                max_val = np.max(measurements_array)
                cv = (std / mean) * 100 if mean != 0 else 0

                # Trend analysis
                x = np.arange(len(measurements_array))
                z = np.polyfit(x, measurements_array, 1)
                slope = z[0]

                if abs(slope) < 0.0001:
                    trend = "Stable"
                    trend_desc = "Process is stable"
                elif slope > 0:
                    trend = "Increasing"
                    trend_desc = f"Measurements trending upward (slope: {slope:.6f})"
                else:
                    trend = "Decreasing"
                    trend_desc = f"Measurements trending downward (slope: {slope:.6f})"

                context.update({
                    'data_count': len(values),
                    'mean': mean,
                    'std_dev': std,
                    'min_val': min_val,
                    'max_val': max_val,
                    'cv': cv,
                    'trend': trend,
                    'slope': slope,
                    'trend_desc': trend_desc,
                })
            else:
                context['data_count'] = measurements.count()
                context['mean'] = 0
                context['std_dev'] = 0

        elif intent == 'root_cause':
            from datetime import timedelta
            from django.utils import timezone

            week_ago = timezone.now() - timedelta(days=7)
            alerts = QualityAlert.objects.filter(
                product_id=product_id,
                created_at__gte=week_ago
            )

            context['alert_count'] = alerts.count()

            # Issue patterns
            issue_patterns = []
            alert_types = alerts.values('alert_type').annotate(count=Count('alert_type'))
            for alert_type in alert_types:
                issue_patterns.append(
                    f"- {alert_type['alert_type']}: {alert_type['count']} occurrences"
                )

            context['issue_patterns'] = '\n'.join(issue_patterns) if issue_patterns else 'No patterns identified'

        elif intent == 'improvement':
            capability = ProcessCapability.objects.filter(
                product_id=product_id
            ).order_by('-analyzed_at').first()

            if capability:
                from scipy.stats import norm

                current_cpk = capability.cpk
                target_cpk = capability.product.min_cpk_target or 1.33
                cpk_gap = target_cpk - current_cpk

                # Calculate PPM
                z_current = current_cpk * 3
                z_target = target_cpk * 3
                current_ppm = (1 - norm.cdf(z_current)) * 2 * 1_000_000
                target_ppm = (1 - norm.cdf(z_target)) * 2 * 1_000_000

                context.update({
                    'current_cpk': current_cpk,
                    'target_cpk': target_cpk,
                    'cpk_gap': cpk_gap,
                    'current_ppm': current_ppm,
                    'target_ppm': target_ppm,
                })

        return context

    def _get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation history from database"""
        # Import ChatMessage from APS app
        try:
            from apps.aps.ai_llm_models import ChatConversation, ChatMessage

            conversation = ChatConversation.objects.filter(session_id=session_id).first()
            if not conversation:
                return []

            messages = conversation.messages.order_by('timestamp')[-20:]  # Last 20 messages

            history = []
            for msg in messages:
                role = 'user' if msg.role == 'USER' else 'assistant'
                history.append({
                    'role': role,
                    'content': msg.content
                })

            return history
        except Exception as e:
            logger.error(f"Error fetching conversation history: {str(e)}")
            return []

    def _save_conversation_message(self, session_id: str, user_message: str, bot_response: str):
        """Save conversation to database"""
        try:
            from apps.aps.ai_llm_models import ChatConversation, ChatMessage

            conversation, created = ChatConversation.objects.get_or_create(
                session_id=session_id,
                defaults={'title': user_message[:50]}
            )

            # Save user message
            ChatMessage.objects.create(
                conversation=conversation,
                role='USER',
                content=user_message
            )

            # Save bot response
            ChatMessage.objects.create(
                conversation=conversation,
                role='ASSISTANT',
                content=bot_response
            )

            conversation.updated_at = timezone.now()
            conversation.save()

        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")

    @action(detail=False, methods=['get'])
    def capabilities(self, request):
        """챗봇 기능 안내"""
        from .services.llm_service import get_spc_chatbot_service

        # Get LLM provider status
        llm_service = get_spc_chatbot_service()
        provider_status = llm_service.get_provider_status()

        return Response({
            'name': 'SPC Quality Control Chatbot',
            'version': '2.0.0',
            'llm_provider': provider_status,
            'capabilities': [
                {
                    'intent': 'capability_analysis',
                    'description': 'Process Capability Analysis',
                    'description_ko': '공정능력 분석',
                    'examples': [
                        'What is the process capability for product 1?',
                        'Why is the Cpk low?',
                        'Analyze the process capability',
                        '제품 1의 공정능력은 어떤가요?',
                        'Cpk가 낮은 제품을 찾아주세요',
                    ]
                },
                {
                    'intent': 'troubleshooting',
                    'description': 'Quality Issue Troubleshooting',
                    'description_ko': '품질 문제 해결',
                    'examples': [
                        'Why is the defect rate high?',
                        'Help troubleshoot this quality issue',
                        'What are the recent alerts?',
                        '불량률이 높아요',
                        '품질 문제가 발생했어요',
                    ]
                },
                {
                    'intent': 'trend_analysis',
                    'description': 'Data Trend Analysis',
                    'description_ko': '데이터 추세 분석',
                    'examples': [
                        'Show me the recent trend',
                        'Is the process stable?',
                        'Analyze the data trend',
                        '최근 데이터 추세를 보여주세요',
                        '공정이 안정적인가요?',
                    ]
                },
                {
                    'intent': 'root_cause',
                    'description': 'Root Cause Analysis',
                    'description_ko': '근본 원인 분석',
                    'examples': [
                        'What is causing the defects?',
                        'Perform root cause analysis',
                        'Why is Cpk decreasing?',
                        '불량이 발생하는 원인은?',
                        '품질 문제의 근본 원인을 분석해주세요',
                    ]
                },
                {
                    'intent': 'improvement',
                    'description': 'Improvement Recommendations',
                    'description_ko': '개선 방안 제언',
                    'examples': [
                        'How can we improve the process?',
                        'Give me improvement recommendations',
                        'What should we do to increase Cpk?',
                        '공정을 어떻게 개선할까요?',
                        'Cpk 개선 방법을 알려주세요',
                    ]
                }
            ]
        })

    @action(detail=False, methods=['get'])
    def status(self, request):
        """LLM Service Status"""
        from .services.llm_service import get_spc_chatbot_service

        llm_service = get_spc_chatbot_service()
        provider_status = llm_service.get_provider_status()

        return Response({
            'status': 'online',
            'llm_integration': True,
            **provider_status,
            'configuration': {
                'openai_available': bool(os.environ.get('OPENAI_API_KEY')),
                'anthropic_available': bool(os.environ.get('ANTHROPIC_API_KEY')),
                'demo_mode': provider_status['provider'] == 'demo',
            }
        })


class AdvancedControlChartViewSet(viewsets.GenericViewSet):
    """고급 관리도 API (CUSUM, EWMA)"""
    queryset = Product.objects.all()  # Dummy queryset

    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """
        고급 관리도 계산
        CUSUM 또는 EWMA 관리도 계산
        """
        from .services.advanced_control_charts import AdvancedControlChartService

        product_id = request.data.get('product_id')
        chart_type = request.data.get('chart_type', 'CUSUM')  # CUSUM or EWMA
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        # 선택적 파라미터
        k = request.data.get('k', 0.5)  # CUSUM 참조값
        h = request.data.get('h', 5.0)  # CUSUM 결정한계
        lambda_param = request.data.get('lambda_param', 0.2)  # EWMA 스무딩 파라미터
        l = request.data.get('l', 3.0)  # EWMA 관리한계 계수

        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if chart_type not in ['CUSUM', 'EWMA']:
            return Response(
                {'error': 'chart_type must be CUSUM or EWMA'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 제품 정보 조회
            product = Product.objects.get(id=product_id)
            target_value = product.target_value
            usl = product.usl
            lsl = product.lsl

            # 측정 데이터 조회
            measurements = QualityMeasurement.objects.filter(
                product_id=product_id
            )

            if start_date:
                measurements = measurements.filter(measured_at__gte=start_date)
            if end_date:
                measurements = measurements.filter(measured_at__lte=end_date)

            measurements = measurements.order_by('measured_at')

            if measurements.count() < 2:
                return Response(
                    {'error': '최소 2개 이상의 측정 데이터가 필요합니다'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 표준편차 계산
            import numpy as np
            values = list(measurements.values_list('measurement_value', flat=True))
            std_dev = float(np.std(values))

            # 측정 데이터를 딕셔너리 형태로 변환
            measurements_data = [
                {'measurement_value': m.measurement_value}
                for m in measurements
            ]

            # 관리도 계산
            result = AdvancedControlChartService.calculate_from_measurements(
                measurements_data=measurements_data,
                target_value=target_value,
                std_dev=std_dev,
                chart_type=chart_type,
                k=k,
                h=h,
                lambda_param=lambda_param,
                l=l
            )

            # 추가 정보
            result['product_id'] = product_id
            result['product_code'] = product.product_code
            result['product_name'] = product.product_name
            result['usl'] = usl
            result['lsl'] = lsl
            result['data_points'] = len(values)
            result['calculated_at'] = timezone.now().isoformat()

            return Response(result)

        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def compare(self, request):
        """
        CUSUM과 EWMA 비교 분석
        """
        from .services.advanced_control_charts import AdvancedControlChartService

        product_id = request.data.get('product_id')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 제품 및 데이터 조회
            product = Product.objects.get(id=product_id)
            target_value = product.target_value

            measurements = QualityMeasurement.objects.filter(
                product_id=product_id
            )

            if start_date:
                measurements = measurements.filter(measured_at__gte=start_date)
            if end_date:
                measurements = measurements.filter(measured_at__lte=end_date)

            measurements = measurements.order_by('measured_at')

            if measurements.count() < 2:
                return Response(
                    {'error': '최소 2개 이상의 측정 데이터가 필요합니다'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 표준편차 계산
            import numpy as np
            values = list(measurements.values_list('measurement_value', flat=True))
            std_dev = float(np.std(values))

            measurements_data = [
                {'measurement_value': m.measurement_value}
                for m in measurements
            ]

            # CUSUM 계산
            cusum_result = AdvancedControlChartService.calculate_from_measurements(
                measurements_data=measurements_data,
                target_value=target_value,
                std_dev=std_dev,
                chart_type='CUSUM'
            )

            # EWMA 계산
            ewma_result = AdvancedControlChartService.calculate_from_measurements(
                measurements_data=measurements_data,
                target_value=target_value,
                std_dev=std_dev,
                chart_type='EWMA'
            )

            # 권장사항 생성
            recommendations = AdvancedControlChartService.get_recommendations(
                cusum_result, ewma_result
            )

            return Response({
                'product_id': product_id,
                'product_code': product.product_code,
                'product_name': product.product_name,
                'cusum': cusum_result,
                'ewma': ewma_result,
                'recommendations': recommendations,
                'calculated_at': timezone.now().isoformat()
            })

        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TimeSeriesAnalysisViewSet(viewsets.GenericViewSet):
    """
    시계열 분석 API (Time Series Analysis)
    추세 분석, 예측, 이상 감지, 예지 보전 기능 제공
    """
    queryset = Product.objects.all()  # Dummy queryset

    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """
        종합 시계열 분석
        추세, 계절성, 분해, 예측, 이상 감지를 모두 포함
        """
        serializer = TimeSeriesAnalysisRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        product_id = data['product_id']
        days = data['days']
        forecast_steps = data['forecast_steps']

        try:
            from .services.time_series_analysis import TimeSeriesService

            service = TimeSeriesService()
            result = service.analyze_product_timeseries(
                product_id=product_id,
                days=days,
                forecast_steps=forecast_steps
            )

            return Response(result)

        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Time series analysis error: {str(e)}")
            return Response(
                {'error': f'Analysis failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def forecast(self, request):
        """
        시계열 예측
        단일 예측 방법 사용 (MA, ES, LT, COMBINED)
        """
        serializer = ForecastRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        product_id = data['product_id']
        days = data['days']
        forecast_steps = data['forecast_steps']
        method = data['method']

        try:
            from .services.time_series_analysis import ForecastEngine

            # 제품 정보 조회
            product = Product.objects.get(id=product_id)

            # 측정 데이터 조회
            start_date = timezone.now() - timedelta(days=days)
            measurements_qs = QualityMeasurement.objects.filter(
                product_id=product_id,
                measured_at__gte=start_date
            ).order_by('measured_at')

            if measurements_qs.count() < 5:
                return Response(
                    {'error': '최소 5개 이상의 측정 데이터가 필요합니다'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            measurements = list(measurements_qs.values_list('measurement_value', flat=True))
            timestamps = list(measurements_qs.values_list('measured_at', flat=True))

            # 예측 엔진 생성
            engine = ForecastEngine()

            # 예측 방법별 실행
            if method == 'MA':
                forecast_data = engine.simple_ma_forecast(
                    measurements,
                    forecast_steps=forecast_steps,
                    window_size=min(7, len(measurements) // 2)
                )
            elif method == 'ES':
                forecast_data = engine.exponential_smoothing_forecast(
                    measurements,
                    forecast_steps=forecast_steps,
                    alpha=0.3
                )
            elif method == 'LT':
                forecast_data = engine.linear_trend_forecast(
                    measurements,
                    forecast_steps=forecast_steps
                )
            else:  # COMBINED
                forecast_data = engine.combined_forecast(
                    measurements,
                    forecast_steps=forecast_steps
                )

            # 예측 날짜 계산
            last_timestamp = timestamps[-1]
            forecast_dates = []
            for i in range(forecast_steps):
                next_time = last_timestamp + timedelta(hours=i * 8)  # 8시간 간격 가정
                forecast_dates.append(next_time.isoformat())

            # 응답 생성
            response = {
                'product_id': product_id,
                'product_code': product.product_code,
                'method': method,
                'forecast_steps': forecast_steps,
                'forecast_values': forecast_data['forecast_values'],
                'forecast_dates': forecast_dates,
                'accuracy_metrics': forecast_data.get('accuracy_metrics', {}),
                'forecasted_at': timezone.now().isoformat()
            }

            # 신뢰 구간 추가 (있는 경우)
            if 'confidence_interval' in forecast_data:
                response['confidence_interval'] = forecast_data['confidence_interval']

            return Response(response)

        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Forecast error: {str(e)}")
            return Response(
                {'error': f'Forecast failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def maintenance_predict(self, request):
        """
        예지 보전 분석
        설비 건전도, 열화 추세, 고장 예측 제공
        """
        serializer = PredictiveMaintenanceRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        product_id = data['product_id']
        days = data['days']

        try:
            from .services.time_series_analysis import TimeSeriesService

            service = TimeSeriesService()
            result = service.get_maintenance_prediction(
                product_id=product_id,
                days=days
            )

            return Response(result)

        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Maintenance prediction error: {str(e)}")
            return Response(
                {'error': f'Prediction failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def detect_anomalies(self, request):
        """
        이상 감지
        통계적 방법 (Z-score) 및 패턴 기반 이상 감지
        """
        serializer = AnomalyDetectionRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        product_id = data['product_id']
        days = data['days']
        threshold = data['threshold']

        try:
            from .services.time_series_analysis import AnomalyDetector

            # 제품 정보 조회
            product = Product.objects.get(id=product_id)

            # 측정 데이터 조회
            start_date = timezone.now() - timedelta(days=days)
            end_date = timezone.now()

            measurements_qs = QualityMeasurement.objects.filter(
                product_id=product_id,
                measured_at__gte=start_date,
                measured_at__lte=end_date
            ).order_by('measured_at')

            if measurements_qs.count() < 3:
                return Response(
                    {'error': '최소 3개 이상의 측정 데이터가 필요합니다'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            measurements = list(measurements_qs.values_list('measurement_value', flat=True))

            # 이상 감지기 생성
            detector = AnomalyDetector()

            # 통계적 이상 감지
            statistical_anomalies = detector.detect_statistical_anomalies(
                measurements,
                threshold=threshold
            )

            # 패턴 기반 이상 감지
            pattern_anomalies = detector.detect_pattern_anomalies(measurements)

            # 이상 데이터에 인덱스와 타임스탬프 추가
            measurements_with_timestamp = measurements_qs.values('id', 'measurement_value', 'measured_at')

            anomalies_list = []
            for idx, measurement in enumerate(measurements_with_timestamp):
                measurement_idx = idx

                # 통계적 이상 확인
                stat_anomaly = next(
                    (a for a in statistical_anomalies if a['index'] == measurement_idx),
                    None
                )

                # 패턴 기반 이상 확인
                pattern_anomaly = next(
                    (a for a in pattern_anomalies if a['index'] == measurement_idx),
                    None
                )

                if stat_anomaly or pattern_anomaly:
                    anomaly_info = {
                        'id': measurement['id'],
                        'value': measurement['measurement_value'],
                        'measured_at': measurement['measured_at'].isoformat(),
                    }

                    if stat_anomaly:
                        anomaly_info['statistical'] = {
                            'z_score': stat_anomaly['z_score'],
                            'severity': stat_anomaly['severity']
                        }

                    if pattern_anomaly:
                        anomaly_info['pattern'] = {
                            'type': pattern_anomaly['type'],
                            'description': pattern_anomaly['description']
                        }

                    # 이상 점수 계산
                    anomaly_score = detector.calculate_anomaly_score(
                        measurement['measurement_value'],
                        measurements
                    )
                    anomaly_info['anomaly_score'] = anomaly_score

                    anomalies_list.append(anomaly_info)

            # 응답 생성
            response = {
                'product_id': product_id,
                'product_code': product.product_code,
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'total_data_points': len(measurements),
                'anomalies': anomalies_list,
                'anomaly_count': len(anomalies_list),
                'anomaly_rate': round(len(anomalies_list) / len(measurements) * 100, 2) if measurements else 0,
                'detection_method': 'statistical_and_pattern',
                'threshold': threshold,
                'detected_at': timezone.now().isoformat()
            }

            return Response(response)

        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Anomaly detection error: {str(e)}")
            return Response(
                {'error': f'Detection failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def capabilities(self, request):
        """
        시계열 분석 기능 안내
        """
        return Response({
            'name': 'Time Series Analysis Service',
            'version': '1.0.0',
            'description': '시계열 분석, 예측, 이상 감지, 예지 보전 기능을 제공합니다',
            'endpoints': {
                'analyze': {
                    'method': 'POST',
                    'description': '종합 시계열 분석 (추세, 계절성, 분해, 예측, 이상 감지)',
                    'parameters': {
                        'product_id': '제품 ID (필수)',
                        'days': '분석 기간 (일, 기본값: 30)',
                        'forecast_steps': '예측 스텝 수 (기본값: 5)'
                    }
                },
                'forecast': {
                    'method': 'POST',
                    'description': '시계열 예측',
                    'parameters': {
                        'product_id': '제품 ID (필수)',
                        'days': '학습 데이터 기간 (일, 기본값: 30)',
                        'forecast_steps': '예측 스텝 수 (기본값: 5)',
                        'method': '예측 방법 (MA, ES, LT, COMBINED, 기본값: COMBINED)'
                    }
                },
                'maintenance_predict': {
                    'method': 'POST',
                    'description': '예지 보전 분석',
                    'parameters': {
                        'product_id': '제품 ID (필수)',
                        'days': '분석 기간 (일, 기본값: 30)'
                    }
                },
                'detect_anomalies': {
                    'method': 'POST',
                    'description': '이상 감지',
                    'parameters': {
                        'product_id': '제품 ID (필수)',
                        'days': '분석 기간 (일, 기본값: 30)',
                        'threshold': 'Z-score 임계값 (기본값: 3.0)'
                    }
                }
            },
            'forecast_methods': {
                'MA': '이동평균 (Moving Average) - 안정적인 데이터에 적합',
                'ES': '지수평활 (Exponential Smoothing) - 최근 데이터에 가중치',
                'LT': '선형추세 (Linear Trend) - 추세가 명확한 경우',
                'COMBINED': '앙상블 (Combined) - 여러 방법 결합 (권장)'
            },
            'anomaly_detection': {
                'statistical': 'Z-score 기반 통계적 이상 감지',
                'pattern': 'Spike, Trend Shift 등 패턴 기반 감지',
                'anomaly_score': '0-100 사이의 이상 점수'
            },
            'predictive_maintenance': {
                'equipment_health': '설비 건전도 점수 (0-100)',
                'degradation_trend': '열화 추세 분석',
                'failure_prediction': '규격 벗어남 예측 시점'
            }
        })


class AIPromptViewSet(viewsets.GenericViewSet):
    """
    AI 프롬프트 관리 API
    검수 프로세스 설계, 기준표 생성, Q-COST 분류, COPQ 리포트 등의 AI 기능을 제공
    """
    queryset = Product.objects.all()  # Dummy queryset

    @action(detail=False, methods=['get'])
    def use_cases(self, request):
        """사용 가능한 Use Case 목록"""
        from .services.ai_prompt_service import AIPromptService

        use_cases = AIPromptService.get_available_use_cases()

        return Response({
            'use_cases': use_cases,
            'total_count': len(use_cases)
        })

    @action(detail=False, methods=['post'])
    def format(self, request):
        """프롬프트 포맷팅 (입력 데이터 적용)"""
        serializer = AIPromptRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        use_case = data['use_case']
        inputs = data['inputs']
        language = data.get('language', 'ko')

        try:
            from .services.ai_prompt_service import AIPromptService

            result = AIPromptService.get_formatted_prompt(use_case, inputs, language)

            return Response(result)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Prompt format error: {str(e)}")
            return Response(
                {'error': f'Format failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def execute(self, request):
        """
        AI 프롬프트 실행

        프롬프트를 생성하고 AI 모델을 호출한 후 결과를 저장합니다.
        현재는 모의 출력을 반환하지만, 실제 LLM API 연동 시 실제 출력을 반환합니다.
        """
        serializer = AIPromptExecuteSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        use_case = data['use_case']
        inputs = data['inputs']
        language = data.get('language', 'ko')
        model_name = data.get('model_name', 'gpt-4')

        # 사이트 ID와 사용자 ID (실제로는 인증에서 가져와야 함)
        site_id = request.data.get('site_id', 1)
        user_id = request.data.get('user_id', 1)

        try:
            from .services.ai_prompt_service import AIPromptService

            result = AIPromptService.execute_prompt(
                use_case=use_case,
                inputs=inputs,
                site_id=site_id,
                user_id=user_id,
                language=language,
                model_name=model_name
            )

            return Response(result)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Prompt execute error: {str(e)}")
            return Response(
                {'error': f'Execution failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def outputs(self, request):
        """AI 출력 결과 목록 조회"""
        site_id = request.query_params.get('site_id', 1)
        use_case = request.query_params.get('use_case')
        limit = int(request.query_params.get('limit', 50))

        try:
            from .services.ai_prompt_service import AIPromptService

            outputs = AIPromptService.list_ai_outputs(site_id, use_case, limit)

            return Response({
                'outputs': outputs,
                'total_count': len(outputs)
            })

        except Exception as e:
            logger.error(f"List outputs error: {str(e)}")
            return Response(
                {'error': f'Failed to list outputs: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def output_detail(self, request):
        """AI 출력 결과 상세 조회"""
        ai_output_id = request.query_params.get('ai_output_id')

        if not ai_output_id:
            return Response(
                {'error': 'ai_output_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from .services.ai_prompt_service import AIPromptService

            output = AIPromptService.get_ai_output(int(ai_output_id))

            if not output:
                return Response(
                    {'error': 'AI output not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(output)

        except Exception as e:
            logger.error(f"Get output error: {str(e)}")
            return Response(
                {'error': f'Failed to get output: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def capabilities(self, request):
        """
        AI 프롬프트 시스템 기능 안내
        """
        from .services.ai_prompt_service import AIPromptService

        use_cases = AIPromptService.get_available_use_cases()

        return Response({
            'name': 'AI Prompt Management System',
            'version': '1.0.0',
            'description': '검수 프로세스 설계, 기준표 생성, Q-COST 분류, COPQ 리포트 등의 AI 기능을 제공합니다',
            'use_cases': use_cases,
            'endpoints': {
                'use_cases': {
                    'method': 'GET',
                    'description': '사용 가능한 Use Case 목록 조회'
                },
                'format': {
                    'method': 'POST',
                    'description': '프롬프트 포맷팅 (입력 데이터 적용)',
                    'parameters': {
                        'use_case': '사용 케이스 (PROCESS_DESIGN, CRITERIA_CHECKLIST, QCOST_CLASSIFY, COPQ_REPORT)',
                        'inputs': '입력 데이터 (JSON)',
                        'language': '언어 (ko/en/zh, 기본값: ko)'
                    }
                },
                'execute': {
                    'method': 'POST',
                    'description': 'AI 프롬프트 실행 및 결과 저장',
                    'parameters': {
                        'use_case': '사용 케이스',
                        'inputs': '입력 데이터 (JSON)',
                        'language': '언어 (기본값: ko)',
                        'model_name': 'AI 모델 이름 (기본값: gpt-4)',
                        'site_id': '사이트 ID (기본값: 1)',
                        'user_id': '사용자 ID (기본값: 1)'
                    }
                },
                'outputs': {
                    'method': 'GET',
                    'description': 'AI 출력 결과 목록 조회',
                    'parameters': {
                        'site_id': '사이트 ID (기본값: 1)',
                        'use_case': '사용 케이스 (선택)',
                        'limit': '최대 결과 수 (기본값: 50)'
                    }
                },
                'output_detail': {
                    'method': 'GET',
                    'description': 'AI 출력 결과 상세 조회',
                    'parameters': {
                        'ai_output_id': 'AI 출력 ID (필수)'
                    }
                }
            },
            'features': {
                'caching': '동일 입력에 대한 결과 캐싱',
                'versioning': '프롬프트 버전 관리',
                'input_validation': '입력 스키마 검증',
                'output_storage': 'AI 출력 결과 저장 및 조회',
                'mock_mode': '테스트용 모의 출력 지원'
            }
        })
