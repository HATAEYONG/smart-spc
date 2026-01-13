"""
CP-SAT Repair 사용 예제

이 파일은 CP-SAT Repair 엔진의 사용 방법을 보여줍니다.
"""
from datetime import datetime, timedelta
from .runner import repair_schedule_with_cpsat


def example_basic_repair():
    """
    기본 Repair 예제

    Resource 충돌이 있는 스케줄을 Repair
    """
    print("=" * 80)
    print("Example 1: Basic Repair with Resource Conflict")
    print("=" * 80)

    # 입력 스케줄 (MC-001에서 충돌)
    schedule_rows = [
        {
            'id': 1,
            'order_id': 'WO-001',
            'op_seq': 1,
            'resource_code': 'MC-001',
            'start_dt': datetime(2026, 1, 10, 8, 0),
            'end_dt': datetime(2026, 1, 10, 9, 0),
            'duration_minutes': 60,
            'due_date': datetime(2026, 1, 15, 17, 0),
        },
        {
            'id': 2,
            'order_id': 'WO-002',
            'op_seq': 1,
            'resource_code': 'MC-001',
            'start_dt': datetime(2026, 1, 10, 8, 30),  # 충돌!
            'end_dt': datetime(2026, 1, 10, 9, 30),
            'duration_minutes': 60,
            'due_date': datetime(2026, 1, 15, 17, 0),
        },
    ]

    # Repair 실행
    repaired = repair_schedule_with_cpsat(
        scenario_id=1,
        schedule_rows=schedule_rows,
        use_cpsat=True,
        use_plant_calendar=False  # MVP: 단순 근무시간
    )

    # 결과 출력
    print("\n[Before Repair]")
    for row in schedule_rows:
        print(f"  {row['order_id']}-{row['op_seq']} @ {row['resource_code']}: "
              f"{row['start_dt'].strftime('%H:%M')} ~ {row['end_dt'].strftime('%H:%M')}")

    print("\n[After Repair]")
    for row in repaired:
        print(f"  {row['order_id']}-{row['op_seq']} @ {row['resource_code']}: "
              f"{row['start_dt'].strftime('%H:%M')} ~ {row['end_dt'].strftime('%H:%M')}")

    print("\n[OK] Resource conflict resolved!\n")


def example_precedence_repair():
    """
    Precedence 제약 예제

    동일 Order 내에서 op_seq 순서 위반을 Repair
    """
    print("=" * 80)
    print("Example 2: Precedence Constraint Repair")
    print("=" * 80)

    # 입력 스케줄 (WO-001의 op_seq 순서 위반)
    schedule_rows = [
        {
            'id': 1,
            'order_id': 'WO-001',
            'op_seq': 1,
            'resource_code': 'MC-001',
            'start_dt': datetime(2026, 1, 10, 10, 0),  # 늦음!
            'end_dt': datetime(2026, 1, 10, 11, 0),
            'duration_minutes': 60,
            'due_date': datetime(2026, 1, 15, 17, 0),
        },
        {
            'id': 2,
            'order_id': 'WO-001',
            'op_seq': 2,
            'resource_code': 'MC-002',
            'start_dt': datetime(2026, 1, 10, 8, 0),  # 너무 빠름!
            'end_dt': datetime(2026, 1, 10, 9, 30),
            'duration_minutes': 90,
            'due_date': datetime(2026, 1, 15, 17, 0),
        },
    ]

    # Repair 실행
    repaired = repair_schedule_with_cpsat(
        scenario_id=1,
        schedule_rows=schedule_rows,
        use_cpsat=True,
        use_plant_calendar=False
    )

    # 결과 출력
    print("\n[Before Repair]")
    for row in sorted(schedule_rows, key=lambda x: x['op_seq']):
        print(f"  {row['order_id']}-{row['op_seq']}: "
              f"{row['start_dt'].strftime('%H:%M')} ~ {row['end_dt'].strftime('%H:%M')}")

    print("\n[After Repair]")
    for row in sorted(repaired, key=lambda x: x['op_seq']):
        print(f"  {row['order_id']}-{row['op_seq']}: "
              f"{row['start_dt'].strftime('%H:%M')} ~ {row['end_dt'].strftime('%H:%M')}")

    print("\n[OK] Precedence order enforced!\n")


