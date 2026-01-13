"""
CP-SAT Repair Engine 검증 테스트

Phase 1-3 기능 검증
"""
import sys
import os
from datetime import datetime, timedelta

# Django setup
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.aps.services.or_repair.runner import repair_schedule_with_cpsat


def test_phase1_resource_conflict():
    """Phase 1: Resource 충돌 해소 테스트"""
    print("\n" + "="*60)
    print("Test 1: Resource Conflict Resolution (Phase 1)")
    print("="*60)

    # Setup: 동일 설비에 동시 작업
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
            'start_dt': datetime(2026, 1, 10, 8, 30),  # ← 충돌!
            'end_dt': datetime(2026, 1, 10, 9, 30),
            'duration_minutes': 60,
            'due_date': datetime(2026, 1, 15, 17, 0),
        },
    ]

    print("\nBefore Repair:")
    for row in schedule_rows:
        print(f"  {row['order_id']} @ {row['resource_code']}: "
              f"{row['start_dt'].strftime('%H:%M')} ~ {row['end_dt'].strftime('%H:%M')}")

    # Execute
    try:
        repaired = repair_schedule_with_cpsat(
            scenario_id=1,
            schedule_rows=schedule_rows,
            use_cpsat=True,
            use_plant_calendar=False,  # Phase 1 only
            use_machine_constraints=False
        )

        print("\nAfter Repair:")
        for row in repaired:
            print(f"  {row['order_id']} @ {row['resource_code']}: "
                  f"{row['start_dt'].strftime('%H:%M')} ~ {row['end_dt'].strftime('%H:%M')}")

        # Verify: 충돌 해소 확인
        mc001_tasks = [r for r in repaired if r['resource_code'] == 'MC-001']
        mc001_tasks.sort(key=lambda x: x['start_dt'])

        conflict = False
        for i in range(len(mc001_tasks) - 1):
            if mc001_tasks[i]['end_dt'] > mc001_tasks[i+1]['start_dt']:
                conflict = True
                break

        if not conflict:
            print("\n[OK] Resource conflict resolved!")
            return True
        else:
            print("\n[FAIL] Conflict still exists!")
            return False

    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False


def test_phase1_precedence():
    """Phase 1: 공정 순서 준수 테스트"""
    print("\n" + "="*60)
    print("Test 2: Order Precedence (Phase 1)")
    print("="*60)

    # Setup: 역순으로 스케줄된 작업
    schedule_rows = [
        {
            'id': 2,
            'order_id': 'WO-001',
            'op_seq': 2,  # 2번째 공정
            'resource_code': 'MC-002',
            'start_dt': datetime(2026, 1, 10, 8, 0),  # ← 더 일찍 시작
            'end_dt': datetime(2026, 1, 10, 9, 30),
            'duration_minutes': 90,
            'due_date': datetime(2026, 1, 15, 17, 0),
        },
        {
            'id': 1,
            'order_id': 'WO-001',
            'op_seq': 1,  # 1번째 공정
            'resource_code': 'MC-001',
            'start_dt': datetime(2026, 1, 10, 9, 0),  # ← 더 늦게 시작 (역순!)
            'end_dt': datetime(2026, 1, 10, 10, 0),
            'duration_minutes': 60,
            'due_date': datetime(2026, 1, 15, 17, 0),
        },
    ]

    print("\nBefore Repair:")
    for row in sorted(schedule_rows, key=lambda x: x['op_seq']):
        print(f"  {row['order_id']}-{row['op_seq']} @ {row['resource_code']}: "
              f"{row['start_dt'].strftime('%H:%M')} ~ {row['end_dt'].strftime('%H:%M')}")

    # Execute
    try:
        repaired = repair_schedule_with_cpsat(
            scenario_id=1,
            schedule_rows=schedule_rows,
            use_cpsat=True,
            use_plant_calendar=False,
            use_machine_constraints=False
        )

        print("\nAfter Repair:")
        for row in sorted(repaired, key=lambda x: x['op_seq']):
            print(f"  {row['order_id']}-{row['op_seq']} @ {row['resource_code']}: "
                  f"{row['start_dt'].strftime('%H:%M')} ~ {row['end_dt'].strftime('%H:%M')}")

        # Verify: 순서 확인
        tasks = sorted(repaired, key=lambda x: x['op_seq'])
        if tasks[0]['end_dt'] <= tasks[1]['start_dt']:
            print("\n[OK] Precedence constraint enforced!")
            return True
        else:
            print("\n[FAIL] Precedence violated!")
            return False

    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False


