"""
CP-SAT 기반 스케줄 Repair 엔진

OR-Tools CP-SAT Solver를 사용하여 제약 조건을 만족하는
스케줄을 생성합니다.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from decimal import Decimal

from ortools.sat.python import cp_model

from .constants import (
    CPSAT_TIMEOUT_SECONDS,
    MAX_TASKS_FOR_CPSAT,
    WEIGHT_DEVIATION,
    WEIGHT_MAKESPAN,
    WEIGHT_TARDINESS,
    WORK_START_HOUR,
    WORK_END_HOUR,
    WORK_MINUTES_PER_DAY,
    MINUTES_PER_HOUR,
    MINUTES_PER_DAY,
    CPSAT_VERBOSE,
    DEBUG_REPAIR,
)

logger = logging.getLogger(__name__)


class RepairInfeasible(Exception):
    """Repair가 불가능한 경우 발생하는 예외"""
    pass


def cpsat_repair(
    scenario_id: int,
    schedule_rows: List[Dict[str, Any]],
    use_plant_calendar: bool = True,
    plant_cd: str = None,
    use_machine_constraints: bool = True,
    predictions=None,
    risk_weight: float = 3.0
) -> Optional[List[Dict[str, Any]]]:
    """
    CP-SAT를 사용하여 스케줄 Repair

    Args:
        scenario_id: 시나리오 ID
        schedule_rows: 스케줄 행 리스트
            [
                {
                    'id': int,
                    'order_id': str,
                    'op_seq': int,
                    'resource_code': str,
                    'start_dt': datetime,
                    'end_dt': datetime,
                    'duration_minutes': int,  # setup + proc
                    'due_date': datetime (optional),
                },
                ...
            ]
        use_plant_calendar: PlantCalendar 사용 여부 (Phase 2 기능)
        plant_cd: 공장 코드 (PlantCalendar 조회용, optional)
        use_machine_constraints: MachineWorkTime/Downtime 사용 여부 (Phase 3 기능)
        predictions: DOWN_RISK Prediction QuerySet (STEP 2 추가)
        risk_weight: DOWN_RISK penalty 가중치 (기본 3.0)

    Returns:
        Repaired schedule_rows (None if infeasible)
    """
    try:
        if not schedule_rows:
            logger.warning("Empty schedule_rows, nothing to repair")
            return schedule_rows

        if len(schedule_rows) > MAX_TASKS_FOR_CPSAT:
            logger.warning(
                f"Too many tasks ({len(schedule_rows)} > {MAX_TASKS_FOR_CPSAT}), "
                "CP-SAT may be slow"
            )
            return None

        logger.info(f"Starting CP-SAT repair for {len(schedule_rows)} tasks")

        # Step 1: 데이터 전처리
        tasks, scenario_start_dt, horizon_minutes = _preprocess_data(schedule_rows)

        if not tasks:
            logger.warning("No valid tasks after preprocessing")
            return schedule_rows

        # Step 2: CP-SAT 모델 생성
        model = cp_model.CpModel()

        # Step 3: 변수 생성
        task_vars = _create_variables(model, tasks, horizon_minutes)

        # Step 4: 제약 조건 추가
        _add_constraints(
            model, tasks, task_vars,
            use_plant_calendar, plant_cd,
            use_machine_constraints,
            scenario_start_dt
        )

        # Step 5: 목적함수 설정 (DOWN_RISK 반영)
        objective_expr = _create_objective(
            model, tasks, task_vars, horizon_minutes,
            predictions=predictions,
            risk_weight=risk_weight
        )
        model.Minimize(objective_expr)

        # Step 6: Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = CPSAT_TIMEOUT_SECONDS

        if CPSAT_VERBOSE:
            solver.parameters.log_search_progress = True

        logger.info("Solving CP-SAT model...")
        status = solver.Solve(model)

        # Step 7: 결과 처리
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            logger.info(
                f"CP-SAT solved successfully (status={status}, "
                f"obj={solver.ObjectiveValue():.2f}, "
                f"time={solver.WallTime():.2f}s)"
            )
            return _extract_solution(solver, tasks, task_vars, schedule_rows, scenario_start_dt)
        else:
            logger.warning(f"CP-SAT failed (status={status})")
            return None

    except Exception as e:
        logger.error(f"CP-SAT repair error: {e}", exc_info=True)
        return None


# ==============================================================================
# Helper Functions
# ==============================================================================

def _preprocess_data(
    schedule_rows: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], datetime, int]:
    """
    데이터 전처리

    Returns:
        (tasks, scenario_start_dt, horizon_minutes)
    """
    if not schedule_rows:
        return [], datetime.now(), 0

    # scenario_start_dt: 가장 이른 시작 시간의 자정 (00:00)
    start_dts = [row['start_dt'] for row in schedule_rows if row.get('start_dt')]
    if not start_dts:
        scenario_start_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        earliest_start = min(start_dts)
        # 해당 날짜의 00:00으로 설정
        scenario_start_dt = earliest_start.replace(hour=0, minute=0, second=0, microsecond=0)

    # horizon 계산
    end_dts = [row['end_dt'] for row in schedule_rows if row.get('end_dt')]
    if end_dts:
        max_end_dt = max(end_dts)
        horizon_minutes = int((max_end_dt - scenario_start_dt).total_seconds() / 60) + 1440
    else:
        horizon_minutes = 7 * MINUTES_PER_DAY  # 7일

    # Task 리스트 생성
    tasks = []
    for idx, row in enumerate(schedule_rows):
        task = {
            'idx': idx,
            'id': row.get('id'),
            'order_id': row.get('order_id'),
            'op_seq': row.get('op_seq', 1),
            'resource_code': row.get('resource_code', 'UNKNOWN'),
            'duration_minutes': row.get('duration_minutes', 60),
            'old_start_dt': row.get('start_dt'),
            'due_date': row.get('due_date'),
        }

        # old_start_minutes 계산
        if task['old_start_dt']:
            old_start_minutes = int((task['old_start_dt'] - scenario_start_dt).total_seconds() / 60)
            task['old_start_minutes'] = max(0, old_start_minutes)
        else:
            task['old_start_minutes'] = 0

        # due_date_minutes 계산
        if task['due_date']:
            due_minutes = int((task['due_date'] - scenario_start_dt).total_seconds() / 60)
            task['due_date_minutes'] = max(0, due_minutes)
        else:
            task['due_date_minutes'] = horizon_minutes

        tasks.append(task)

    logger.debug(f"Preprocessed {len(tasks)} tasks, horizon={horizon_minutes} minutes")
    return tasks, scenario_start_dt, horizon_minutes


def _create_variables(
    model: cp_model.CpModel,
    tasks: List[Dict[str, Any]],
    horizon_minutes: int
) -> Dict[int, Dict[str, Any]]:
    """
    CP-SAT 변수 생성

    Returns:
        task_vars: {
            task_idx: {
                'start': IntVar,
                'end': IntVar,
                'interval': IntervalVar,
                'deviation': IntVar,
                'abs_deviation': IntVar,
                'tardiness': IntVar,
            }
        }
    """
    task_vars = {}

    for task in tasks:
        idx = task['idx']
        duration = task['duration_minutes']

        # Start, End 변수
        start_var = model.NewIntVar(0, horizon_minutes, f'start_{idx}')
        end_var = model.NewIntVar(0, horizon_minutes, f'end_{idx}')

        # Interval 변수 (Resource NoOverlap용)
        interval_var = model.NewIntervalVar(
            start_var,
            duration,
            end_var,
            f'interval_{idx}'
        )

        # Deviation 변수 (변경 최소화용)
        old_start = task['old_start_minutes']
        deviation_var = model.NewIntVar(
            -horizon_minutes,
            horizon_minutes,
            f'deviation_{idx}'
        )
        model.Add(deviation_var == start_var - old_start)

        # Absolute deviation
        abs_deviation_var = model.NewIntVar(0, horizon_minutes, f'abs_dev_{idx}')
        model.AddAbsEquality(abs_deviation_var, deviation_var)

        # Tardiness 변수 (지연 시간)
        due_minutes = task['due_date_minutes']
        tardiness_var = model.NewIntVar(0, horizon_minutes, f'tardiness_{idx}')
        model.AddMaxEquality(tardiness_var, [end_var - due_minutes, 0])

        task_vars[idx] = {
            'start': start_var,
            'end': end_var,
            'interval': interval_var,
            'deviation': deviation_var,
            'abs_deviation': abs_deviation_var,
            'tardiness': tardiness_var,
        }

    logger.debug(f"Created variables for {len(tasks)} tasks")
    return task_vars


def _add_constraints(
    model: cp_model.CpModel,
    tasks: List[Dict[str, Any]],
    task_vars: Dict[int, Dict[str, Any]],
    use_plant_calendar: bool,
    plant_cd: str = None,
    use_machine_constraints: bool = True,
    scenario_start_dt: datetime = None
):
    """제약 조건 추가"""

    # 1) Resource NoOverlap 제약
    _add_resource_nooverlap_constraints(model, tasks, task_vars)

    # 2) Order Precedence 제약
    _add_order_precedence_constraints(model, tasks, task_vars)

    # 3) Time Window 제약 (근무시간)
    if use_machine_constraints and plant_cd and scenario_start_dt:
        # Phase 3: MachineWorkTime + MachineDowntime 통합
        _add_machine_specific_constraints(
            model, tasks, task_vars, plant_cd, scenario_start_dt,
            use_plant_calendar
        )
    elif use_plant_calendar and plant_cd and scenario_start_dt:
        # Phase 2: PlantCalendar만 사용
        _add_plant_calendar_constraints(model, tasks, task_vars, plant_cd, scenario_start_dt)
    else:
        # Phase 1: MVP (고정 근무시간)
        _add_simple_work_hour_constraints(model, tasks, task_vars)


def _add_resource_nooverlap_constraints(
    model: cp_model.CpModel,
    tasks: List[Dict[str, Any]],
    task_vars: Dict[int, Dict[str, Any]]
):
    """
    Resource NoOverlap 제약

    동일 resource_code에서 작업이 겹치지 않도록 함
    """
    # Resource별로 그룹핑
    resource_tasks = defaultdict(list)
    for task in tasks:
        resource_code = task['resource_code']
        resource_tasks[resource_code].append(task['idx'])

    # 각 Resource에 대해 NoOverlap 제약 추가
    for resource_code, task_indices in resource_tasks.items():
        if len(task_indices) <= 1:
            continue  # 작업이 1개 이하면 제약 불필요

        intervals = [task_vars[idx]['interval'] for idx in task_indices]
        model.AddNoOverlap(intervals)

    logger.debug(f"Added NoOverlap constraints for {len(resource_tasks)} resources")


def _add_order_precedence_constraints(
    model: cp_model.CpModel,
    tasks: List[Dict[str, Any]],
    task_vars: Dict[int, Dict[str, Any]]
):
    """
    Order Precedence 제약

    동일 order_id 내에서 op_seq 순서대로 실행
    (이전 작업 종료 <= 다음 작업 시작)
    """
    # Order별로 그룹핑
    order_ops = defaultdict(list)
    for task in tasks:
        order_id = task['order_id']
        order_ops[order_id].append((task['op_seq'], task['idx']))

    # 각 Order에 대해 Precedence 제약 추가
    precedence_count = 0
    for order_id, ops in order_ops.items():
        if len(ops) <= 1:
            continue

        # op_seq 순서대로 정렬
        ops.sort(key=lambda x: x[0])

        # 연속된 작업 간 제약 추가
        for i in range(len(ops) - 1):
            prev_idx = ops[i][1]
            next_idx = ops[i + 1][1]

            prev_end = task_vars[prev_idx]['end']
            next_start = task_vars[next_idx]['start']

            model.Add(prev_end <= next_start)
            precedence_count += 1

    logger.debug(f"Added {precedence_count} precedence constraints for {len(order_ops)} orders")


def _add_plant_calendar_constraints(
    model: cp_model.CpModel,
    tasks: List[Dict[str, Any]],
    task_vars: Dict[int, Dict[str, Any]],
    plant_cd: str,
    scenario_start_dt: datetime
):
    """
    PlantCalendar 기반 근무시간 제약 (Phase 2)

    PlantCalendar 테이블에서 실제 근무일/시간을 가져와서 적용
    """
    try:
        from apps.erp.models_calendar import PlantCalendar
        from datetime import datetime as dt, timedelta

        logger.info(f"PlantCalendar constraints enabled for plant_cd={plant_cd}")

        # Phase 2 완전 구현:
        # 1. PlantCalendar에서 근무일 조회 (30일 범위)
        end_dt = scenario_start_dt + timedelta(days=30)

        calendars = PlantCalendar.objects.filter(
            plant_cd=plant_cd,
            work_date__gte=scenario_start_dt.date(),
            work_date__lte=end_dt.date(),
            is_available=True
        ).order_by('work_date')

        if not calendars.exists():
            logger.warning(f"No PlantCalendar data found for {plant_cd}, using simple work hours")
            _add_simple_work_hour_constraints(model, tasks, task_vars)
            return

        # 2. 각 근무일의 work time windows 생성 (분 단위, scenario_start 기준)
        work_windows = []  # [(start_min, end_min), ...]

        for cal in calendars:
            if cal.day_type == 'HOLIDAY' and not cal.day_type == 'OVERTIME':
                continue  # 휴일 제외 (특근은 포함)

            # 해당 날짜의 시작 시간 (00:00)
            day_start_dt = dt.combine(cal.work_date, dt.min.time())
            day_offset_min = int((day_start_dt - scenario_start_dt).total_seconds() / 60)

            # 근무 시작/종료 시간 (분 단위)
            work_start_min = day_offset_min + (cal.work_start_time.hour * 60 + cal.work_start_time.minute)
            work_end_min = day_offset_min + (cal.work_end_time.hour * 60 + cal.work_end_time.minute)

            # 휴게시간 처리
            if cal.break_start_time and cal.break_end_time:
                break_start_min = day_offset_min + (cal.break_start_time.hour * 60 + cal.break_start_time.minute)
                break_end_min = day_offset_min + (cal.break_end_time.hour * 60 + cal.break_end_time.minute)

                # 휴게 전/후로 분할
                work_windows.append((work_start_min, break_start_min))
                work_windows.append((break_end_min, work_end_min))
            else:
                work_windows.append((work_start_min, work_end_min))

        if not work_windows:
            logger.warning("No valid work windows from PlantCalendar, using simple work hours")
            _add_simple_work_hour_constraints(model, tasks, task_vars)
            return

        logger.info(f"Created {len(work_windows)} work time windows from PlantCalendar")

        # 3. CP-SAT 제약: 각 작업의 start와 end가 work windows 내에 있어야 함
        for task in tasks:
            idx = task['idx']
            start_var = task_vars[idx]['start']
            end_var = task_vars[idx]['end']
            duration = task['duration_minutes']

            # 작업이 어느 work window에 속하는지 표현하는 boolean 변수들
            window_vars = []
            for i, (win_start, win_end) in enumerate(work_windows):
                # 작업이 이 window에 속하는가?
                in_window = model.NewBoolVar(f'task_{idx}_in_window_{i}')
                window_vars.append(in_window)

                # in_window == True이면:
                # - start >= win_start
                # - end <= win_end
                # - start + duration == end
                model.Add(start_var >= win_start).OnlyEnforceIf(in_window)
                model.Add(end_var <= win_end).OnlyEnforceIf(in_window)

            # 최소 하나의 window에는 속해야 함
            model.Add(sum(window_vars) >= 1)

            # Duration 제약 (이미 변수 생성 시 추가되었지만 명시)
            model.Add(end_var == start_var + duration)

        logger.debug(f"Added PlantCalendar work hour constraints with {len(work_windows)} windows")

    except Exception as e:
        logger.error(f"PlantCalendar constraints failed: {e}, using simple work hours")
        _add_simple_work_hour_constraints(model, tasks, task_vars)


def _add_machine_specific_constraints(
    model: cp_model.CpModel,
    tasks: List[Dict[str, Any]],
    task_vars: Dict[int, Dict[str, Any]],
    plant_cd: str,
    scenario_start_dt: datetime,
    use_plant_calendar: bool = True
):
    """
    설비별 작업 시간 제약 (Phase 3)

    PlantCalendar + MachineWorkTime + MachineDowntime을 통합하여
    각 설비의 실제 가용 시간만 작업 스케줄링

    Args:
        model: CP-SAT 모델
        tasks: 작업 리스트
        task_vars: 작업 변수 딕셔너리
        plant_cd: 공장 코드
        scenario_start_dt: 시나리오 시작 시간 (00:00으로 정규화됨)
        use_plant_calendar: PlantCalendar도 함께 고려할지 여부
    """
    try:
        from apps.erp.models_calendar import (
            PlantCalendar, MachineWorkTime, MachineDowntime
        )
        from apps.erp.models import MasterMachine
        from datetime import datetime as dt, timedelta, time

        logger.info(f"Phase 3: Machine-specific constraints enabled for plant_cd={plant_cd}")

        # Step 1: 설비별로 작업 그룹핑
        machine_tasks = defaultdict(list)
        for task in tasks:
            resource_code = task['resource_code']
            machine_tasks[resource_code].append(task)

        # Step 2: 각 설비별로 가용 시간 계산
        end_dt = scenario_start_dt + timedelta(days=30)

        for resource_code, machine_task_list in machine_tasks.items():
            logger.debug(f"Processing machine {resource_code} with {len(machine_task_list)} tasks")

            # Step 2-1: MasterMachine 조회
            try:
                machine = MasterMachine.objects.get(mc_cd=resource_code)
            except MasterMachine.DoesNotExist:
                logger.warning(f"Machine {resource_code} not found, using PlantCalendar only")
                if use_plant_calendar:
                    _add_plant_calendar_constraints_for_tasks(
                        model, machine_task_list, task_vars, plant_cd, scenario_start_dt
                    )
                else:
                    _add_simple_work_hour_constraints_for_tasks(
                        model, machine_task_list, task_vars
                    )
                continue

            # Step 2-2: Work time windows 생성
            work_windows = _generate_machine_work_windows(
                machine, plant_cd, scenario_start_dt, end_dt, use_plant_calendar
            )

            # Step 2-3: Downtime 제외
            downtimes = MachineDowntime.objects.filter(
                machine=machine,
                start_dt__lt=end_dt,
                end_dt__gt=scenario_start_dt
            )

            if downtimes.exists():
                logger.debug(f"Found {downtimes.count()} downtimes for {resource_code}")
                work_windows = _exclude_downtimes(work_windows, downtimes, scenario_start_dt)

            if not work_windows:
                logger.warning(f"No valid work windows for {resource_code}, using PlantCalendar")
                if use_plant_calendar:
                    _add_plant_calendar_constraints_for_tasks(
                        model, machine_task_list, task_vars, plant_cd, scenario_start_dt
                    )
                else:
                    _add_simple_work_hour_constraints_for_tasks(
                        model, machine_task_list, task_vars
                    )
                continue

            logger.info(f"Machine {resource_code}: {len(work_windows)} work windows")

            # Step 2-4: CP-SAT 제약 추가 (각 작업이 work windows 내에만)
            for task in machine_task_list:
                idx = task['idx']
                start_var = task_vars[idx]['start']
                end_var = task_vars[idx]['end']
                duration = task['duration_minutes']

                # Capacity rate 반영 (Phase 3)
                adjusted_duration = _adjust_duration_by_capacity(
                    duration, machine, plant_cd, scenario_start_dt, end_dt
                )

                if adjusted_duration != duration:
                    logger.debug(f"Task {idx} duration adjusted: {duration} -> {adjusted_duration}")
                    # Duration 제약 업데이트
                    model.Add(end_var == start_var + adjusted_duration)

                # Boolean 변수: 어느 window에 속하는가?
                window_vars = []
                for i, (win_start, win_end) in enumerate(work_windows):
                    in_window = model.NewBoolVar(f'task_{idx}_machine_window_{i}')
                    window_vars.append(in_window)

                    model.Add(start_var >= win_start).OnlyEnforceIf(in_window)
                    model.Add(end_var <= win_end).OnlyEnforceIf(in_window)

                # 최소 하나의 window에는 속해야 함
                if window_vars:
                    model.Add(sum(window_vars) >= 1)

        logger.debug(f"Added machine-specific constraints for {len(machine_tasks)} machines")

    except Exception as e:
        logger.error(f"Machine-specific constraints failed: {e}, falling back to PlantCalendar")
        if use_plant_calendar:
            _add_plant_calendar_constraints(model, tasks, task_vars, plant_cd, scenario_start_dt)
        else:
            _add_simple_work_hour_constraints(model, tasks, task_vars)


def _generate_machine_work_windows(
    machine,
    plant_cd: str,
    scenario_start_dt: datetime,
    end_dt: datetime,
    use_plant_calendar: bool
) -> List[Tuple[int, int]]:
    """
    설비별 work time windows 생성

    Returns:
        List of (start_min, end_min) tuples (분 단위, scenario_start_dt 기준)
    """
    from apps.erp.models_calendar import PlantCalendar, MachineWorkTime
    from datetime import datetime as dt, timedelta, time

    work_windows = []

    # MachineWorkTime 조회 (요일별 가동시간)
    machine_work_times = MachineWorkTime.objects.filter(
        machine=machine,
        is_available=True
    )

    # 요일별 가동시간 매핑
    dow_work_times = {}
    for mwt in machine_work_times:
        dow_work_times[mwt.day_of_week] = {
            'start_time': mwt.start_time,
            'end_time': mwt.end_time,
            'is_overnight': mwt.is_overnight
        }

    if not dow_work_times:
        logger.warning(f"No MachineWorkTime for {machine.mc_cd}, using PlantCalendar")
        # MachineWorkTime 없으면 PlantCalendar만 사용
        if use_plant_calendar:
            return _generate_plant_work_windows(plant_cd, scenario_start_dt, end_dt)
        else:
            # Fallback: 평일 08:00~17:00
            return _generate_default_work_windows(scenario_start_dt, end_dt)

    # PlantCalendar 조회 (근무일 확인)
    if use_plant_calendar:
        calendars = PlantCalendar.objects.filter(
            plant_cd=plant_cd,
            work_date__gte=scenario_start_dt.date(),
            work_date__lte=end_dt.date(),
            is_available=True
        ).order_by('work_date')

        plant_work_dates = {cal.work_date for cal in calendars if cal.day_type != 'HOLIDAY'}
    else:
        # PlantCalendar 미사용 시 모든 날짜 허용
        plant_work_dates = None

    # 날짜별로 순회하며 work windows 생성
    current_date = scenario_start_dt.date()
    while current_date <= end_dt.date():
        # PlantCalendar 체크
        if plant_work_dates is not None and current_date not in plant_work_dates:
            current_date += timedelta(days=1)
            continue

        # 요일별 MachineWorkTime 체크
        dow = current_date.weekday()  # 0=월, 6=일
        if dow not in dow_work_times:
            current_date += timedelta(days=1)
            continue

        mwt_info = dow_work_times[dow]

        # 해당 날짜의 00:00 기준 offset
        day_start_dt = dt.combine(current_date, time(0, 0))
        day_offset_min = int((day_start_dt - scenario_start_dt).total_seconds() / 60)

        # 작업 시작/종료 시간
        work_start_min = day_offset_min + (mwt_info['start_time'].hour * 60 + mwt_info['start_time'].minute)
        work_end_min = day_offset_min + (mwt_info['end_time'].hour * 60 + mwt_info['end_time'].minute)

        # 야간 근무 처리
        if mwt_info['is_overnight'] or work_end_min <= work_start_min:
            work_end_min += 24 * 60  # 다음날로

        # PlantCalendar의 휴게시간 반영 (선택)
        if use_plant_calendar:
            try:
                cal = PlantCalendar.objects.get(
                    plant_cd=plant_cd,
                    work_date=current_date
                )
                if cal.break_start_time and cal.break_end_time:
                    break_start_min = day_offset_min + (cal.break_start_time.hour * 60 + cal.break_start_time.minute)
                    break_end_min = day_offset_min + (cal.break_end_time.hour * 60 + cal.break_end_time.minute)

                    # 휴게 전/후 분할
                    work_windows.append((work_start_min, break_start_min))
                    work_windows.append((break_end_min, work_end_min))
                else:
                    work_windows.append((work_start_min, work_end_min))
            except PlantCalendar.DoesNotExist:
                work_windows.append((work_start_min, work_end_min))
        else:
            work_windows.append((work_start_min, work_end_min))

        current_date += timedelta(days=1)

    return work_windows


def _generate_plant_work_windows(
    plant_cd: str,
    scenario_start_dt: datetime,
    end_dt: datetime
) -> List[Tuple[int, int]]:
    """PlantCalendar만 사용하여 work windows 생성"""
    from apps.erp.models_calendar import PlantCalendar
    from datetime import datetime as dt, timedelta, time

    work_windows = []

    calendars = PlantCalendar.objects.filter(
        plant_cd=plant_cd,
        work_date__gte=scenario_start_dt.date(),
        work_date__lte=end_dt.date(),
        is_available=True
    ).order_by('work_date')

    for cal in calendars:
        if cal.day_type == 'HOLIDAY':
            continue

        day_start_dt = dt.combine(cal.work_date, time(0, 0))
        day_offset_min = int((day_start_dt - scenario_start_dt).total_seconds() / 60)

        work_start_min = day_offset_min + (cal.work_start_time.hour * 60 + cal.work_start_time.minute)
        work_end_min = day_offset_min + (cal.work_end_time.hour * 60 + cal.work_end_time.minute)

        if cal.break_start_time and cal.break_end_time:
            break_start_min = day_offset_min + (cal.break_start_time.hour * 60 + cal.break_start_time.minute)
            break_end_min = day_offset_min + (cal.break_end_time.hour * 60 + cal.break_end_time.minute)
            work_windows.append((work_start_min, break_start_min))
            work_windows.append((break_end_min, work_end_min))
        else:
            work_windows.append((work_start_min, work_end_min))

    return work_windows


def _generate_default_work_windows(
    scenario_start_dt: datetime,
    end_dt: datetime
) -> List[Tuple[int, int]]:
    """기본 work windows: 평일 08:00~17:00"""
    from datetime import timedelta, time as dt_time, datetime as dt

    work_windows = []
    current_date = scenario_start_dt.date()

    while current_date <= end_dt.date():
        dow = current_date.weekday()
        if dow >= 5:  # 토, 일 제외
            current_date += timedelta(days=1)
            continue

        day_start_dt = dt.combine(current_date, dt_time(0, 0))
        day_offset_min = int((day_start_dt - scenario_start_dt).total_seconds() / 60)

        work_start_min = day_offset_min + 8 * 60  # 08:00
        work_end_min = day_offset_min + 17 * 60   # 17:00

        work_windows.append((work_start_min, work_end_min))
        current_date += timedelta(days=1)

    return work_windows


def _exclude_downtimes(
    work_windows: List[Tuple[int, int]],
    downtimes,
    scenario_start_dt: datetime
) -> List[Tuple[int, int]]:
    """
    Downtime 기간을 work windows에서 제외

    Returns:
        Downtime이 제외된 work windows
    """
    result_windows = []

    # Downtime을 분 단위로 변환
    downtime_periods = []
    for dt in downtimes:
        start_min = int((dt.start_dt - scenario_start_dt).total_seconds() / 60)
        end_min = int((dt.end_dt - scenario_start_dt).total_seconds() / 60)
        downtime_periods.append((start_min, end_min))

    # 각 work window에서 downtime 제외
    for win_start, win_end in work_windows:
        current_start = win_start

        # 해당 window와 겹치는 downtime들 찾기
        overlapping_dts = [
            (dt_start, dt_end) for dt_start, dt_end in downtime_periods
            if not (dt_end <= win_start or dt_start >= win_end)
        ]

        if not overlapping_dts:
            # Downtime 없으면 그대로 추가
            result_windows.append((win_start, win_end))
            continue

        # Downtime 시작 시간 기준 정렬
        overlapping_dts.sort()

        for dt_start, dt_end in overlapping_dts:
            # Downtime 이전 부분이 있으면 추가
            if current_start < dt_start:
                result_windows.append((current_start, min(dt_start, win_end)))

            # Downtime 이후로 이동
            current_start = max(current_start, dt_end)

            if current_start >= win_end:
                break

        # 마지막 Downtime 이후 남은 부분
        if current_start < win_end:
            result_windows.append((current_start, win_end))

    return result_windows


def _adjust_duration_by_capacity(
    duration_minutes: int,
    machine,
    plant_cd: str,
    scenario_start_dt: datetime,
    end_dt: datetime
) -> int:
    """
    Capacity rate를 반영하여 duration 조정

    예: capacity_rate=80%, duration=60분 → 75분 (60/0.8)

    Returns:
        조정된 duration (분)
    """
    from apps.erp.models_calendar import PlantCalendar

    try:
        # PlantCalendar에서 평균 capacity rate 계산
        calendars = PlantCalendar.objects.filter(
            plant_cd=plant_cd,
            work_date__gte=scenario_start_dt.date(),
            work_date__lte=end_dt.date(),
            is_available=True
        )

        if not calendars.exists():
            return duration_minutes

        # 평균 capacity rate
        total_rate = sum(float(cal.capacity_rate) for cal in calendars)
        avg_rate = total_rate / calendars.count()

        if avg_rate <= 0 or avg_rate >= 100:
            return duration_minutes

        # Duration 조정: duration / (rate / 100)
        adjusted = int(duration_minutes / (avg_rate / 100))
        return adjusted

    except Exception as e:
        logger.warning(f"Capacity rate adjustment failed: {e}")
        return duration_minutes


def _add_plant_calendar_constraints_for_tasks(
    model: cp_model.CpModel,
    tasks: List[Dict[str, Any]],
    task_vars: Dict[int, Dict[str, Any]],
    plant_cd: str,
    scenario_start_dt: datetime
):
    """특정 작업들에만 PlantCalendar 제약 적용"""
    _add_plant_calendar_constraints(model, tasks, task_vars, plant_cd, scenario_start_dt)


def _add_simple_work_hour_constraints_for_tasks(
    model: cp_model.CpModel,
    tasks: List[Dict[str, Any]],
    task_vars: Dict[int, Dict[str, Any]]
):
    """특정 작업들에만 단순 근무시간 제약 적용"""
    _add_simple_work_hour_constraints(model, tasks, task_vars)


def _add_simple_work_hour_constraints(
    model: cp_model.CpModel,
    tasks: List[Dict[str, Any]],
    task_vars: Dict[int, Dict[str, Any]]
):
    """
    단순 근무시간 제약 (MVP)

    08:00~17:00만 작업 가능

    MVP 가정: 각 작업은 하나의 근무일 내에서 완료되어야 함
    (즉, 작업이 비근무시간을 건너뛰지 않음)
    """
    work_start_minutes = WORK_START_HOUR * MINUTES_PER_HOUR  # 480 (08:00)
    work_end_minutes = WORK_END_HOUR * MINUTES_PER_HOUR  # 1020 (17:00)
    work_minutes_per_day = work_end_minutes - work_start_minutes  # 540 (9 hours)

    for task in tasks:
        idx = task['idx']
        start_var = task_vars[idx]['start']
        end_var = task_vars[idx]['end']
        duration = task['duration_minutes']

        # 작업 duration이 근무시간보다 길면 여러 날 필요 - MVP에서는 허용
        # 하지만 각 날마다 근무시간만 사용

        # 시작 시간의 날짜와 하루 내 시간 분해
        start_day = model.NewIntVar(0, 100, f'start_day_{idx}')
        start_time_in_day = model.NewIntVar(0, MINUTES_PER_DAY - 1, f'start_time_{idx}')

        model.AddDivisionEquality(start_day, start_var, MINUTES_PER_DAY)
        model.AddModuloEquality(start_time_in_day, start_var, MINUTES_PER_DAY)

        # 시작 시간은 근무시간 내에만 (08:00 ~ 17:00)
        model.Add(start_time_in_day >= work_start_minutes)
        model.Add(start_time_in_day < work_end_minutes)

        # 종료 시간도 근무시간 내에만
        end_day = model.NewIntVar(0, 100, f'end_day_{idx}')
        end_time_in_day = model.NewIntVar(0, MINUTES_PER_DAY - 1, f'end_time_{idx}')

        model.AddDivisionEquality(end_day, end_var, MINUTES_PER_DAY)
        model.AddModuloEquality(end_time_in_day, end_var, MINUTES_PER_DAY)

        model.Add(end_time_in_day > work_start_minutes)  # 08:00 이후
        model.Add(end_time_in_day <= work_end_minutes)  # 17:00 이하

        # duration 제약
        model.Add(end_var == start_var + duration)

        # MVP: 단순화를 위해 작업이 하루 근무시간을 넘지 않는다고 가정
        # (실제로는 duration이 540분 이하여야 함)
        # 만약 duration > 540이면, Phase 2에서 비근무시간 건너뛰기 로직 필요

    logger.debug(f"Added simple work hour constraints (08:00-17:00)")


def _create_objective(
    model: cp_model.CpModel,
    tasks: List[Dict[str, Any]],
    task_vars: Dict[int, Dict[str, Any]],
    horizon_minutes: int,
    predictions=None,
    risk_weight: float = 3.0
) -> Any:
    """
    목적함수 생성 (STEP 2: DOWN_RISK 반영)

    minimize(
        W1 * sum(|new_start - old_start|)
      + W2 * makespan
      + W3 * total_tardiness
      + W4 * risk_penalty  ← STEP 2 추가
    )

    Args:
        predictions: DOWN_RISK Prediction QuerySet (optional)
        risk_weight: DOWN_RISK penalty 가중치 (기본 3.0)
    """
    # 1) Total deviation (변경 최소화)
    total_deviation = sum(
        task_vars[task['idx']]['abs_deviation']
        for task in tasks
    )

    # 2) Makespan (전체 작업 완료 시간)
    makespan = model.NewIntVar(0, horizon_minutes, 'makespan')
    model.AddMaxEquality(makespan, [
        task_vars[task['idx']]['end']
        for task in tasks
    ])

    # 3) Total tardiness (총 지연 시간)
    total_tardiness = sum(
        task_vars[task['idx']]['tardiness']
        for task in tasks
    )

    # 4) DOWN_RISK penalty (STEP 2 추가)
    total_risk_penalty = _calculate_risk_penalty(model, tasks, predictions)

    # 목적함수
    objective = (
        WEIGHT_DEVIATION * total_deviation
        + WEIGHT_MAKESPAN * makespan
        + WEIGHT_TARDINESS * total_tardiness
        + int(risk_weight) * total_risk_penalty  # ← STEP 2 추가
    )

    logger.debug(
        f"Objective: {WEIGHT_DEVIATION}*deviation + {WEIGHT_MAKESPAN}*makespan + "
        f"{WEIGHT_TARDINESS}*tardiness + {int(risk_weight)}*risk_penalty"
    )

    return objective


def _calculate_risk_penalty(
    model: cp_model.CpModel,
    tasks: List[Dict[str, Any]],
    predictions=None
) -> int:
    """
    DOWN_RISK penalty 계산 (STEP 2)

    risk_penalty = sum(risk * duration) for all tasks

    Args:
        predictions: DOWN_RISK Prediction QuerySet

    Returns:
        int: Total risk penalty (CP-SAT 정수형)
    """
    if predictions is None or not predictions.exists():
        logger.debug("No DOWN_RISK predictions, risk_penalty = 0")
        return 0

    # Prediction을 딕셔너리로 변환 (resource_code -> risk_value)
    risk_dict = {}
    for pred in predictions:
        if pred.prediction_type == 'DOWN_RISK':
            # target_entity format: "RES:<resource_code>"
            resource_code = pred.target_entity.split(':')[1] if ':' in pred.target_entity else pred.target_entity
            risk_dict[resource_code] = pred.predicted_value

    logger.debug(f"Loaded {len(risk_dict)} DOWN_RISK predictions")

    # 각 작업별 risk penalty 변수 생성
    risk_penalties = []

    for task in tasks:
        resource_code = task['resource_code']
        duration = task['duration_minutes']

        # 위험도 조회 (없으면 기본 0.5)
        risk_value = risk_dict.get(resource_code, 0.5)

        # risk_penalty = risk * duration (정수화: risk * 100)
        scaled_risk = int(risk_value * 100)  # 0.75 → 75
        penalty = scaled_risk * duration

        risk_penalties.append(penalty)

        logger.debug(
            f"  Task {task['idx']} ({resource_code}): risk={risk_value:.2f}, "
            f"duration={duration}, penalty={penalty}"
        )

    total_risk_penalty = sum(risk_penalties)
    logger.debug(f"Total risk_penalty = {total_risk_penalty}")

    return total_risk_penalty


def _extract_solution(
    solver: cp_model.CpSolver,
    tasks: List[Dict[str, Any]],
    task_vars: Dict[int, Dict[str, Any]],
    original_rows: List[Dict[str, Any]],
    scenario_start_dt: datetime
) -> List[Dict[str, Any]]:
    """
    CP-SAT 솔루션을 schedule_rows 형식으로 변환
    """
    repaired_rows = []

    for task in tasks:
        idx = task['idx']
        original_row = original_rows[idx].copy()

        # 새로운 start/end 시간 계산
        start_minutes = solver.Value(task_vars[idx]['start'])
        end_minutes = solver.Value(task_vars[idx]['end'])

        new_start_dt = scenario_start_dt + timedelta(minutes=start_minutes)
        new_end_dt = scenario_start_dt + timedelta(minutes=end_minutes)

        # 업데이트
        original_row['start_dt'] = new_start_dt
        original_row['end_dt'] = new_end_dt

        if DEBUG_REPAIR:
            old_start = task['old_start_dt']
            deviation = (new_start_dt - old_start).total_seconds() / 60 if old_start else 0
            logger.debug(
                f"Task {idx}: {task['order_id']}-{task['op_seq']} "
                f"@ {task['resource_code']} "
                f"start_min={start_minutes}, end_min={end_minutes}, "
                f"moved by {deviation:.0f} min"
            )

        repaired_rows.append(original_row)

    return repaired_rows