def example_complex_scenario():
    """
    복잡한 시나리오 예제

    - 여러 Order
    - Resource 충돌
    - Precedence 제약
    """
    print("=" * 80)
    print("Example 3: Complex Scenario with Multiple Constraints")
    print("=" * 80)

    schedule_rows = [
        # WO-001
        {
            'id': 1,
            'order_id': 'WO-001',
            'op_seq': 1,
            'resource_code': 'MC-001',
            'start_dt': datetime(2026, 1, 10, 8, 0),
            'end_dt': datetime(2026, 1, 10, 9, 0),
            'duration_minutes': 60,
            'due_date': datetime(2026, 1, 12, 17, 0),
        },
        {
            'id': 2,
            'order_id': 'WO-001',
            'op_seq': 2,
            'resource_code': 'MC-002',
            'start_dt': datetime(2026, 1, 10, 8, 30),  # Precedence 위반
            'end_dt': datetime(2026, 1, 10, 10, 0),
            'duration_minutes': 90,
            'due_date': datetime(2026, 1, 12, 17, 0),
        },
        # WO-002
        {
            'id': 3,
            'order_id': 'WO-002',
            'op_seq': 1,
            'resource_code': 'MC-001',
            'start_dt': datetime(2026, 1, 10, 8, 30),  # MC-001 충돌
            'end_dt': datetime(2026, 1, 10, 9, 30),
            'duration_minutes': 60,
            'due_date': datetime(2026, 1, 13, 17, 0),
        },
        {
            'id': 4,
            'order_id': 'WO-002',
            'op_seq': 2,
            'resource_code': 'MC-003',
            'start_dt': datetime(2026, 1, 10, 9, 0),
            'end_dt': datetime(2026, 1, 10, 10, 30),
            'duration_minutes': 90,
            'due_date': datetime(2026, 1, 13, 17, 0),
        },
        # WO-003
        {
            'id': 5,
            'order_id': 'WO-003',
            'op_seq': 1,
            'resource_code': 'MC-002',
            'start_dt': datetime(2026, 1, 10, 9, 0),  # MC-002 충돌
            'end_dt': datetime(2026, 1, 10, 10, 0),
            'duration_minutes': 60,
            'due_date': datetime(2026, 1, 14, 17, 0),
        },
    ]

    # Repair 실행
    repaired = repair_schedule_with_cpsat(
        scenario_id=1,
        schedule_rows=schedule_rows,
        use_cpsat=True,
        use_plant_calendar=False
    )

    # 결과 출력 (Resource별로 그룹핑)
    print("\n[Before Repair - By Resource]")
    for resource in ['MC-001', 'MC-002', 'MC-003']:
        print(f"\n  {resource}:")
        for row in sorted(schedule_rows, key=lambda x: x['start_dt']):
            if row['resource_code'] == resource:
                print(f"    {row['order_id']}-{row['op_seq']}: "
                      f"{row['start_dt'].strftime('%H:%M')} ~ {row['end_dt'].strftime('%H:%M')}")

    print("\n[After Repair - By Resource]")
    for resource in ['MC-001', 'MC-002', 'MC-003']:
        print(f"\n  {resource}:")
        for row in sorted(repaired, key=lambda x: x['start_dt']):
            if row['resource_code'] == resource:
                print(f"    {row['order_id']}-{row['op_seq']}: "
                      f"{row['start_dt'].strftime('%H:%M')} ~ {row['end_dt'].strftime('%H:%M')}")

    print("\n[OK] All constraints satisfied!\n")


def example_fallback():
    """
    Fallback 예제

    CP-SAT를 비활성화하고 시간 이동 방식 사용
    """
    print("=" * 80)
    print("Example 4: Fallback to Time-Shift Repair")
    print("=" * 80)

    schedule_rows = [
        {
            'id': 1,
            'order_id': 'WO-001',
            'op_seq': 1,
            'resource_code': 'MC-001',
            'start_dt': datetime(2026, 1, 10, 8, 0),
            'end_dt': datetime(2026, 1, 10, 9, 0),
            'duration_minutes': 60,
            'due_date': datetime(2026, 1, 15, 17, 0),
        },
        {
            'id': 2,
            'order_id': 'WO-002',
            'op_seq': 1,
            'resource_code': 'MC-001',
            'start_dt': datetime(2026, 1, 10, 8, 30),
            'end_dt': datetime(2026, 1, 10, 9, 30),
            'duration_minutes': 60,
            'due_date': datetime(2026, 1, 15, 17, 0),
        },
    ]

    # Fallback only (CP-SAT 비활성화)
    repaired = repair_schedule_with_cpsat(
        scenario_id=1,
        schedule_rows=schedule_rows,
        use_cpsat=False,  # Fallback만 사용
    )

    print("\n[After Fallback Repair]")
    for row in repaired:
        print(f"  {row['order_id']}-{row['op_seq']} @ {row['resource_code']}: "
              f"{row['start_dt'].strftime('%H:%M')} ~ {row['end_dt'].strftime('%H:%M')}")

    print("\n[OK] Simple time-shift repair completed!\n")


if __name__ == '__main__':
    """
    모든 예제 실행

    실행 방법:
        cd backend
        python -m apps.aps.services.or_repair.example_usage
    """
    example_basic_repair()
    example_precedence_repair()
    example_complex_scenario()
    example_fallback()

    print("=" * 80)
    print("All examples completed!")
    print("=" * 80)
