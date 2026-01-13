"""
QA Views - QA-01/02/03
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
import uuid

from smart_spc.exceptions import api_response
from .serializers import (
    QaProcessSerializer, QaChecklistItemSerializer, QaAssessmentSerializer, QaFindingSerializer,
    CapaSerializer, CapaActionSerializer, AIRootCauseCAPARequestSerializer, AIRootCauseCAPAResponseSerializer
)
from .models import (
    QaProcess, QaChecklistItem, QaAssessment, QaFinding,
    Capa, CapaAction, AIRootCauseAnalysisHistory
)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_qa_processes(request):
    """Get all QA processes"""
    try:
        processes = QaProcess.objects.all()
        data = [
            {
                'qa_process_id': proc.qa_process_id,
                'process_type': proc.process_type,
                'title': proc.title,
                'description': proc.description,
                'scheduled_at': proc.scheduled_at.isoformat(),
                'status': proc.status
            }
            for proc in processes
        ]
        return api_response(ok=True, data=data, error=None)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_qa_process(request):
    """Create QA process"""
    serializer = QaProcessSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response(ok=False, data=None, error=str(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

    try:
        process = QaProcess.objects.create(
            qa_process_id=serializer.validated_data.get('qa_process_id', f"QA-{uuid.uuid4().hex[:8].upper()}"),
            process_type=serializer.validated_data['process_type'],
            title=serializer.validated_data['title'],
            description=serializer.validated_data.get('description', ''),
            scheduled_at=serializer.validated_data['scheduled_at'],
            status='PLANNED'
        )
        return api_response(ok=True, data={'qa_process_id': process.qa_process_id}, error=None)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_qa_checklist_items(request, qa_process_id):
    """Get QA checklist items for a process"""
    try:
        items = QaChecklistItem.objects.filter(qa_process__qa_process_id=qa_process_id)
        data = [
            {
                'item_id': item.item_id,
                'qa_process_id': item.qa_process.qa_process_id,
                'check_point': item.check_point,
                'requirement': item.requirement,
                'verification_method': item.verification_method,
                'is_compliant': item.is_compliant,
                'notes': item.notes
            }
            for item in items
        ]
        return api_response(ok=True, data=data, error=None)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_qa_checklist_item(request, qa_process_id):
    """Create QA checklist item"""
    serializer = QaChecklistItemSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response(ok=False, data=None, error=str(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

    try:
        qa_process = QaProcess.objects.get(qa_process_id=qa_process_id)
        item = QaChecklistItem.objects.create(
            item_id=serializer.validated_data.get('item_id', f"CHECK-{uuid.uuid4().hex[:8].upper()}"),
            qa_process=qa_process,
            check_point=serializer.validated_data['check_point'],
            requirement=serializer.validated_data['requirement'],
            verification_method=serializer.validated_data.get('verification_method', '')
        )
        return api_response(ok=True, data={'item_id': item.item_id}, error=None)
    except QaProcess.DoesNotExist:
        return api_response(ok=False, data=None, error="QA process not found", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_qa_assessments(request, qa_process_id):
    """Get QA assessments for a process"""
    try:
        assessments = QaAssessment.objects.filter(qa_process__qa_process_id=qa_process_id)
        data = [
            {
                'assessment_id': assess.assessment_id,
                'qa_process_id': assess.qa_process.qa_process_id,
                'assessed_at': assess.assessed_at.isoformat(),
                'assessed_by': assess.assessed_by,
                'overall_score': assess.overall_score,
                'conclusion': assess.conclusion
            }
            for assess in assessments
        ]
        return api_response(ok=True, data=data, error=None)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_qa_assessment(request, qa_process_id):
    """Create QA assessment"""
    serializer = QaAssessmentSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response(ok=False, data=None, error=str(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

    try:
        qa_process = QaProcess.objects.get(qa_process_id=qa_process_id)
        assessment = QaAssessment.objects.create(
            assessment_id=serializer.validated_data.get('assessment_id', f"ASSESS-{uuid.uuid4().hex[:8].upper()}"),
            qa_process=qa_process,
            assessed_at=serializer.validated_data['assessed_at'],
            assessed_by=serializer.validated_data['assessed_by'],
            overall_score=serializer.validated_data['overall_score'],
            conclusion=serializer.validated_data['conclusion'],
            recommendations=serializer.validated_data.get('recommendations', '')
        )
        return api_response(ok=True, data={'assessment_id': assessment.assessment_id}, error=None)
    except QaProcess.DoesNotExist:
        return api_response(ok=False, data=None, error="QA process not found", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_qa_findings(request, qa_process_id):
    """Get QA findings for a process"""
    try:
        findings = QaFinding.objects.filter(qa_process__qa_process_id=qa_process_id, is_resolved=False)
        data = [
            {
                'finding_id': find.finding_id,
                'qa_process_id': find.qa_process.qa_process_id,
                'severity': find.severity,
                'description': find.description,
                'root_cause': find.root_cause,
                'corrective_action': find.corrective_action,
                'is_resolved': find.is_resolved
            }
            for find in findings
        ]
        return api_response(ok=True, data=data, error=None)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_qa_finding(request, qa_process_id):
    """Create QA finding"""
    serializer = QaFindingSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response(ok=False, data=None, error=str(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

    try:
        qa_process = QaProcess.objects.get(qa_process_id=qa_process_id)
        finding = QaFinding.objects.create(
            finding_id=serializer.validated_data.get('finding_id', f"FIND-{uuid.uuid4().hex[:8].upper()}"),
            qa_process=qa_process,
            severity=serializer.validated_data['severity'],
            description=serializer.validated_data['description'],
            root_cause=serializer.validated_data.get('root_cause', ''),
            corrective_action=serializer.validated_data.get('corrective_action', '')
        )
        return api_response(ok=True, data={'finding_id': finding.finding_id}, error=None)
    except QaProcess.DoesNotExist:
        return api_response(ok=False, data=None, error="QA process not found", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_capas(request):
    """Get all CAPAs"""
    try:
        capas = Capa.objects.all()
        data = [
            {
                'capa_id': capa.capa_id,
                'source_type': capa.source_type,
                'source_id': capa.source_id,
                'title': capa.title,
                'description': capa.description,
                'severity': capa.severity,
                'status': capa.status,
                'assigned_to': capa.assigned_to,
                'opened_at': capa.opened_at.isoformat(),
                'target_date': capa.target_date.isoformat()
            }
            for capa in capas
        ]
        return api_response(ok=True, data=data, error=None)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_capa(request):
    """Create CAPA"""
    serializer = CapaSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response(ok=False, data=None, error=str(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

    try:
        capa = Capa.objects.create(
            capa_id=serializer.validated_data.get('capa_id', f"CAPA-{uuid.uuid4().hex[:8].upper()}"),
            source_type=serializer.validated_data['source_type'],
            source_id=serializer.validated_data['source_id'],
            title=serializer.validated_data['title'],
            description=serializer.validated_data['description'],
            severity=serializer.validated_data['severity'],
            assigned_to=serializer.validated_data['assigned_to'],
            target_date=serializer.validated_data['target_date'],
            status='OPEN'
        )
        return api_response(ok=True, data={'capa_id': capa.capa_id}, error=None)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_capa_actions(request, capa_id):
    """Get CAPA actions"""
    try:
        actions = CapaAction.objects.filter(capa__capa_id=capa_id)
        data = [
            {
                'action_id': act.action_id,
                'capa_id': act.capa.capa_id,
                'action_type': act.action_type,
                'description': act.description,
                'assignee': act.assignee,
                'due_date': act.due_date.isoformat(),
                'status': act.status
            }
            for act in actions
        ]
        return api_response(ok=True, data=data, error=None)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_capa_action(request, capa_id):
    """Create CAPA action"""
    serializer = CapaActionSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response(ok=False, data=None, error=str(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

    try:
        capa = Capa.objects.get(capa_id=capa_id)
        action = CapaAction.objects.create(
            action_id=serializer.validated_data.get('action_id', f"ACT-{uuid.uuid4().hex[:8].upper()}"),
            capa=capa,
            action_type=serializer.validated_data['action_type'],
            description=serializer.validated_data['description'],
            assignee=serializer.validated_data['assignee'],
            due_date=serializer.validated_data['due_date'],
            status='PENDING'
        )
        return api_response(ok=True, data={'action_id': action.action_id}, error=None)
    except Capa.DoesNotExist:
        return api_response(ok=False, data=None, error="CAPA not found", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def analyze_root_cause(request):
    """AI-powered root cause analysis"""
    serializer = AIRootCauseCAPARequestSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response(ok=False, data=None, error=str(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

    try:
        # TODO: Integrate with AI service
        analysis = AIRootCauseAnalysisHistory.objects.create(
            analysis_id=f"AI-RCA-{uuid.uuid4().hex[:8].upper()}",
            problem_description=serializer.validated_data['problem_description'],
            defect_details=serializer.validated_data['defect_details'],
            context=serializer.validated_data.get('context', ''),
            root_cause='AI service not yet implemented',
            confidence=0.0,
            recommended_corrective_actions=[],
            recommended_preventive_actions=[],
            is_applied=False
        )

        return api_response(
            ok=True,
            data={
                'root_cause': '',
                'confidence': 0.0,
                'recommended_corrective_actions': [],
                'recommended_preventive_actions': []
            },
            error="AI service not implemented"
        )
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
