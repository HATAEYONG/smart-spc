"""
Dashboard Views - DASH-01
GET /api/v1/dashboard/summary
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status

from smart_spc.exceptions import api_response
from .serializers import DashboardSummarySerializer, KPIsSerializer, TopDefectSerializer, AlertSerializer, AIInsightSerializer
from .models import DashboardKPI, TopDefect, Alert, AIInsight


@api_view(['GET'])
@permission_classes([AllowAny])
def get_dashboard_summary(request):
    """
    Get dashboard summary

    Query Parameters:
    - period: str (YYYY-MM format)

    Returns KPIs, top defects, alerts, and AI insights for the specified period.
    Matches frontend: dashboardService.getSummary(period)
    """
    period = request.query_params.get('period')
    if not period:
        return api_response(
            ok=False,
            data=None,
            error="period parameter is required (YYYY-MM format)",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Get KPIs for the period
    try:
        kpi = DashboardKPI.objects.filter(period=period).first()
        if kpi:
            kpis_data = {
                'copq_rate': kpi.copq_rate,
                'total_copq': kpi.total_copq,
                'total_qcost': kpi.total_qcost,
                'oos_count': kpi.oos_count,
                'spc_open_events': kpi.spc_open_events
            }
        else:
            # Return default values if no data for period
            kpis_data = {
                'copq_rate': 0.0,
                'total_copq': 0,
                'total_qcost': 0,
                'oos_count': 0,
                'spc_open_events': 0
            }
    except Exception as e:
        return api_response(
            ok=False,
            data=None,
            error=f"Error fetching KPIs: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Get top defects for the period
    try:
        top_defects_qs = TopDefect.objects.filter(period=period)[:5]
        top_defects_data = [
            {
                'defect': td.defect,
                'count': td.count,
                'cost': td.cost
            }
            for td in top_defects_qs
        ]
    except Exception as e:
        top_defects_data = []

    # Get recent alerts (last 7 days)
    try:
        from django.utils import timezone
        from datetime import timedelta
        seven_days_ago = timezone.now() - timedelta(days=7)
        alerts_qs = Alert.objects.filter(created_at__gte=seven_days_ago, status='OPEN')[:10]
        alerts_data = [
            {
                'event_id': alert.event_id,
                'type': alert.type,
                'severity': alert.severity,
                'title': alert.title
            }
            for alert in alerts_qs
        ]
    except Exception as e:
        alerts_data = []

    # Get AI insights for the period
    try:
        ai_insights_qs = AIInsight.objects.filter(period=period, actionable=True)[:5]
        ai_insights_data = [
            {
                'ai_id': insight.ai_id,
                'title': insight.title,
                'summary': insight.summary,
                'confidence': insight.confidence
            }
            for insight in ai_insights_qs
        ]
    except Exception as e:
        ai_insights_data = []

    data = {
        'period': period,
        'kpis': kpis_data,
        'top_defects': top_defects_data,
        'alerts': alerts_data,
        'ai_insights': ai_insights_data
    }

    # Validate data with serializer
    serializer = DashboardSummarySerializer(data=data)
    serializer.is_valid(raise_exception=True)

    return api_response(ok=True, data=serializer.validated_data, error=None)
