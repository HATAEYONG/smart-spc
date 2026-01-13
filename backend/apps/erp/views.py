"""
ERP Integration Views
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import (
    MasterItem,
    MasterMachine,
    MasterWorkCenter,
    MasterBOM,
    MasterRouting,
    ERPWorkOrder,
    ERPSyncLog,
)
from .serializers import (
    MasterItemSerializer,
    MasterMachineSerializer,
    MasterWorkCenterSerializer,
    MasterBOMSerializer,
    MasterRoutingSerializer,
    ERPWorkOrderSerializer,
    ERPSyncLogSerializer,
    ERPDataImportSerializer,
)
from .services import ERPDataService


class MasterItemViewSet(viewsets.ModelViewSet):
    """품목 마스터 API"""

    queryset = MasterItem.objects.filter(active_yn="Y")
    serializer_class = MasterItemSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["itm_id", "itm_nm", "itm_family"]
    ordering_fields = ["itm_id", "created_at"]


class MasterMachineViewSet(viewsets.ModelViewSet):
    """기계 마스터 API"""

    queryset = MasterMachine.objects.filter(active_yn="Y")
    serializer_class = MasterMachineSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["mc_cd", "mc_nm", "wc_cd"]
    ordering_fields = ["mc_cd", "created_at"]


class MasterWorkCenterViewSet(viewsets.ModelViewSet):
    """작업장 마스터 API"""

    queryset = MasterWorkCenter.objects.filter(active_yn="Y")
    serializer_class = MasterWorkCenterSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["wc_cd", "wc_nm"]
    ordering_fields = ["wc_cd"]


class MasterBOMViewSet(viewsets.ModelViewSet):
    """BOM API"""

    queryset = MasterBOM.objects.filter(active_yn="Y")
    serializer_class = MasterBOMSerializer

    @action(detail=False, methods=["get"])
    def by_parent(self, request):
        """모품목으로 BOM 조회"""
        parent_id = request.query_params.get("parent_id")
        if not parent_id:
            return Response(
                {"error": "parent_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        boms = self.queryset.filter(parent_item_id=parent_id)
        serializer = self.get_serializer(boms, many=True)
        return Response(serializer.data)


class MasterRoutingViewSet(viewsets.ModelViewSet):
    """라우팅 API"""

    queryset = MasterRouting.objects.filter(active_yn="Y")
    serializer_class = MasterRoutingSerializer

    @action(detail=False, methods=["get"])
    def by_item(self, request):
        """품목별 라우팅 조회"""
        item_id = request.query_params.get("item_id")
        if not item_id:
            return Response(
                {"error": "item_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        routings = self.queryset.filter(item_id=item_id).order_by("seq")
        serializer = self.get_serializer(routings, many=True)
        return Response(serializer.data)


class ERPWorkOrderViewSet(viewsets.ModelViewSet):
    """작업지시 API"""

    queryset = ERPWorkOrder.objects.all().order_by("-due_date")
    serializer_class = ERPWorkOrderSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["wo_no", "item__itm_id", "item__itm_nm"]
    ordering_fields = ["due_date", "priority", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()

        # Filter by status
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        # Filter by date range
        from_date = self.request.query_params.get("from_date")
        to_date = self.request.query_params.get("to_date")
        if from_date:
            qs = qs.filter(due_date__gte=from_date)
        if to_date:
            qs = qs.filter(due_date__lte=to_date)

        return qs


class ERPSyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ERP 동기화 로그 API"""

    queryset = ERPSyncLog.objects.all().order_by("-sync_ts")
    serializer_class = ERPSyncLogSerializer


