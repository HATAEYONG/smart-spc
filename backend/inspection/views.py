"""
Inspection Views - INSP-01/02
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
import uuid

from smart_spc.exceptions import api_response
from .serializers import (
    ProcessFlowSerializer, ProcessStepSerializer,
    AIProcessDesignRequestSerializer, AIProcessDesignResponseSerializer,
    AICriteriaChecklistRequestSerializer, AICriteriaChecklistResponseSerializer,
    InspectionRunSerializer, BulkResultRequestSerializer, BulkResultResponseSerializer,
    InspectionJudgeResponseSerializer
)
from .models import ProcessFlow, ProcessStep, InspectionRun, InspectionResult, AIProcessDesignHistory


@api_view(['GET'])
@permission_classes([AllowAny])
def get_flows(request):
    """Get all process flows"""
    try:
        flows = ProcessFlow.objects.filter(is_active=True).prefetch_related('steps')
        data = [
            {
                'flow_id': flow.flow_id,
                'product_id': flow.product_id,
                'version': flow.version,
                'is_active': flow.is_active,
                'steps_count': flow.steps.count()
            }
            for flow in flows
        ]
        return api_response(ok=True, data=data, error=None)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_flow(request):
    """Create process flow"""
    serializer = ProcessFlowSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response(ok=False, data=None, error=str(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

    try:
        flow = ProcessFlow.objects.create(
            flow_id=serializer.validated_data.get('flow_id', f"FLOW-{uuid.uuid4().hex[:8].upper()}"),
            product_id=serializer.validated_data['product_id'],
            version=serializer.validated_data['version'],
            is_active=serializer.validated_data.get('is_active', True)
        )
        return api_response(ok=True, data={'flow_id': flow.flow_id}, error=None)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_steps(request, flow_id):
    """Get process steps for a flow"""
    try:
        steps = ProcessStep.objects.filter(flow__flow_id=flow_id).order_by('step_order')
        data = [
            {
                'step_id': step.step_id,
                'flow_id': step.flow.flow_id,
                'step_order': step.step_order,
                'step_name': step.step_name,
                'inspection_type': step.inspection_type,
                'criteria': step.criteria
            }
            for step in steps
        ]
        return api_response(ok=True, data=data, error=None)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_step(request, flow_id):
    """Create process step"""
    serializer = ProcessStepSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response(ok=False, data=None, error=str(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

    try:
        flow = ProcessFlow.objects.get(flow_id=flow_id)
        step = ProcessStep.objects.create(
            step_id=serializer.validated_data.get('step_id', f"STEP-{uuid.uuid4().hex[:8].upper()}"),
            flow=flow,
            step_order=serializer.validated_data['step_order'],
            step_name=serializer.validated_data['step_name'],
            inspection_type=serializer.validated_data['inspection_type'],
            criteria=serializer.validated_data.get('criteria', {})
        )
        return api_response(ok=True, data={'step_id': step.step_id}, error=None)
    except ProcessFlow.DoesNotExist:
        return api_response(ok=False, data=None, error="Flow not found", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def design_process(request):
    """AI-powered process design"""
    serializer = AIProcessDesignRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response(ok=False, data=None, error=str(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

    try:
        # TODO: Integrate with AI service
        design = AIProcessDesignHistory.objects.create(
            design_id=f"AI-DESIGN-{uuid.uuid4().hex[:8].upper()}",
            product_description=serializer.validated_data['product_description'],
            quality_requirements=serializer.validated_data['quality_requirements'],
            production_volume=serializer.validated_data.get('production_volume', ''),
            confidence=0.0,
            reasoning='AI service not yet implemented',
            is_applied=False
        )

        return api_response(
            ok=True,
            data={
                'proposed_flow': None,
                'confidence': 0.0,
                'reasoning': 'AI service not yet implemented'
            },
            error="AI service not implemented"
        )
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_criteria_checklist(request):
    """AI-powered criteria checklist generation"""
    serializer = AICriteriaChecklistRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response(ok=False, data=None, error=str(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

    # TODO: Integrate with AI service
    return api_response(
        ok=True,
        data={
            'criteria': {},
            'confidence': 0.0,
            'rationale': 'AI service not yet implemented'
        },
        error="AI service not implemented"
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def create_run(request):
    """Create inspection run"""
    serializer = InspectionRunSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response(ok=False, data=None, error=str(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

    try:
        flow = ProcessFlow.objects.get(flow_id=serializer.validated_data['flow_id'])
        run = InspectionRun.objects.create(
            run_id=serializer.validated_data.get('run_id', f"RUN-{uuid.uuid4().hex[:8].upper()}"),
            flow=flow,
            run_type=serializer.validated_data['run_type'],
            inspector_id=serializer.validated_data['inspector_id'],
            started_at=serializer.validated_data.get('started_at'),
            status='OPEN'
        )
        return api_response(ok=True, data={'run_id': run.run_id, 'status': run.status}, error=None)
    except ProcessFlow.DoesNotExist:
        return api_response(ok=False, data=None, error="Flow not found", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def add_bulk_results(request, run_id):
    """Add bulk inspection results"""
    serializer = BulkResultRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response(ok=False, data=None, error=str(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

    try:
        run = InspectionRun.objects.get(run_id=run_id)
        results_data = serializer.validated_data['results']

        created_count = 0
        oos_count = 0

        for result in results_data:
            step = ProcessStep.objects.get(step_id=result['step_id'])
            is_oos = result.get('is_oos', False)

            InspectionResult.objects.create(
                result_id=f"RESULT-{uuid.uuid4().hex[:8].upper()}",
                run=run,
                step=step,
                sample_id=result['sample_id'],
                measurement_value=result['measurement_value'],
                is_oos=is_oos,
                measured_at=result.get('measured_at')
            )

            created_count += 1
            if is_oos:
                oos_count += 1

        data = {'inserted': created_count, 'oos_count': oos_count}
        return api_response(ok=True, data=data, error=None)

    except InspectionRun.DoesNotExist:
        return api_response(ok=False, data=None, error="Run not found", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def judge_run(request, run_id):
    """Judge inspection run"""
    try:
        run = InspectionRun.objects.get(run_id=run_id)
        results = InspectionResult.objects.filter(run=run)

        if not results.exists():
            return api_response(ok=False, data=None, error="No results found for this run", status_code=status.HTTP_400_BAD_REQUEST)

        # Simple judgment logic: if any OOS, then REJECT
        oos_results = results.filter(is_oos=True)
        if oos_results.exists():
            judgment = 'REJECT'
        else:
            judgment = 'ACCEPT'

        # Update run status
        run.status = 'JUDGED'
        run.completed_at = timezone.now()
        run.save()

        from django.utils import timezone
        data = {
            'run_id': run.run_id,
            'judgment': judgment,
            'judged_at': timezone.now().isoformat()
        }
        return api_response(ok=True, data=data, error=None)

    except InspectionRun.DoesNotExist:
        return api_response(ok=False, data=None, error="Run not found", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