def test_phase2_work_hours():
    """Phase 2: 근무시간 제약 테스트 (MVP 모드)"""
    print("\n" + "="*60)
    print("Test 3: Work Hours Constraint (Phase 2 MVP)")
    print("="*60)

    # Setup: 근무시간 외 작업
    schedule_rows = [
        {
            'id': 1,
            'order_id': 'WO-001',
            'op_seq': 1,
            'resource_code': 'MC-001',
            'start_dt': datetime(2026, 1, 10, 18, 0),  # ← 18:00 (근무시간 외!)
            'end_dt': datetime(2026, 1, 10, 19, 0),
            'duration_minutes': 60,
            'due_date': datetime(2026, 1, 15, 17, 0),
        },
    ]

    print("\nBefore Repair:")
    for row in schedule_rows:
        print(f"  {row['order_id']} @ {row['resource_code']}: "
              f"{row['start_dt'].strftime('%Y-%m-%d %H:%M')} ~ {row['end_dt'].strftime('%H:%M')}")

    # Execute
    try:
        repaired = repair_schedule_with_cpsat(
            scenario_id=1,
            schedule_rows=schedule_rows,
            use_cpsat=True,
            use_plant_calendar=False,  # MVP mode (08:00~17:00)
            use_machine_constraints=False
        )

        print("\nAfter Repair:")
        for row in repaired:
            print(f"  {row['order_id']} @ {row['resource_code']}: "
                  f"{row['start_dt'].strftime('%Y-%m-%d %H:%M')} ~ {row['end_dt'].strftime('%H:%M')}")

        # Verify: 08:00~17:00 내에 있는지 확인
        for row in repaired:
            start_hour = row['start_dt'].hour
            end_hour = row['end_dt'].hour

            if start_hour < 8 or (end_hour > 17 or (end_hour == 17 and row['end_dt'].minute > 0)):
                print(f"\n[FAIL] Task outside work hours: {row['start_dt']} ~ {row['end_dt']}")
                return False

        print("\n[OK] All tasks within work hours (08:00~17:00)!")
        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False


def test_complex_scenario():
    """복합 시나리오 테스트"""
    print("\n" + "="*60)
    print("Test 4: Complex Scenario (Multiple Resources)")
    print("="*60)

    # Setup: 3개 설비, 5개 작업
    schedule_rows = [
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
            'start_dt': datetime(2026, 1, 10, 8, 30),
            'end_dt': datetime(2026, 1, 10, 10, 0),
            'duration_minutes': 90,
            'due_date': datetime(2026, 1, 12, 17, 0),
        },
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
            'order_id': 'WO-003',
            'op_seq': 1,
            'resource_code': 'MC-003',
            'start_dt': datetime(2026, 1, 10, 8, 0),
            'end_dt': datetime(2026, 1, 10, 10, 0),
            'duration_minutes': 120,
            'due_date': datetime(2026, 1, 14, 17, 0),
        },
        {
            'id': 5,
            'order_id': 'WO-002',
            'op_seq': 2,
            'resource_code': 'MC-002',
            'start_dt': datetime(2026, 1, 10, 9, 0),  # Precedence 위반
            'end_dt': datetime(2026, 1, 10, 10, 30),
            'duration_minutes': 90,
            'due_date': datetime(2026, 1, 13, 17, 0),
        },
    ]

    print("\nBefore Repair:")
    for row in schedule_rows:
        print(f"  {row['order_id']}-{row['op_seq']} @ {row['resource_code']}: "
              f"{row['start_dt'].strftime('%H:%M')} ~ {row['end_dt'].strftime('%H:%M')}")

    # Execute
    try:
        repaired = repair_schedule_with_cpsat(
            scenario_id=1,
            schedule_rows=schedule_rows,
            use_cpsat=True,
            use_plant_calendar=False,
            use_machine_constraints=False
        )

        print("\nAfter Repair:")
        for row in sorted(repaired, key=lambda x: (x['order_id'], x['op_seq'])):
            print(f"  {row['order_id']}-{row['op_seq']} @ {row['resource_code']}: "
                  f"{row['start_dt'].strftime('%H:%M')} ~ {row['end_dt'].strftime('%H:%M')}")

        # Verify
        errors = []

        # 1. Resource conflict check
        for mc in ['MC-001', 'MC-002', 'MC-003']:
            mc_tasks = sorted(
                [r for r in repaired if r['resource_code'] == mc],
                key=lambda x: x['start_dt']
            )
            for i in range(len(mc_tasks) - 1):
                if mc_tasks[i]['end_dt'] > mc_tasks[i+1]['start_dt']:
                    errors.append(f"Resource conflict on {mc}")

        # 2. Precedence check
        for order_id in ['WO-001', 'WO-002']:
            order_tasks = sorted(
                [r for r in repaired if r['order_id'] == order_id],
                key=lambda x: x['op_seq']
            )
            for i in range(len(order_tasks) - 1):
                if order_tasks[i]['end_dt'] > order_tasks[i+1]['start_dt']:
                    errors.append(f"Precedence violation in {order_id}")

        # 3. Work hours check
        for row in repaired:
            if row['start_dt'].hour < 8 or row['end_dt'].hour > 17:
                errors.append(f"Outside work hours: {row['order_id']}")

        if not errors:
            print("\n[OK] Complex scenario solved successfully!")
            return True
        else:
            print("\n[FAIL] Errors found:")
            for err in errors:
                print(f"  - {err}")
            return False

    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "="*60)
    print("CP-SAT Repair Engine - Verification Tests")
    print("="*60)
    print("\nRunning Phase 1-3 tests...\n")

    results = {
        'Phase 1 - Resource Conflict': test_phase1_resource_conflict(),
        'Phase 1 - Precedence': test_phase1_precedence(),
        'Phase 2 - Work Hours': test_phase2_work_hours(),
        'Complex Scenario': test_complex_scenario(),
    }

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")

    print(f"\nTotal: {passed}/{total} passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed! Ready for production.")
        return True
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Please review.")
        return False


if __name__ == "__main__":
    # Run tests
    success = run_all_tests()
    sys.exit(0 if success else 1)
