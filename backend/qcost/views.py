"""
Q-COST Views - QCOST-01/02
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.core.paginator import Paginator
from datetime import datetime
import uuid

from smart_spc.exceptions import api_response
from .serializers import (
    QCostCategorySerializer, QCostItemSerializer, QCostEntrySerializer,
    AIQCostClassifyRequestSerializer, AIQCostClassifyResponseSerializer,
    COPQReportRequestSerializer, COPQReportResponseSerializer
)
from .models import QCostCategory, QCostItem, QCostEntry, AIClassificationHistory


@api_view(['GET'])
@permission_classes([AllowAny])
def get_qcost_categories(request):
    """Get all Q-COST categories"""
    try:
        categories = QCostCategory.objects.filter(is_active=True)
        data = [
            {
                'category_id': cat.category_id,
                'category_type': cat.category_type,
                'name': cat.name,
                'description': cat.description
            }
            for cat in categories
        ]
        return api_response(ok=True, data=data, error=None)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_qcost_category(request):
    """Create Q-COST category"""
    serializer = QCostCategorySerializer(data=request.data)
    if not serializer.is_valid():
        return api_response(ok=False, data=None, error=str(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

    try:
        category = QCostCategory.objects.create(
            category_id=serializer.validated_data.get('category_id', f"CAT-{uuid.uuid4().hex[:8].upper()}"),
            category_type=serializer.validated_data['category_type'],
            name=serializer.validated_data['name'],
            description=serializer.validated_data.get('description', '')
        )
        return api_response(ok=True, data={'category_id': category.category_id}, error=None)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_qcost_items(request):
    """Get Q-COST items with pagination"""
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 50))

    try:
        items_qs = QCostItem.objects.filter(is_active=True).select_related('category')
        paginator = Paginator(items_qs, page_size)
        items_page = paginator.get_page(page)

        data = {
            'count': paginator.count,
            'results': [
                {
                    'item_id': item.item_id,
                    'category_id': item.category.category_id,
                    'code': item.code,
                    'name': item.name,
                    'unit': item.unit,
                    'is_active': item.is_active
                }
                for item in items_page
            ]
        }
        return api_response(ok=True, data=data, error=None)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_qcost_item(request):
    """Create Q-COST item"""
    serializer = QCostItemSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response(ok=False, data=None, error=str(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

    try:
        category = QCostCategory.objects.get(category_id=serializer.validated_data['category_id'])
        item = QCostItem.objects.create(
            item_id=serializer.validated_data.get('item_id', f"ITEM-{uuid.uuid4().hex[:8].upper()}"),
            category=category,
            code=serializer.validated_data['code'],
            name=serializer.validated_data['name'],
            unit=serializer.validated_data.get('unit', '')
        )
        return api_response(ok=True, data={'item_id': item.item_id}, error=None)
    except QCostCategory.DoesNotExist:
        return api_response(ok=False, data=None, error="Category not found", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_qcost_entries(request):
    """Get Q-COST entries by date range"""
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 50))

    if not from_date or not to_date:
        return api_response(ok=False, data=None, error="from_date and to_date are required", status_code=status.HTTP_400_BAD_REQUEST)

    try:
        from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
        to_datetime = datetime.strptime(to_date, '%Y-%m-%d')

        entries_qs = QCostEntry.objects.filter(
            occurred_at__range=[from_datetime, to_datetime]
        ).select_related('item__category')

        paginator = Paginator(entries_qs, page_size)
        entries_page = paginator.get_page(page)

        data = {
            'count': paginator.count,
            'results': [
                {
                    'entry_id': entry.entry_id,
                    'item_id': entry.item.item_id,
                    'occurred_at': entry.occurred_at.isoformat(),
                    'quantity': entry.quantity,
                    'unit_cost': entry.unit_cost,
                    'total_cost': entry.total_cost,
                    'reference_id': entry.reference_id,
                    'notes': entry.notes
                }
                for entry in entries_page
            ]
        }
        return api_response(ok=True, data=data, error=None)
    except ValueError:
        return api_response(ok=False, data=None, error="Invalid date format. Use YYYY-MM-DD", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_qcost_entry(request):
    """Create Q-COST entry"""
    serializer = QCostEntrySerializer(data=request.data)
    if not serializer.is_valid():
        return api_response(ok=False, data=None, error=str(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

    try:
        item = QCostItem.objects.get(item_id=serializer.validated_data['item_id'])
        quantity = serializer.validated_data['quantity']
        unit_cost = serializer.validated_data['unit_cost']
        total_cost = quantity * unit_cost

        entry = QCostEntry.objects.create(
            entry_id=serializer.validated_data.get('entry_id', f"ENTRY-{uuid.uuid4().hex[:8].upper()}"),
            item=item,
            occurred_at=serializer.validated_data['occurred_at'],
            quantity=quantity,
            unit_cost=unit_cost,
            total_cost=total_cost,
            reference_id=serializer.validated_data.get('reference_id', ''),
            notes=serializer.validated_data.get('notes', '')
        )
        return api_response(ok=True, data={'entry_id': entry.entry_id, 'total_cost': total_cost}, error=None)
    except QCostItem.DoesNotExist:
        return api_response(ok=False, data=None, error="Item not found", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def classify_qcost(request):
    """Classify Q-COST using AI"""
    serializer = AIQCostClassifyRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response(ok=False, data=None, error=str(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

    # TODO: Integrate with AI service
    # This is a placeholder for AI classification
    try:
        classification = AIClassificationHistory.objects.create(
            classification_id=f"AI-CLASS-{uuid.uuid4().hex[:8].upper()}",
            description=serializer.validated_data['description'],
            amount=serializer.validated_data['amount'],
            context=serializer.validated_data.get('context', ''),
            suggested_category=None,  # AI will suggest
            suggested_item=None,
            confidence=0.0,
            reasoning='AI service not yet implemented'
        )

        return api_response(
            ok=True,
            data={
                'suggested_category_id': '',
                'suggested_item_id': '',
                'confidence': 0.0,
                'reasoning': 'AI service not yet implemented'
            },
            error="AI service not implemented"
        )
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_copq_report(request):
    """Generate COPQ report"""
    serializer = COPQReportRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response(ok=False, data=None, error=str(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

    # TODO: Implement report generation
    try:
        from_date = serializer.validated_data['from_date']
        to_date = serializer.validated_data['to_date']
        group_by = serializer.validated_data.get('group_by', 'category')

        # Placeholder response
        data = {
            'total_copq': 0,
            'breakdown': [],
            'trend': []
        }
        return api_response(ok=True, data=data, error=None)
    except Exception as e:
        return api_response(ok=False, data=None, error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
