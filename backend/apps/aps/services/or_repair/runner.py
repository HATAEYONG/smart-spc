"""
Repair Runner

CP-SAT repair를 먼저 시도하고, 실패 시 기존 시간 이동 방식으로 fallback
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from .cpsat_repair import cpsat_repair, RepairInfeasible
from .constants import MAX_TASKS_FOR_CPSAT, DEBUG_REPAIR

logger = logging.getLogger(__name__)


def repair_schedule_with_cpsat(
    scenario_id: int,
    schedule_rows: List[Dict[str, Any]],
    use_cpsat: bool = True,
    use_plant_calendar: bool = True,
    plant_cd: str = None,
    use_machine_constraints: bool = True,
    predictions=None,
    risk_weight: float = 3.0
) -> List[Dict[str, Any]]:
    """
    스케줄 Repair 메인 함수

    Args:
        scenario_id: 시나리오 ID
        schedule_rows: 스케줄 행 리스트
        use_cpsat: CP-SAT 사용 여부
        use_plant_calendar: PlantCalendar 사용 여부
        plant_cd: 공장 코드 (PlantCalendar 조회용, optional)
        use_machine_constraints: MachineWorkTime/Downtime 사용 여부 (Phase 3, default: True)
        predictions: DOWN_RISK Prediction QuerySet (STEP 2 추가)
        risk_weight: DOWN_RISK penalty 가중치 (기본 3.0)

    Returns:
        Repaired schedule_rows
    """
    if not schedule_rows:
        logger.warning("Empty schedule_rows, nothing to repair")
        return schedule_rows

    logger.info(
        f"Starting repair for scenario {scenario_id} with {len(schedule_rows)} tasks "
        f"(use_cpsat={use_cpsat}, use_plant_calendar={use_plant_calendar}, "
        f"use_machine_constraints={use_machine_constraints}, "
        f"use_down_risk={predictions is not None})"
    )

    # Step 1: CP-SAT repair 시도
    if use_cpsat:
        try:
            if len(schedule_rows) > MAX_TASKS_FOR_CPSAT:
                logger.warning(
                    f"Too many tasks ({len(schedule_rows)} > {MAX_TASKS_FOR_CPSAT}), "
                    "skipping CP-SAT and using fallback"
                )
            else:
                logger.info("Attempting CP-SAT repair...")
                result = cpsat_repair(
                    scenario_id,
                    schedule_rows,
                    use_plant_calendar,
                    plant_cd,
                    use_machine_constraints,
                    predictions=predictions,
                    risk_weight=risk_weight
                )

                if result is not None:
                    logger.info("✓ CP-SAT repair succeeded")
                    return result
                else:
                    logger.warning("CP-SAT repair returned None, falling back")

        except RepairInfeasible as e:
            logger.warning(f"CP-SAT repair infeasible: {e}, falling back")
        except Exception as e:
            logger.error(f"CP-SAT repair error: {e}, falling back", exc_info=True)

    # Step 2: Fallback to time-shift repair
    logger.info("Using time-shift fallback repair...")
    return time_shift_repair(schedule_rows)


def time_shift_repair(schedule_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    기존 시간 이동 기반 Repair (임시 방식, fallback용)

    간단한 휴리스틱:
    1. order_id, op_seq 순서로 정렬
    2. 각 작업을 순차적으로 배치하되, resource 충돌 시 뒤로 밀기
    """
    if not schedule_rows:
        return schedule_rows

    logger.info(f"Time-shift repair for {len(schedule_rows)} tasks")

    # 정렬: order_id, op_seq
    sorted_rows = sorted(
        schedule_rows,
        key=lambda x: (x.get('order_id', ''), x.get('op_seq', 0))
    )

    # Resource별 마지막 종료 시간 추적
    resource_end_times: Dict[str, datetime] = {}

    # Order별 마지막 종료 시간 추적 (precedence)
    order_end_times: Dict[str, datetime] = {}

    repaired_rows = []

    for row in sorted_rows:
        order_id = row.get('order_id', '')
        resource_code = row.get('resource_code', 'UNKNOWN')
        duration_minutes = row.get('duration_minutes', 60)
        old_start = row.get('start_dt')

        # 최소 시작 시간 계산
        min_start = old_start if old_start else datetime.now()

        # 1) Order precedence: 이전 op 종료 후
        if order_id in order_end_times:
            min_start = max(min_start, order_end_times[order_id])

        # 2) Resource conflict: resource 마지막 종료 후
        if resource_code in resource_end_times:
            min_start = max(min_start, resource_end_times[resource_code])

        # 새로운 시작/종료 시간
        new_start = min_start
        new_end = new_start + timedelta(minutes=duration_minutes)

        # 업데이트
        row_copy = row.copy()
        row_copy['start_dt'] = new_start
        row_copy['end_dt'] = new_end

        # 추적 업데이트
        resource_end_times[resource_code] = new_end
        order_end_times[order_id] = new_end

        repaired_rows.append(row_copy)

        if DEBUG_REPAIR:
            deviation = (new_start - old_start).total_seconds() / 60 if old_start else 0
            logger.debug(
                f"Task {order_id}-{row.get('op_seq')} @ {resource_code} "
                f"moved by {deviation:.0f} min"
            )

    logger.info("Time-shift repair completed")
    return repaired_rows


# ==============================================================================
# 기존 호환성 함수 (선택)
# ==============================================================================

def repair_schedule(schedule_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    기존 repair_schedule() 함수 (호환성 유지)

    CP-SAT를 사용하지 않고 바로 time-shift repair 수행
    """
    logger.info("Legacy repair_schedule() called (time-shift only)")
    return time_shift_repair(schedule_rows)
