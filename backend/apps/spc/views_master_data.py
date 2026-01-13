"""
SPC Master Data Views
?�질 기본?�보 API �?"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from typing import Dict, Any

from apps.spc.models_master_data import (
    QualityItemMaster,
    QualityProcessMaster,
    QualityCharacteristicMaster,
    MeasurementInstrumentMaster,
    MeasurementSystemMaster,
    MeasurementSystemComponent,
    InspectionStandardMaster,
    QualitySyncLog
)

from apps.spc.serializers_master_data import (
    QualityItemMasterSerializer,
    QualityItemMasterListSerializer,
    QualityProcessMasterSerializer,
    QualityProcessMasterListSerializer,
    QualityCharacteristicMasterSerializer,
    QualityCharacteristicMasterListSerializer,
    MeasurementInstrumentMasterSerializer,
    MeasurementInstrumentMasterListSerializer,
    MeasurementSystemMasterSerializer,
    MeasurementSystemMasterListSerializer,
    MeasurementSystemComponentSerializer,
    InspectionStandardMasterSerializer,
    InspectionStandardMasterListSerializer,
    QualitySyncLogSerializer,
    ERPItemImportSerializer,
    MESProcessImportSerializer,
    ERPItemBatchImportSerializer,
    MESProcessBatchImportSerializer,
)


# ============================================================================
# 1. ?�질 마스??뷰셋
# ============================================================================

class QualityItemMasterViewSet(viewsets.ModelViewSet):
    """?�질 ?�목 마스??뷰셋"""

    queryset = QualityItemMaster.objects.all()
    lookup_field = 'itm_id'

    def get_serializer_class(self):
        if self.action == 'list':
            return QualityItemMasterListSerializer
        return QualityItemMasterSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        itm_type = self.request.query_params.get('itm_type')
        itm_family = self.request.query_params.get('itm_family')
        quality_grade = self.request.query_params.get('quality_grade')

        if itm_type:
            queryset = queryset.filter(itm_type=itm_type)
        if itm_family:
            queryset = queryset.filter(itm_family=itm_family)
        if quality_grade:
            queryset = queryset.filter(quality_grade=quality_grade)

        return queryset

    @action(detail=False, methods=['post'])
    def import_from_erp(self, request):
        """
        ERP?�서 ?�목 마스???�이??가?�오�?
        POST /api/spc/master-data/items/import_from_erp/
        {
            "items": [
                {
                    "itm_id": "ERP-001",
                    "itm_nm": "배터�??�",
                    "itm_type": "FINISHED_GOOD",
                    ...
                }
            ]
        }
        """
        serializer = ERPItemBatchImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid data', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        items_data = serializer.validated_data['items']
        sync_log = QualitySyncLog.objects.create(
            sync_type='ITEM',
            sync_source='ERP',
            sync_status='SUCCESS',
            records_total=len(items_data),
            sync_start_ts=timezone.now(),
        )

        result = {
            'total': len(items_data),
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': []
        }

        try:
            with transaction.atomic():
                for item_data in items_data:
                    try:
                        item, created = QualityItemMaster.objects.update_or_create(
                            itm_id=item_data['itm_id'],
                            defaults={
                                **item_data,
                                'active_yn': 'Y',
                                'erp_sync_ts': timezone.now()
                            }
                        )
                        if created:
                            result['created'] += 1
                        else:
                            result['updated'] += 1
                    except Exception as e:
                        result['failed'] += 1
                        result['errors'].append({
                            'itm_id': item_data.get('itm_id'),
                            'error': str(e)
                        })

                sync_log.records_success = result['created'] + result['updated']
                sync_log.records_failed = result['failed']
                sync_log.sync_end_ts = timezone.now()
                sync_log.sync_status = 'FAILED' if result['failed'] > 0 else 'SUCCESS'
                sync_log.sync_details = result
                sync_log.save()

        except Exception as e:
            sync_log.sync_status = 'FAILED'
            sync_log.error_message = str(e)
            sync_log.sync_end_ts = timezone.now()
            sync_log.save()
            raise

        return Response(result, status=status.HTTP_200_OK)


class QualityProcessMasterViewSet(viewsets.ModelViewSet):
    """?�질 공정 마스??뷰셋"""

    queryset = QualityProcessMaster.objects.all()
    lookup_field = 'process_cd'

    def get_serializer_class(self):
        if self.action == 'list':
            return QualityProcessMasterListSerializer
        return QualityProcessMasterSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        process_type = self.request.query_params.get('process_type')
        workcenter_cd = self.request.query_params.get('workcenter_cd')
        line_cd = self.request.query_params.get('line_cd')

        if process_type:
            queryset = queryset.filter(process_type=process_type)
        if workcenter_cd:
            queryset = queryset.filter(workcenter_cd=workcenter_cd)
        if line_cd:
            queryset = queryset.filter(line_cd=line_cd)

        return queryset

    @action(detail=False, methods=['post'])
    def import_from_mes(self, request):
        """
        MES?�서 공정 마스???�이??가?�오�?
        POST /api/spc/master-data/processes/import_from_mes/
        {
            "processes": [
                {
                    "process_cd": "MES-P001",
                    "process_nm": "코팅 공정",
                    "process_type": "PROCESS",
                    ...
                }
            ]
        }
        """
        serializer = MESProcessBatchImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid data', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        processes_data = serializer.validated_data['processes']
        sync_log = QualitySyncLog.objects.create(
            sync_type='PROCESS',
            sync_source='MES',
            sync_status='SUCCESS',
            records_total=len(processes_data),
            sync_start_ts=timezone.now(),
        )

        result = {
            'total': len(processes_data),
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': []
        }

        try:
            with transaction.atomic():
                for process_data in processes_data:
                    try:
                        process, created = QualityProcessMaster.objects.update_or_create(
                            process_cd=process_data['process_cd'],
                            defaults={
                                **process_data,
                                'active_yn': 'Y',
                                'mes_sync_ts': timezone.now()
                            }
                        )
                        if created:
                            result['created'] += 1
                        else:
                            result['updated'] += 1
                    except Exception as e:
                        result['failed'] += 1
                        result['errors'].append({
                            'process_cd': process_data.get('process_cd'),
                            'error': str(e)
                        })

                sync_log.records_success = result['created'] + result['updated']
                sync_log.records_failed = result['failed']
                sync_log.sync_end_ts = timezone.now()
                sync_log.sync_status = 'FAILED' if result['failed'] > 0 else 'SUCCESS'
                sync_log.sync_details = result
                sync_log.save()

        except Exception as e:
            sync_log.sync_status = 'FAILED'
            sync_log.error_message = str(e)
            sync_log.sync_end_ts = timezone.now()
            sync_log.save()
            raise

        return Response(result, status=status.HTTP_200_OK)


class QualityCharacteristicMasterViewSet(viewsets.ModelViewSet):
    """?�질 ?�성 마스??뷰셋"""

    queryset = QualityCharacteristicMaster.objects.select_related('item', 'process').all()
    lookup_field = 'characteristic_cd'

    def get_serializer_class(self):
        if self.action == 'list':
            return QualityCharacteristicMasterListSerializer
        return QualityCharacteristicMasterSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        item_id = self.request.query_params.get('item_id')
        process_id = self.request.query_params.get('process_id')
        characteristic_type = self.request.query_params.get('characteristic_type')

        if item_id:
            queryset = queryset.filter(item__itm_id=item_id)
        if process_id:
            queryset = queryset.filter(process__process_cd=process_id)
        if characteristic_type:
            queryset = queryset.filter(characteristic_type=characteristic_type)

        return queryset


# ============================================================================
# 2. 측정 ?�스??뷰셋
# ============================================================================

class MeasurementInstrumentMasterViewSet(viewsets.ModelViewSet):
    """측정기구 마스??뷰셋"""

    queryset = MeasurementInstrumentMaster.objects.all()
    lookup_field = 'instrument_cd'

    def get_serializer_class(self):
        if self.action == 'list':
            return MeasurementInstrumentMasterListSerializer
        return MeasurementInstrumentMasterSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        instrument_type = self.request.query_params.get('instrument_type')
        status_filter = self.request.query_params.get('status')

        if instrument_type:
            queryset = queryset.filter(instrument_type=instrument_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    @action(detail=False, methods=['get'])
    def calibration_due(self, request):
        """
        보정 만료 기구 목록 조회

        GET /api/spc/master-data/instruments/calibration_due/
        """
        from django.utils import timezone

        queryset = self.queryset.filter(
            next_calibration_date__lte=timezone.now().date()
        )
        serializer = MeasurementInstrumentMasterListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def gage_rr_due(self, request):
        """
        Gage R&R ?�시 ?�요 기구 목록 조회

        GET /api/spc/master-data/instruments/gage_rr_due/
        """
        queryset = self.queryset.filter(
            gage_rr_required=True
        ).filter(
            status__in=['ACTIVE', 'CALIBRATION_DUE']
        )
        serializer = MeasurementInstrumentMasterListSerializer(queryset, many=True)
        return Response(serializer.data)


class MeasurementSystemMasterViewSet(viewsets.ModelViewSet):
    """측정 ?�스??마스??뷰셋"""

    queryset = MeasurementSystemMaster.objects.prefetch_related('instruments').all()
    lookup_field = 'system_cd'

    def get_serializer_class(self):
        if self.action == 'list':
            return MeasurementSystemMasterListSerializer
        return MeasurementSystemMasterSerializer

    @action(detail=True, methods=['post'])
    def add_instrument(self, request, system_cd=None):
        """
        ?�스?�에 기구 추�?

        POST /api/spc/master-data/systems/{system_cd}/add_instrument/
        {
            "instrument_cd": "INST-001",
            "component_role": "주측?�기",
            "seq": 1
        }
        """
        system = self.get_object()
        instrument_cd = request.data.get('instrument_cd')
        component_role = request.data.get('component_role')
        seq = request.data.get('seq', 1)

        try:
            instrument = MeasurementInstrumentMaster.objects.get(instrument_cd=instrument_cd)
            component, created = MeasurementSystemComponent.objects.update_or_create(
                system=system,
                instrument=instrument,
                defaults={
                    'component_role': component_role,
                    'seq': seq
                }
            )
            serializer = MeasurementSystemComponentSerializer(component)
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        except MeasurementInstrumentMaster.DoesNotExist:
            return Response(
                {'error': f'Instrument {instrument_cd} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['delete'])
    def remove_instrument(self, request, system_cd=None):
        """
        ?�스?�에??기구 ?�거

        DELETE /api/spc/master-data/systems/{system_cd}/remove_instrument/?instrument_cd=INST-001
        """
        system = self.get_object()
        instrument_cd = request.query_params.get('instrument_cd')

        try:
            component = MeasurementSystemComponent.objects.get(
                system=system,
                instrument__instrument_cd=instrument_cd
            )
            component.delete()
            return Response(
                {'message': f'Instrument {instrument_cd} removed from system'},
                status=status.HTTP_204_NO_CONTENT
            )
        except MeasurementSystemComponent.DoesNotExist:
            return Response(
                {'error': f'Component not found'},
                status=status.HTTP_404_NOT_FOUND
            )


# ============================================================================
# 3. 검??기�? 뷰셋
# ============================================================================

class InspectionStandardMasterViewSet(viewsets.ModelViewSet):
    """검??기�? 마스??뷰셋"""

    queryset = InspectionStandardMaster.objects.select_related('item', 'characteristic').all()
    lookup_field = 'standard_cd'

    def get_serializer_class(self):
        if self.action == 'list':
            return InspectionStandardMasterListSerializer
        return InspectionStandardMasterSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        item_id = self.request.query_params.get('item_id')
        characteristic_id = self.request.query_params.get('characteristic_id')
        standard_type = self.request.query_params.get('standard_type')

        if item_id:
            queryset = queryset.filter(item__itm_id=item_id)
        if characteristic_id:
            queryset = queryset.filter(characteristic__characteristic_cd=characteristic_id)
        if standard_type:
            queryset = queryset.filter(standard_type=standard_type)

        return queryset


# ============================================================================
# 4. ?�기??로그 뷰셋
# ============================================================================

class QualitySyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """?�질 ?�이???�기??로그 뷰셋 (?�기 ?�용)"""

    queryset = QualitySyncLog.objects.all()
    serializer_class = QualitySyncLogSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        sync_type = self.request.query_params.get('sync_type')
        sync_source = self.request.query_params.get('sync_source')
        sync_status = self.request.query_params.get('sync_status')

        if sync_type:
            queryset = queryset.filter(sync_type=sync_type)
        if sync_source:
            queryset = queryset.filter(sync_source=sync_source)
        if sync_status:
            queryset = queryset.filter(sync_status=sync_status)

        return queryset

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        ?�기???�계 조회

        GET /api/spc/master-data/sync-logs/statistics/
        """
        from django.db.models import Count, Sum

        stats = {
            'total_syncs': self.queryset.count(),
            'by_type': dict(
                self.queryset.values('sync_type').annotate(count=Count('sync_id')).values_list('sync_type', 'count')
            ),
            'by_source': dict(
                self.queryset.values('sync_source').annotate(count=Count('sync_id')).values_list('sync_source', 'count')
            ),
            'by_status': dict(
                self.queryset.values('sync_status').annotate(count=Count('sync_id')).values_list('sync_status', 'count')
            ),
            'total_records': self.queryset.aggregate(Sum('records_total'))['records_total__sum'] or 0,
            'total_success': self.queryset.aggregate(Sum('records_success'))['records_success__sum'] or 0,
            'total_failed': self.queryset.aggregate(Sum('records_failed'))['records_failed__sum'] or 0,
        }

        return Response(stats)
