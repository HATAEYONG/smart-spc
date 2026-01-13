"""
ERP 연계 서비스
EMAX ERP → APS DB 데이터 저장
"""
from typing import List, Dict, Any
from django.db import transaction
from django.utils import timezone
from .models import (
    MasterItem,
    MasterMachine,
    MasterWorkCenter,
    MasterBOM,
    MasterRouting,
    ERPWorkOrder,
    ERPSyncLog,
    # Phase 1: 긴급
    PlantCalendar,
    MachineWorkTime,
    MachineDowntime,
    ItemInventory,
    InventoryTransaction,
    MaterialRequirement,
    # Phase 2: 단기
    MasterShift,
    MasterWorker,
    WorkerSkill,
    WorkAssignment,
)


class ERPDataService:
    """ERP 데이터 수집 및 APS DB 저장 서비스"""

    # ==========================================================================
    # 1단계: 수집 (Collection) → 2단계: 적재 (Loading)
    # ==========================================================================

    @staticmethod
    @transaction.atomic
    def save_items_from_emax(emax_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        품목 마스터 저장 (EMAX → APS DB)

        Args:
            emax_items: EMAX 품목 데이터 리스트
            [
                {
                    'itm_id': 'EMAX-12345',
                    'itm_nm': 'PCB 보드',
                    'itm_type': '제품',
                    'std_ct': 30,
                    ...
                }
            ]

        Returns:
            {
                'success': True,
                'total': 100,
                'created': 50,
                'updated': 50,
                'failed': 0,
                'errors': []
            }
        """
        result = {
            'success': True,
            'total': len(emax_items),
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': [],
        }

        sync_log = ERPSyncLog.objects.create(
            sync_type='ITEM',
            sync_status='SUCCESS',
            records_total=len(emax_items),
        )

        try:
            for item_data in emax_items:
                try:
                    # APS 형식으로 변환
                    aps_data = {
                        'itm_id': item_data.get('itm_id'),
                        'itm_nm': item_data.get('itm_nm'),
                        'itm_type': item_data.get('itm_type', '제품'),
                        'itm_family': item_data.get('itm_family'),
                        'std_cycle_time': item_data.get('std_ct', 60),
                        'unit': item_data.get('unit', 'EA'),
                        'active_yn': 'Y',
                    }

                    # Upsert (생성 또는 업데이트)
                    item, created = MasterItem.objects.update_or_create(
                        itm_id=aps_data['itm_id'],
                        defaults=aps_data
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

            # 동기화 로그 업데이트
            sync_log.records_success = result['created'] + result['updated']
            sync_log.records_failed = result['failed']

            if result['failed'] > 0:
                sync_log.sync_status = 'PARTIAL'
                sync_log.error_message = f"{result['failed']}건 실패: {result['errors'][:3]}"
                result['success'] = False

            sync_log.save()

        except Exception as e:
            sync_log.sync_status = 'FAILED'
            sync_log.error_message = str(e)
            sync_log.save()
            result['success'] = False
            result['errors'].append({'error': str(e)})

        return result

    @staticmethod
    @transaction.atomic
    def save_machines_from_emax(emax_machines: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        기계 마스터 저장 (EMAX → APS DB)

        Args:
            emax_machines: EMAX 기계 데이터 리스트
        """
        result = {
            'success': True,
            'total': len(emax_machines),
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': [],
        }

        sync_log = ERPSyncLog.objects.create(
            sync_type='MACHINE',
            sync_status='SUCCESS',
            records_total=len(emax_machines),
        )

        try:
            for machine_data in emax_machines:
                try:
                    aps_data = {
                        'mc_cd': machine_data.get('mc_cd'),
                        'mc_nm': machine_data.get('mc_nm'),
                        'wc_cd': machine_data.get('wc_cd'),
                        'mc_type': machine_data.get('mc_type', '일반'),
                        'capacity': machine_data.get('capacity', 1),
                        'cost_per_hour': machine_data.get('cost_per_hour', 100.0),
                        'active_yn': 'Y',
                    }

                    machine, created = MasterMachine.objects.update_or_create(
                        mc_cd=aps_data['mc_cd'],
                        defaults=aps_data
                    )

                    if created:
                        result['created'] += 1
                    else:
                        result['updated'] += 1

                except Exception as e:
                    result['failed'] += 1
                    result['errors'].append({
                        'mc_cd': machine_data.get('mc_cd'),
                        'error': str(e)
                    })

            sync_log.records_success = result['created'] + result['updated']
            sync_log.records_failed = result['failed']

            if result['failed'] > 0:
                sync_log.sync_status = 'PARTIAL'
                sync_log.error_message = f"{result['failed']}건 실패"
                result['success'] = False

            sync_log.save()

        except Exception as e:
            sync_log.sync_status = 'FAILED'
            sync_log.error_message = str(e)
            sync_log.save()
            result['success'] = False

        return result

    @staticmethod
    @transaction.atomic
    def save_workcenters_from_emax(emax_wcs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        작업장 마스터 저장 (EMAX → APS DB)

        Args:
            emax_wcs: EMAX 작업장 데이터 리스트
        """
        result = {
            'success': True,
            'total': len(emax_wcs),
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': [],
        }

        sync_log = ERPSyncLog.objects.create(
            sync_type='WORKCENTER',
            sync_status='SUCCESS',
            records_total=len(emax_wcs),
        )

        try:
            for wc_data in emax_wcs:
                try:
                    aps_data = {
                        'wc_cd': wc_data.get('wc_cd'),
                        'wc_nm': wc_data.get('wc_nm'),
                        'plant_cd': wc_data.get('fac_cd', 'FAC01'),
                        'active_yn': 'Y',
                    }

                    wc, created = MasterWorkCenter.objects.update_or_create(
                        wc_cd=aps_data['wc_cd'],
                        defaults=aps_data
                    )

                    if created:
                        result['created'] += 1
                    else:
                        result['updated'] += 1

                except Exception as e:
                    result['failed'] += 1
                    result['errors'].append({
                        'wc_cd': wc_data.get('wc_cd'),
                        'error': str(e)
                    })

            sync_log.records_success = result['created'] + result['updated']
            sync_log.records_failed = result['failed']

            if result['failed'] > 0:
                sync_log.sync_status = 'PARTIAL'
                result['success'] = False

            sync_log.save()

        except Exception as e:
            sync_log.sync_status = 'FAILED'
            sync_log.error_message = str(e)
            sync_log.save()
            result['success'] = False

        return result

    @staticmethod
    @transaction.atomic
    def save_bom_from_emax(emax_bom: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        BOM 저장 (EMAX → APS DB)

        Args:
            emax_bom: EMAX BOM 데이터 리스트
            [
                {
                    'parent_itm_id': 'EMAX-12345',
                    'child_itm_id': 'EMAX-67890',
                    'quantity': 2.5,
                    'seq': 1
                }
            ]
        """
        result = {
            'success': True,
            'total': len(emax_bom),
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': [],
        }

        sync_log = ERPSyncLog.objects.create(
            sync_type='BOM',
            sync_status='SUCCESS',
            records_total=len(emax_bom),
        )

        try:
            for bom_data in emax_bom:
                try:
                    parent_id = bom_data.get('parent_itm_id')
                    child_id = bom_data.get('child_itm_id')

                    # 품목 존재 확인
                    if not MasterItem.objects.filter(itm_id=parent_id).exists():
                        result['failed'] += 1
                        result['errors'].append({
                            'parent_itm_id': parent_id,
                            'error': '모품목이 존재하지 않습니다'
                        })
                        continue

                    if not MasterItem.objects.filter(itm_id=child_id).exists():
                        result['failed'] += 1
                        result['errors'].append({
                            'child_itm_id': child_id,
                            'error': '자품목이 존재하지 않습니다'
                        })
                        continue

                    parent_item = MasterItem.objects.get(itm_id=parent_id)
                    child_item = MasterItem.objects.get(itm_id=child_id)

                    aps_data = {
                        'quantity': bom_data.get('quantity', 1.0),
                        'seq': bom_data.get('seq', 1),
                        'active_yn': 'Y',
                    }

                    bom, created = MasterBOM.objects.update_or_create(
                        parent_item=parent_item,
                        child_item=child_item,
                        defaults=aps_data
                    )

                    if created:
                        result['created'] += 1
                    else:
                        result['updated'] += 1

                except Exception as e:
                    result['failed'] += 1
                    result['errors'].append({
                        'bom': f"{bom_data.get('parent_itm_id')} > {bom_data.get('child_itm_id')}",
                        'error': str(e)
                    })

            sync_log.records_success = result['created'] + result['updated']
            sync_log.records_failed = result['failed']

            if result['failed'] > 0:
                sync_log.sync_status = 'PARTIAL'
                result['success'] = False

            sync_log.save()

        except Exception as e:
            sync_log.sync_status = 'FAILED'
            sync_log.error_message = str(e)
            sync_log.save()
            result['success'] = False

        return result

    @staticmethod
    @transaction.atomic
    def save_routing_from_emax(emax_routing: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        라우팅 저장 (EMAX → APS DB)

        Args:
            emax_routing: EMAX 라우팅 데이터 리스트
            [
                {
                    'itm_id': 'EMAX-12345',
                    'seq': 1,
                    'wc_cd': 'WC01',
                    'operation_nm': '인쇄',
                    'std_time': 30,
                    'setup_time': 10
                }
            ]
        """
        result = {
            'success': True,
            'total': len(emax_routing),
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': [],
        }

        sync_log = ERPSyncLog.objects.create(
            sync_type='ROUTING',
            sync_status='SUCCESS',
            records_total=len(emax_routing),
        )

        try:
            for routing_data in emax_routing:
                try:
                    itm_id = routing_data.get('itm_id')
                    wc_cd = routing_data.get('wc_cd')

                    # 품목/작업장 존재 확인
                    if not MasterItem.objects.filter(itm_id=itm_id).exists():
                        result['failed'] += 1
                        result['errors'].append({
                            'itm_id': itm_id,
                            'error': '품목이 존재하지 않습니다'
                        })
                        continue

                    if not MasterWorkCenter.objects.filter(wc_cd=wc_cd).exists():
                        result['failed'] += 1
                        result['errors'].append({
                            'wc_cd': wc_cd,
                            'error': '작업장이 존재하지 않습니다'
                        })
                        continue

                    item = MasterItem.objects.get(itm_id=itm_id)
                    workcenter = MasterWorkCenter.objects.get(wc_cd=wc_cd)

                    aps_data = {
                        'workcenter': workcenter,
                        'operation_nm': routing_data.get('operation_nm', '공정'),
                        'std_time': routing_data.get('std_time', 60),
                        'setup_time': routing_data.get('setup_time', 0),
                        'active_yn': 'Y',
                    }

                    routing, created = MasterRouting.objects.update_or_create(
                        item=item,
                        seq=routing_data.get('seq', 1),
                        defaults=aps_data
                    )

                    if created:
                        result['created'] += 1
                    else:
                        result['updated'] += 1

                except Exception as e:
                    result['failed'] += 1
                    result['errors'].append({
                        'routing': f"{routing_data.get('itm_id')}-{routing_data.get('seq')}",
                        'error': str(e)
                    })

            sync_log.records_success = result['created'] + result['updated']
            sync_log.records_failed = result['failed']

            if result['failed'] > 0:
                sync_log.sync_status = 'PARTIAL'
                result['success'] = False

            sync_log.save()

        except Exception as e:
            sync_log.sync_status = 'FAILED'
            sync_log.error_message = str(e)
            sync_log.save()
            result['success'] = False

        return result

    @staticmethod
    @transaction.atomic
    def save_workorders_from_emax(emax_wos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        작업지시 저장 (EMAX → APS DB)

        Args:
            emax_wos: EMAX 작업지시 데이터 리스트
            [
                {
                    'wo_no': 'WO-2026-001',
                    'itm_id': 'EMAX-12345',
                    'order_qty': 500,
                    'due_date': '2026-01-15T23:59:59',
                    'priority': 1
                }
            ]
        """
        result = {
            'success': True,
            'total': len(emax_wos),
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': [],
        }

        sync_log = ERPSyncLog.objects.create(
            sync_type='WORKORDER',
            sync_status='SUCCESS',
            records_total=len(emax_wos),
        )

        try:
            for wo_data in emax_wos:
                try:
                    itm_id = wo_data.get('itm_id')

                    # 품목 존재 확인
                    if not MasterItem.objects.filter(itm_id=itm_id).exists():
                        result['failed'] += 1
                        result['errors'].append({
                            'wo_no': wo_data.get('wo_no'),
                            'error': f'품목 {itm_id}이 존재하지 않습니다'
                        })
                        continue

                    item = MasterItem.objects.get(itm_id=itm_id)

                    aps_data = {
                        'item': item,
                        'order_qty': wo_data.get('order_qty', 1),
                        'due_date': wo_data.get('due_date'),
                        'priority': wo_data.get('priority', 5),
                        'status': wo_data.get('status', 'CREATED'),
                        'plant_cd': wo_data.get('plant_cd', 'FAC01'),
                        'erp_sync_ts': timezone.now(),
                    }

                    wo, created = ERPWorkOrder.objects.update_or_create(
                        wo_no=wo_data.get('wo_no'),
                        defaults=aps_data
                    )

                    if created:
                        result['created'] += 1
                    else:
                        result['updated'] += 1

                except Exception as e:
                    result['failed'] += 1
                    result['errors'].append({
                        'wo_no': wo_data.get('wo_no'),
                        'error': str(e)
                    })

            sync_log.records_success = result['created'] + result['updated']
            sync_log.records_failed = result['failed']

            if result['failed'] > 0:
                sync_log.sync_status = 'PARTIAL'
                result['success'] = False

            sync_log.save()

        except Exception as e:
            sync_log.sync_status = 'FAILED'
            sync_log.error_message = str(e)
            sync_log.save()
            result['success'] = False

        return result

    # ==========================================================================
    # Phase 1: 긴급 조치 - 공장 캘린더, 설비 가동시간, 재고 관리
    # ==========================================================================

    @staticmethod
    @transaction.atomic
    def save_plant_calendars_from_emax(emax_calendars: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        공장 캘린더 저장 (EMAX → APS DB)

        Args:
            emax_calendars: [
                {
                    'work_date': '2026-01-03',
                    'plant_cd': 'FAC01',
                    'day_type': 'WORK',
                    'work_start_time': '08:00',
                    'work_end_time': '17:00',
                    'is_available': True
                }
            ]
        """
        result = {'success': True, 'total': len(emax_calendars), 'created': 0, 'updated': 0, 'failed': 0, 'errors': []}

        try:
            for cal_data in emax_calendars:
                try:
                    from datetime import datetime

                    aps_data = {
                        'plant_cd': cal_data.get('plant_cd', 'FAC01'),
                        'day_type': cal_data.get('day_type', 'WORK'),
                        'work_start_time': cal_data.get('work_start_time', '08:00:00'),
                        'work_end_time': cal_data.get('work_end_time', '17:00:00'),
                        'break_start_time': cal_data.get('break_start_time'),
                        'break_end_time': cal_data.get('break_end_time'),
                        'is_available': cal_data.get('is_available', True),
                        'capacity_rate': cal_data.get('capacity_rate', 100.00),
                        'remarks': cal_data.get('remarks'),
                    }

                    work_date = datetime.strptime(cal_data.get('work_date'), '%Y-%m-%d').date()

                    calendar, created = PlantCalendar.objects.update_or_create(
                        work_date=work_date,
                        plant_cd=aps_data['plant_cd'],
                        defaults=aps_data
                    )

                    if created:
                        result['created'] += 1
                    else:
                        result['updated'] += 1

                except Exception as e:
                    result['failed'] += 1
                    result['errors'].append({'work_date': cal_data.get('work_date'), 'error': str(e)})

        except Exception as e:
            result['success'] = False

        return result

    @staticmethod
    @transaction.atomic
    def save_machine_worktimes_from_emax(emax_worktimes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        설비 가동시간 저장 (EMAX → APS DB)

        Args:
            emax_worktimes: [
                {
                    'mc_cd': 'MC-001',
                    'day_of_week': 0,  # 월요일
                    'start_time': '08:00',
                    'end_time': '17:00',
                    'is_available': True
                }
            ]
        """
        result = {'success': True, 'total': len(emax_worktimes), 'created': 0, 'updated': 0, 'failed': 0, 'errors': []}

        try:
            for wt_data in emax_worktimes:
                try:
                    mc_cd = wt_data.get('mc_cd')

                    if not MasterMachine.objects.filter(mc_cd=mc_cd).exists():
                        result['failed'] += 1
                        result['errors'].append({'mc_cd': mc_cd, 'error': '기계가 존재하지 않습니다'})
                        continue

                    machine = MasterMachine.objects.get(mc_cd=mc_cd)

                    aps_data = {
                        'machine': machine,
                        'start_time': wt_data.get('start_time', '08:00:00'),
                        'end_time': wt_data.get('end_time', '17:00:00'),
                        'is_available': wt_data.get('is_available', True),
                        'is_overnight': wt_data.get('is_overnight', False),
                        'remarks': wt_data.get('remarks'),
                    }

                    work_time, created = MachineWorkTime.objects.update_or_create(
                        machine=machine,
                        day_of_week=wt_data.get('day_of_week'),
                        defaults=aps_data
                    )

                    if created:
                        result['created'] += 1
                    else:
                        result['updated'] += 1

                except Exception as e:
                    result['failed'] += 1
                    result['errors'].append({'mc_cd': wt_data.get('mc_cd'), 'error': str(e)})

        except Exception as e:
            result['success'] = False

        return result

    @staticmethod
    @transaction.atomic
    def save_inventory_from_emax(emax_inventory: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        재고 정보 저장 (EMAX → APS DB)

        Args:
            emax_inventory: [
                {
                    'itm_id': 'PCB-A001',
                    'plant_cd': 'FAC01',
                    'warehouse_cd': 'WH01',
                    'on_hand_qty': 500,
                    'safety_stock': 100
                }
            ]
        """
        result = {'success': True, 'total': len(emax_inventory), 'created': 0, 'updated': 0, 'failed': 0, 'errors': []}

        try:
            for inv_data in emax_inventory:
                try:
                    from decimal import Decimal

                    itm_id = inv_data.get('itm_id')

                    if not MasterItem.objects.filter(itm_id=itm_id).exists():
                        result['failed'] += 1
                        result['errors'].append({'itm_id': itm_id, 'error': '품목이 존재하지 않습니다'})
                        continue

                    item = MasterItem.objects.get(itm_id=itm_id)

                    aps_data = {
                        'item': item,
                        'plant_cd': inv_data.get('plant_cd', 'FAC01'),
                        'warehouse_cd': inv_data.get('warehouse_cd', 'WH01'),
                        'on_hand_qty': Decimal(str(inv_data.get('on_hand_qty', 0))),
                        'allocated_qty': Decimal(str(inv_data.get('allocated_qty', 0))),
                        'safety_stock': Decimal(str(inv_data.get('safety_stock', 0))),
                        'min_stock': Decimal(str(inv_data.get('min_stock', 0))),
                        'max_stock': Decimal(str(inv_data.get('max_stock', 0))),
                        'reorder_point': Decimal(str(inv_data.get('reorder_point', 0))),
                        'order_qty': Decimal(str(inv_data.get('order_qty', 0))),
                        'unit_cost': Decimal(str(inv_data.get('unit_cost', 0))),
                    }

                    inventory, created = ItemInventory.objects.update_or_create(
                        item=item,
                        plant_cd=aps_data['plant_cd'],
                        warehouse_cd=aps_data['warehouse_cd'],
                        defaults=aps_data
                    )

                    if created:
                        result['created'] += 1
                    else:
                        result['updated'] += 1

                except Exception as e:
                    result['failed'] += 1
                    result['errors'].append({'itm_id': inv_data.get('itm_id'), 'error': str(e)})

        except Exception as e:
            result['success'] = False

        return result

    # ==========================================================================
    # Phase 2: 단기 - 작업조, 작업자, 숙련도
    # ==========================================================================

    @staticmethod
    @transaction.atomic
    def save_shifts_from_emax(emax_shifts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        작업조 마스터 저장 (EMAX → APS DB)

        Args:
            emax_shifts: [
                {
                    'shift_cd': 'DAY-A',
                    'shift_nm': '주간A조',
                    'shift_type': 'DAY',
                    'start_time': '08:00',
                    'end_time': '17:00',
                    'break_time': 60
                }
            ]
        """
        result = {'success': True, 'total': len(emax_shifts), 'created': 0, 'updated': 0, 'failed': 0, 'errors': []}

        try:
            for shift_data in emax_shifts:
                try:
                    aps_data = {
                        'shift_nm': shift_data.get('shift_nm'),
                        'shift_type': shift_data.get('shift_type', 'DAY'),
                        'start_time': shift_data.get('start_time', '08:00:00'),
                        'end_time': shift_data.get('end_time', '17:00:00'),
                        'break_time': shift_data.get('break_time', 60),
                        'is_overnight': shift_data.get('is_overnight', False),
                        'active_yn': 'Y',
                    }

                    shift, created = MasterShift.objects.update_or_create(
                        shift_cd=shift_data.get('shift_cd'),
                        defaults=aps_data
                    )

                    if created:
                        result['created'] += 1
                    else:
                        result['updated'] += 1

                except Exception as e:
                    result['failed'] += 1
                    result['errors'].append({'shift_cd': shift_data.get('shift_cd'), 'error': str(e)})

        except Exception as e:
            result['success'] = False

        return result

    @staticmethod
    @transaction.atomic
    def save_workers_from_emax(emax_workers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        작업자 마스터 저장 (EMAX → APS DB)

        Args:
            emax_workers: [
                {
                    'worker_cd': 'W001',
                    'worker_nm': '홍길동',
                    'wc_cd': 'WC-SMT',
                    'shift_cd': 'DAY-A',
                    'cost_per_hour': 25000
                }
            ]
        """
        result = {'success': True, 'total': len(emax_workers), 'created': 0, 'updated': 0, 'failed': 0, 'errors': []}

        try:
            for worker_data in emax_workers:
                try:
                    from decimal import Decimal
                    from datetime import datetime

                    wc_cd = worker_data.get('wc_cd')

                    if not MasterWorkCenter.objects.filter(wc_cd=wc_cd).exists():
                        result['failed'] += 1
                        result['errors'].append({'worker_cd': worker_data.get('worker_cd'), 'error': f'작업장 {wc_cd}이 존재하지 않습니다'})
                        continue

                    workcenter = MasterWorkCenter.objects.get(wc_cd=wc_cd)

                    # 작업조는 선택적
                    shift = None
                    if worker_data.get('shift_cd'):
                        if MasterShift.objects.filter(shift_cd=worker_data.get('shift_cd')).exists():
                            shift = MasterShift.objects.get(shift_cd=worker_data.get('shift_cd'))

                    aps_data = {
                        'worker_nm': worker_data.get('worker_nm'),
                        'workcenter': workcenter,
                        'shift': shift,
                        'worker_type': worker_data.get('worker_type', 'REGULAR'),
                        'hire_date': datetime.strptime(worker_data.get('hire_date'), '%Y-%m-%d').date() if worker_data.get('hire_date') else None,
                        'experience_years': worker_data.get('experience_years', 0),
                        'cost_per_hour': Decimal(str(worker_data.get('cost_per_hour', 20000))),
                        'phone': worker_data.get('phone'),
                        'email': worker_data.get('email'),
                        'active_yn': 'Y',
                    }

                    worker, created = MasterWorker.objects.update_or_create(
                        worker_cd=worker_data.get('worker_cd'),
                        defaults=aps_data
                    )

                    if created:
                        result['created'] += 1
                    else:
                        result['updated'] += 1

                except Exception as e:
                    result['failed'] += 1
                    result['errors'].append({'worker_cd': worker_data.get('worker_cd'), 'error': str(e)})

        except Exception as e:
            result['success'] = False

        return result

    @staticmethod
    @transaction.atomic
    def save_worker_skills_from_emax(emax_skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        작업자 숙련도 저장 (EMAX → APS DB)

        Args:
            emax_skills: [
                {
                    'worker_cd': 'W001',
                    'operation_nm': '인쇄',
                    'skill_level': 5,
                    'efficiency_rate': 130,
                    'certified_yn': 'Y'
                }
            ]
        """
        result = {'success': True, 'total': len(emax_skills), 'created': 0, 'updated': 0, 'failed': 0, 'errors': []}

        try:
            for skill_data in emax_skills:
                try:
                    from decimal import Decimal
                    from datetime import datetime

                    worker_cd = skill_data.get('worker_cd')

                    if not MasterWorker.objects.filter(worker_cd=worker_cd).exists():
                        result['failed'] += 1
                        result['errors'].append({'worker_cd': worker_cd, 'error': '작업자가 존재하지 않습니다'})
                        continue

                    worker = MasterWorker.objects.get(worker_cd=worker_cd)

                    aps_data = {
                        'worker': worker,
                        'skill_level': skill_data.get('skill_level', 3),
                        'efficiency_rate': Decimal(str(skill_data.get('efficiency_rate', 100))),
                        'certified_yn': skill_data.get('certified_yn', 'N'),
                        'certification_nm': skill_data.get('certification_nm'),
                        'certification_date': datetime.strptime(skill_data.get('certification_date'), '%Y-%m-%d').date() if skill_data.get('certification_date') else None,
                        'training_hours': skill_data.get('training_hours', 0),
                        'last_training_date': datetime.strptime(skill_data.get('last_training_date'), '%Y-%m-%d').date() if skill_data.get('last_training_date') else None,
                        'active_yn': 'Y',
                    }

                    skill, created = WorkerSkill.objects.update_or_create(
                        worker=worker,
                        operation_nm=skill_data.get('operation_nm'),
                        defaults=aps_data
                    )

                    if created:
                        result['created'] += 1
                    else:
                        result['updated'] += 1

                except Exception as e:
                    result['failed'] += 1
                    result['errors'].append({
                        'worker_cd': skill_data.get('worker_cd'),
                        'operation_nm': skill_data.get('operation_nm'),
                        'error': str(e)
                    })

        except Exception as e:
            result['success'] = False

        return result

    # ==========================================================================
    # 통합 동기화 메서드
    # ==========================================================================

    @classmethod
    def sync_all_master_data(cls, emax_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        전체 기준정보 동기화 (EMAX → APS DB)

        Args:
            emax_data: {
                'items': [...],
                'machines': [...],
                'workcenters': [...],
                'bom': [...],
                'routing': [...]
            }

        Returns:
            {
                'success': True,
                'results': {
                    'items': {...},
                    'machines': {...},
                    ...
                },
                'total_records': 500,
                'total_created': 250,
                'total_updated': 200,
                'total_failed': 50
            }
        """
        results = {}

        # 순서 중요: 참조 무결성 유지
        # 1. 작업장 먼저
        if 'workcenters' in emax_data:
            results['workcenters'] = cls.save_workcenters_from_emax(emax_data['workcenters'])

        # 2. 품목
        if 'items' in emax_data:
            results['items'] = cls.save_items_from_emax(emax_data['items'])

        # 3. 기계
        if 'machines' in emax_data:
            results['machines'] = cls.save_machines_from_emax(emax_data['machines'])

        # 4. BOM (품목 참조)
        if 'bom' in emax_data:
            results['bom'] = cls.save_bom_from_emax(emax_data['bom'])

        # 5. Routing (품목, 작업장 참조)
        if 'routing' in emax_data:
            results['routing'] = cls.save_routing_from_emax(emax_data['routing'])

        # 전체 집계
        total_records = sum(r.get('total', 0) for r in results.values())
        total_created = sum(r.get('created', 0) for r in results.values())
        total_updated = sum(r.get('updated', 0) for r in results.values())
        total_failed = sum(r.get('failed', 0) for r in results.values())

        return {
            'success': all(r.get('success', False) for r in results.values()),
            'results': results,
            'total_records': total_records,
            'total_created': total_created,
            'total_updated': total_updated,
            'total_failed': total_failed,
        }