class ERPDataImportViewSet(viewsets.ViewSet):
    """
    ERP 데이터 일괄 Import API (EMAX → APS DB 저장)

    POST /api/erp/import/items/        - 품목 마스터 일괄 저장
    POST /api/erp/import/machines/     - 기계 마스터 일괄 저장
    POST /api/erp/import/workcenters/  - 작업장 마스터 일괄 저장
    POST /api/erp/import/bom/          - BOM 일괄 저장
    POST /api/erp/import/routing/      - 라우팅 일괄 저장
    POST /api/erp/import/workorders/   - 작업지시 일괄 저장
    POST /api/erp/import/all/          - 전체 기준정보 일괄 저장
    """

    @action(detail=False, methods=["post"])
    def items(self, request):
        """
        품목 마스터 일괄 저장 (EMAX → APS DB)

        Request Body:
        {
            "items": [
                {
                    "itm_id": "EMAX-12345",
                    "itm_nm": "PCB 보드 A형",
                    "itm_type": "제품",
                    "std_ct": 30,
                    ...
                }
            ]
        }
        """
        items = request.data.get('items', [])

        if not items:
            return Response(
                {'success': False, 'message': '품목 데이터가 없습니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = ERPDataService.save_items_from_emax(items)

        return Response({
            'success': result['success'],
            'message': f"품목 마스터 {result['total']}건 처리 완료 (생성 {result['created']}건, 업데이트 {result['updated']}건, 실패 {result['failed']}건)",
            'data': result
        })

    @action(detail=False, methods=["post"])
    def machines(self, request):
        """기계 마스터 일괄 저장"""
        machines = request.data.get('machines', [])

        if not machines:
            return Response(
                {'success': False, 'message': '기계 데이터가 없습니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = ERPDataService.save_machines_from_emax(machines)

        return Response({
            'success': result['success'],
            'message': f"기계 마스터 {result['total']}건 처리 완료",
            'data': result
        })

    @action(detail=False, methods=["post"])
    def workcenters(self, request):
        """작업장 마스터 일괄 저장"""
        workcenters = request.data.get('workcenters', [])

        if not workcenters:
            return Response(
                {'success': False, 'message': '작업장 데이터가 없습니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = ERPDataService.save_workcenters_from_emax(workcenters)

        return Response({
            'success': result['success'],
            'message': f"작업장 마스터 {result['total']}건 처리 완료",
            'data': result
        })

    @action(detail=False, methods=["post"])
    def bom(self, request):
        """BOM 일괄 저장"""
        bom = request.data.get('bom', [])

        if not bom:
            return Response(
                {'success': False, 'message': 'BOM 데이터가 없습니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = ERPDataService.save_bom_from_emax(bom)

        return Response({
            'success': result['success'],
            'message': f"BOM {result['total']}건 처리 완료",
            'data': result
        })

    @action(detail=False, methods=["post"])
    def routing(self, request):
        """라우팅 일괄 저장"""
        routing = request.data.get('routing', [])

        if not routing:
            return Response(
                {'success': False, 'message': '라우팅 데이터가 없습니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = ERPDataService.save_routing_from_emax(routing)

        return Response({
            'success': result['success'],
            'message': f"라우팅 {result['total']}건 처리 완료",
            'data': result
        })

    @action(detail=False, methods=["post"])
    def workorders(self, request):
        """작업지시 일괄 저장"""
        workorders = request.data.get('workorders', [])

        if not workorders:
            return Response(
                {'success': False, 'message': '작업지시 데이터가 없습니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = ERPDataService.save_workorders_from_emax(workorders)

        return Response({
            'success': result['success'],
            'message': f"작업지시 {result['total']}건 처리 완료",
            'data': result
        })

    @action(detail=False, methods=["post"])
    def all(self, request):
        """
        전체 기준정보 일괄 저장 (EMAX → APS DB)

        Request Body:
        {
            "workcenters": [...],
            "items": [...],
            "machines": [...],
            "bom": [...],
            "routing": [...]
        }

        Response:
        {
            "success": true,
            "message": "전체 동기화 완료: 총 500건 (생성 250, 업데이트 200, 실패 50)",
            "data": {
                "total_records": 500,
                "total_created": 250,
                "total_updated": 200,
                "total_failed": 50,
                "results": {...}
            }
        }
        """
        emax_data = request.data

        if not emax_data:
            return Response(
                {'success': False, 'message': '동기화할 데이터가 없습니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = ERPDataService.sync_all_master_data(emax_data)

        message = (
            f"전체 동기화 완료: 총 {result['total_records']}건 "
            f"(생성 {result['total_created']}건, "
            f"업데이트 {result['total_updated']}건, "
            f"실패 {result['total_failed']}건)"
        )

        return Response({
            'success': result['success'],
            'message': message,
            'data': result
        })

    # ==========================================================================
    # Phase 1: 긴급 조치 - 공장 캘린더, 설비 가동시간, 재고 관리
    # ==========================================================================

    @action(detail=False, methods=["post"])
    def plant_calendars(self, request):
        """공장 캘린더 일괄 저장"""
        calendars = request.data.get('plant_calendars', [])

        if not calendars:
            return Response(
                {'success': False, 'message': '공장 캘린더 데이터가 없습니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = ERPDataService.save_plant_calendars_from_emax(calendars)

        return Response({
            'success': result['success'],
            'message': f"공장 캘린더 {result['total']}건 처리 완료 (생성 {result['created']}건, 업데이트 {result['updated']}건)",
            'data': result
        })

    @action(detail=False, methods=["post"])
    def machine_worktimes(self, request):
        """설비 가동시간 일괄 저장"""
        worktimes = request.data.get('machine_worktimes', [])

        if not worktimes:
            return Response(
                {'success': False, 'message': '설비 가동시간 데이터가 없습니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = ERPDataService.save_machine_worktimes_from_emax(worktimes)

        return Response({
            'success': result['success'],
            'message': f"설비 가동시간 {result['total']}건 처리 완료 (생성 {result['created']}건, 업데이트 {result['updated']}건)",
            'data': result
        })

    @action(detail=False, methods=["post"])
    def inventory(self, request):
        """재고 정보 일괄 저장"""
        inventory = request.data.get('inventory', [])

        if not inventory:
            return Response(
                {'success': False, 'message': '재고 데이터가 없습니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = ERPDataService.save_inventory_from_emax(inventory)

        return Response({
            'success': result['success'],
            'message': f"재고 정보 {result['total']}건 처리 완료 (생성 {result['created']}건, 업데이트 {result['updated']}건)",
            'data': result
        })

    # ==========================================================================
    # Phase 2: 단기 - 작업조, 작업자, 숙련도
    # ==========================================================================

    @action(detail=False, methods=["post"])
    def shifts(self, request):
        """작업조 마스터 일괄 저장"""
        shifts = request.data.get('shifts', [])

        if not shifts:
            return Response(
                {'success': False, 'message': '작업조 데이터가 없습니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = ERPDataService.save_shifts_from_emax(shifts)

        return Response({
            'success': result['success'],
            'message': f"작업조 {result['total']}건 처리 완료 (생성 {result['created']}건, 업데이트 {result['updated']}건)",
            'data': result
        })

    @action(detail=False, methods=["post"])
    def workers(self, request):
        """작업자 마스터 일괄 저장"""
        workers = request.data.get('workers', [])

        if not workers:
            return Response(
                {'success': False, 'message': '작업자 데이터가 없습니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = ERPDataService.save_workers_from_emax(workers)

        return Response({
            'success': result['success'],
            'message': f"작업자 {result['total']}건 처리 완료 (생성 {result['created']}건, 업데이트 {result['updated']}건)",
            'data': result
        })

    @action(detail=False, methods=["post"])
    def worker_skills(self, request):
        """작업자 숙련도 일괄 저장"""
        skills = request.data.get('worker_skills', [])

        if not skills:
            return Response(
                {'success': False, 'message': '작업자 숙련도 데이터가 없습니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = ERPDataService.save_worker_skills_from_emax(skills)

        return Response({
            'success': result['success'],
            'message': f"작업자 숙련도 {result['total']}건 처리 완료 (생성 {result['created']}건, 업데이트 {result['updated']}건)",
            'data': result
        })

    # ==========================================================================
    # 레거시 Import API (호환성 유지)
    # ==========================================================================

    @action(detail=False, methods=["post"])
    def import_data(self, request):
        """
        레거시 Import API (호환성 유지)
        새로운 코드는 위의 개별 엔드포인트 사용 권장
        """
        serializer = ERPDataImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        sync_type = serializer.validated_data["sync_type"]
        data_list = serializer.validated_data["data"]
        overwrite = serializer.validated_data["overwrite"]

        # Initialize sync log
        sync_log = ERPSyncLog.objects.create(
            sync_type=sync_type, sync_status="RUNNING", records_total=len(data_list)
        )

        success_count = 0
        failed_count = 0
        errors = []

        try:
            # Process each record
            for item_data in data_list:
                try:
                    if sync_type == "ITEM":
                        self._import_item(item_data, overwrite)
                    elif sync_type == "MACHINE":
                        self._import_machine(item_data, overwrite)
                    elif sync_type == "WORKCENTER":
                        self._import_workcenter(item_data, overwrite)
                    elif sync_type == "BOM":
                        self._import_bom(item_data, overwrite)
                    elif sync_type == "ROUTING":
                        self._import_routing(item_data, overwrite)
                    elif sync_type == "WORKORDER":
                        self._import_workorder(item_data, overwrite)
                    # Phase 1+2 types
                    elif sync_type == "PLANT_CALENDAR":
                        self._import_plant_calendar(item_data, overwrite)
                    elif sync_type == "MACHINE_WORKTIME":
                        self._import_machine_worktime(item_data, overwrite)
                    elif sync_type == "INVENTORY":
                        self._import_inventory(item_data, overwrite)
                    elif sync_type == "SHIFT":
                        self._import_shift(item_data, overwrite)
                    elif sync_type == "WORKER":
                        self._import_worker(item_data, overwrite)
                    elif sync_type == "WORKER_SKILL":
                        self._import_worker_skill(item_data, overwrite)

                    success_count += 1
                except Exception as e:
                    failed_count += 1
                    errors.append(str(e))

            # Update sync log
            sync_log.records_success = success_count
            sync_log.records_failed = failed_count
            sync_log.sync_status = "SUCCESS" if failed_count == 0 else "PARTIAL"
            if errors:
                sync_log.error_message = "\n".join(errors[:10])  # First 10 errors
            sync_log.save()

            return Response(
                {
                    "sync_id": sync_log.sync_id,
                    "status": sync_log.sync_status,
                    "total": len(data_list),
                    "success": success_count,
                    "failed": failed_count,
                }
            )

        except Exception as e:
            sync_log.sync_status = "FAILED"
            sync_log.error_message = str(e)
            sync_log.save()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _import_item(self, data, overwrite):
        """품목 마스터 Import"""
        itm_id = data.get("itm_id")
        if overwrite:
            MasterItem.objects.update_or_create(itm_id=itm_id, defaults=data)
        else:
            MasterItem.objects.get_or_create(itm_id=itm_id, defaults=data)

    def _import_machine(self, data, overwrite):
        """기계 마스터 Import"""
        mc_cd = data.get("mc_cd")
        if overwrite:
            MasterMachine.objects.update_or_create(mc_cd=mc_cd, defaults=data)
        else:
            MasterMachine.objects.get_or_create(mc_cd=mc_cd, defaults=data)

    def _import_workcenter(self, data, overwrite):
        """작업장 마스터 Import"""
        wc_cd = data.get("wc_cd")
        if overwrite:
            MasterWorkCenter.objects.update_or_create(wc_cd=wc_cd, defaults=data)
        else:
            MasterWorkCenter.objects.get_or_create(wc_cd=wc_cd, defaults=data)

    def _import_bom(self, data, overwrite):
        """BOM Import"""
        parent_id = data.pop("parent_item_id")
        child_id = data.pop("child_item_id")
        parent = MasterItem.objects.get(itm_id=parent_id)
        child = MasterItem.objects.get(itm_id=child_id)

        if overwrite:
            MasterBOM.objects.update_or_create(
                parent_item=parent, child_item=child, defaults=data
            )
        else:
            MasterBOM.objects.get_or_create(parent_item=parent, child_item=child, defaults=data)

    def _import_routing(self, data, overwrite):
        """라우팅 Import"""
        item_id = data.pop("item_id")
        wc_cd = data.pop("wc_cd")
        seq = data.get("seq")

        item = MasterItem.objects.get(itm_id=item_id)
        wc = MasterWorkCenter.objects.get(wc_cd=wc_cd)

        data["item"] = item
        data["workcenter"] = wc

        if overwrite:
            MasterRouting.objects.update_or_create(item=item, seq=seq, defaults=data)
        else:
            MasterRouting.objects.get_or_create(item=item, seq=seq, defaults=data)

    def _import_workorder(self, data, overwrite):
        """작업지시 Import"""
        wo_no = data.get("wo_no")
        item_id = data.pop("item_id")
        item = MasterItem.objects.get(itm_id=item_id)
        data["item"] = item
        data["erp_sync_ts"] = timezone.now()

        if overwrite:
            ERPWorkOrder.objects.update_or_create(wo_no=wo_no, defaults=data)
        else:
            ERPWorkOrder.objects.get_or_create(wo_no=wo_no, defaults=data)

    # ==========================================================================
    # Phase 1+2 CSV Import Methods
    # ==========================================================================

    def _import_plant_calendar(self, data, overwrite):
        """공장 캘린더 Import"""
        from datetime import datetime
        work_date = datetime.strptime(data.get("work_date"), '%Y-%m-%d').date()
        plant_cd = data.get("plant_cd", "FAC01")

        from .models import PlantCalendar
        if overwrite:
            PlantCalendar.objects.update_or_create(
                work_date=work_date,
                plant_cd=plant_cd,
                defaults=data
            )
        else:
            PlantCalendar.objects.get_or_create(
                work_date=work_date,
                plant_cd=plant_cd,
                defaults=data
            )

    def _import_machine_worktime(self, data, overwrite):
        """설비 가동시간 Import"""
        mc_cd = data.pop("mc_cd")
        day_of_week = data.get("day_of_week")

        machine = MasterMachine.objects.get(mc_cd=mc_cd)
        data["machine"] = machine

        from .models import MachineWorkTime
        if overwrite:
            MachineWorkTime.objects.update_or_create(
                machine=machine,
                day_of_week=day_of_week,
                defaults=data
            )
        else:
            MachineWorkTime.objects.get_or_create(
                machine=machine,
                day_of_week=day_of_week,
                defaults=data
            )

    def _import_inventory(self, data, overwrite):
        """품목 재고 Import"""
        itm_id = data.pop("itm_id")
        plant_cd = data.get("plant_cd", "FAC01")
        warehouse_cd = data.get("warehouse_cd", "WH01")

        item = MasterItem.objects.get(itm_id=itm_id)
        data["item"] = item

        from .models import ItemInventory
        if overwrite:
            ItemInventory.objects.update_or_create(
                item=item,
                plant_cd=plant_cd,
                warehouse_cd=warehouse_cd,
                defaults=data
            )
        else:
            ItemInventory.objects.get_or_create(
                item=item,
                plant_cd=plant_cd,
                warehouse_cd=warehouse_cd,
                defaults=data
            )

    def _import_shift(self, data, overwrite):
        """작업조 마스터 Import"""
        shift_cd = data.get("shift_cd")

        from .models import MasterShift
        if overwrite:
            MasterShift.objects.update_or_create(shift_cd=shift_cd, defaults=data)
        else:
            MasterShift.objects.get_or_create(shift_cd=shift_cd, defaults=data)

    def _import_worker(self, data, overwrite):
        """작업자 마스터 Import"""
        worker_cd = data.get("worker_cd")
        wc_cd = data.pop("wc_cd")
        shift_cd = data.pop("shift_cd", None)

        workcenter = MasterWorkCenter.objects.get(wc_cd=wc_cd)
        data["workcenter"] = workcenter

        if shift_cd:
            from .models import MasterShift
            shift = MasterShift.objects.get(shift_cd=shift_cd)
            data["shift"] = shift

        from .models import MasterWorker
        if overwrite:
            MasterWorker.objects.update_or_create(worker_cd=worker_cd, defaults=data)
        else:
            MasterWorker.objects.get_or_create(worker_cd=worker_cd, defaults=data)

    def _import_worker_skill(self, data, overwrite):
        """작업자 숙련도 Import"""
        worker_cd = data.pop("worker_cd")
        operation_nm = data.get("operation_nm")

        from .models import MasterWorker, WorkerSkill
        worker = MasterWorker.objects.get(worker_cd=worker_cd)
        data["worker"] = worker

        if overwrite:
            WorkerSkill.objects.update_or_create(
                worker=worker,
                operation_nm=operation_nm,
                defaults=data
            )
        else:
            WorkerSkill.objects.get_or_create(
                worker=worker,
                operation_nm=operation_nm,
                defaults=data
            )
