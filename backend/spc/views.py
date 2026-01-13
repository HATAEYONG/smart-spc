"""
SPC Views - SPC-01
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from datetime import datetime
import uuid

from smart_spc.exceptions import api_response
from .serializers import (
    SamplingRuleSerializer, SpcChartDefSerializer, SpcPointSerializer, SpcEventSerializer,
    SpcChartCreateRequestSerializer, SpcRecalcResponseSerializer, SpcEventCreateRequestSerializer
)
from .models import SamplingRule, SpcChartDefinition, SpcPoint, SpcEvent


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sampling_rule(request):
    """Get sampling rule based on standard, AQL, and lot size"""
    standard = request.query_params.get('standard')
    aql = request.query_params.get('aql')
    lot_size = int(request.query_params.get('lot_size', 0))

    if not standard or not aql or not lot_size:
        return api_response(ok=False, data=None, error="standard, aql, and lot_size are required", status_code=status.HTTP_400_BAD_REQUEST)

    try:
        rule = SamplingRule.objects.filter(
            standard=standard,
            aql=float(aql),
            lot_size_from__lte=lot_size,
            lot_size_to__gte=lot_size
        ).first()

        if rule:
            data = {
                'standard': rule.standard,
                'aql': rule.aql,
                'lot_size': lot_size,
                'sample_size': rule.sample_size,
                'accept_limit': rule.accept_limit,
                'reject_limit': rule.reject_limit
            }
        else:
            # Default sampling rule if not found
            data = {
                'standard': standard,
                'aql': float(aql),
                'lot_size': lot_size,
                'sample_size': max(5, lot_size // 100),
                'accept_limit': 1,
                'reject_limit': 2
            }

        return api_response(ok=True, data=data, error=None)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_chart(request):
    """Create SPC chart definition"""
    serializer = SpcChartCreateRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response(ok=False, data=None, error=str(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

    try:
        chart = SpcChartDefinition.objects.create(
            chart_def_id=serializer.validated_data.get('chart_def_id', f"CHART-{uuid.uuid4().hex[:8].upper()}"),
            parameter_id=serializer.validated_data['parameter_id'],
            chart_type=serializer.validated_data['chart_type'],
            sample_size=serializer.validated_data.get('sample_size', 5),
            is_active=True
        )

        data = {
            'chart_def_id': chart.chart_def_id,
            'parameter_id': chart.parameter_id,
            'chart_type': chart.chart_type,
            'sample_size': chart.sample_size
        }
        return api_response(ok=True, data=data, error=None)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def recalc_chart(request, chart_def_id):
    """Recalculate SPC chart points"""
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')

    if not from_date or not to_date:
        return api_response(ok=False, data=None, error="from_date and to_date are required", status_code=status.HTTP_400_BAD_REQUEST)

    try:
        chart_def = SpcChartDefinition.objects.get(chart_def_id=chart_def_id)

        # TODO: Implement actual recalculation logic
        # This would calculate UCL, CL, LCL and create points from inspection results

        data = {
            'chart_def_id': chart_def_id,
            'points_created': 0,
            'violations': 0
        }
        return api_response(ok=True, data=data, error="Recalculation not yet implemented")
    except SpcChartDefinition.DoesNotExist:
        return api_response(ok=False, data=None, error="Chart definition not found", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_points(request, chart_def_id):
    """Get SPC chart points"""
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')

    try:
        chart_def = SpcChartDefinition.objects.get(chart_def_id=chart_def_id)
        points_qs = SpcPoint.objects.filter(chart_def=chart_def)

        if from_date and to_date:
            from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
            to_datetime = datetime.strptime(to_date, '%Y-%m-%d')
            points_qs = points_qs.filter(timestamp__range=[from_datetime, to_datetime])

        points_qs = points_qs.order_by('-timestamp')[:1000]  # Limit to last 1000 points

        data = {
            'chart_type': chart_def.chart_type,
            'chart_def_id': chart_def_id,
            'ucl': chart_def.ucl,
            'cl': chart_def.cl,
            'lcl': chart_def.lcl,
            'points': [
                {
                    'point_id': point.point_id,
                    'timestamp': point.timestamp.isoformat(),
                    'sample_id': point.sample_id,
                    'value': point.value,
                    'mean': point.mean,
                    'range_val': point.range_val,
                    'std_dev': point.std_dev,
                    'violated_rules': point.violated_rules
                }
                for point in points_qs
            ]
        }
        return api_response(ok=True, data=data, error=None)
    except SpcChartDefinition.DoesNotExist:
        return api_response(ok=False, data=None, error="Chart definition not found", status_code=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return api_response(ok=False, data=None, error="Invalid date format. Use YYYY-MM-DD", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_event(request):
    """Create SPC event"""
    serializer = SpcEventCreateRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response(ok=False, data=None, error=str(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

    try:
        chart_def = SpcChartDefinition.objects.get(chart_def_id=serializer.validated_data['chart_def_id'])

        event = SpcEvent.objects.create(
            event_id=f"EVT-{uuid.uuid4().hex[:8].upper()}",
            chart_def=chart_def,
            event_type=serializer.validated_data['event_type'],
            triggered_at=datetime.now(),
            description=serializer.validated_data['description'],
            severity=serializer.validated_data['severity'],
            status='OPEN'
        )

        data = {
            'event_id': event.event_id,
            'event_type': event.event_type,
            'severity': event.severity,
            'status': event.status
        }
        return api_response(ok=True, data=data, error=None)
    except SpcChartDefinition.DoesNotExist:
        return api_response(ok=False, data=None, error="Chart definition not found", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
