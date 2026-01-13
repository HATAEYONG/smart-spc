"""
STEP 3: UnplannedReason 간단 테스트

Django shell에서 실행:
python manage.py shell < apps/aps/services/test_unplanned_simple.py
"""

from datetime import datetime, timedelta
from django.utils import timezone
from apps.core.models import StageFactPlanOut
from apps.aps.scenario_models import Scenario, ScenarioResult
from apps.aps.analytics_models import UnplannedReason
from apps.aps.services.analytics import UnplannedClassifier


def run_test():
    print("\n" + "="*60)
    print("STEP 3: UnplannedReason Quick Test")
    print("="*60)

    # 1. 테스트 시나리오 생성
    print("\n[1] Creating test scenario...")
    Scenario.objects.filter(name__startswith='TEST_UNPLANNED').delete()

    scenario = Scenario.objects.create(
        name='TEST_UNPLANNED_QUICK',
        description='Quick test',
        base_plan_date=timezone.now(),
        algorithm='GA',
        status='DRAFT'
    )
    print(f"    Created scenario: {scenario.scenario_id}")

    # 2. 테스트 주문 생성
    print("\n[2] Creating test orders...")
    StageFactPlanOut.objects.filter(wo_no__startswith='WO-QUICK').delete()

    base_time = timezone.now()
    orders = [
        StageFactPlanOut(
            wo_no='WO-QUICK-001',
            mc_cd='MC-001',
            itm_id='ITEM-001',
            plan_qty=100,
            fr_ts=base_time + timedelta(hours=1),
            to_ts=base_time + timedelta(hours=3),
        ),
        StageFactPlanOut(
            wo_no='WO-QUICK-002',
            mc_cd='',  # DATA_MISSING
            itm_id='ITEM-002',
            plan_qty=50,
            fr_ts=base_time + timedelta(hours=2),
            to_ts=base_time + timedelta(hours=4),
        ),
        StageFactPlanOut(
            wo_no='WO-QUICK-003',
            mc_cd='MC-003',
            itm_id='ITEM-003',
            plan_qty=75,
            fr_ts=base_time + timedelta(hours=1),
            to_ts=base_time + timedelta(hours=2),  # 짧은 납기 (지연 가능성)
        ),
    ]
    StageFactPlanOut.objects.bulk_create(orders)
    print(f"    Created {len(orders)} orders")

    # 3. 스케줄 결과 생성
    print("\n[3] Creating schedule result...")
    schedule_rows = [
        {
            'wo_no': 'WO-QUICK-001',
            'mc_cd': 'MC-001',
            'fr_ts': base_time + timedelta(hours=1),
            'to_ts': base_time + timedelta(hours=3),
        },
        {
            'wo_no': 'WO-QUICK-003',
            'mc_cd': 'MC-003',
            'fr_ts': base_time + timedelta(hours=1),
            'to_ts': base_time + timedelta(hours=3),  # 지연 (to_ts > 원래 납기)
        },
    ]

    result = ScenarioResult.objects.create(
        scenario=scenario,
        makespan=120,
        total_tardiness=60,
        max_tardiness=60,
        avg_utilization=75.0,
        total_cost=1000.0,
        total_jobs=3,
        completed_jobs=2,
        tardy_jobs=1,
        total_machines=3,
        avg_machine_utilization=70.0,
        bottleneck_machines=['MC-001'],
        schedule=schedule_rows,
        execution_time=1.5,
    )
    print(f"    Created ScenarioResult: {result.result_id}")

    # 4. 분류기 실행
    print("\n[4] Running UnplannedClassifier...")
    classifier = UnplannedClassifier(scenario_id=scenario.scenario_id)
    reasons = classifier.analyze(
        schedule_rows=result.schedule,
        orders=orders
    )

    print(f"    Created {len(reasons)} UnplannedReason records")

    # 5. 결과 출력
    print("\n[5] Results:")
    for r in reasons:
        print(f"\n    {r.wo_no}:")
        print(f"      Reason: {r.get_reason_code_display()}")
        print(f"      Status: {r.get_status_display()}")
        print(f"      Confidence: {r.confidence:.2f}")
        print(f"      Delay: {r.delay_hours:.1f} hours")
        print(f"      Explanation: {r.explanation}")

    # 6. 검증
    print("\n[6] Validation:")
    wo002 = next((r for r in reasons if r.wo_no == 'WO-QUICK-002'), None)
    if wo002 and wo002.reason_code == 'DATA_MISSING':
        print("    [PASS] WO-QUICK-002: DATA_MISSING")
    else:
        print(f"    [FAIL] WO-QUICK-002: Expected DATA_MISSING, got {wo002.reason_code if wo002 else 'None'}")

    wo003 = next((r for r in reasons if r.wo_no == 'WO-QUICK-003'), None)
    if wo003 and wo003.status == 'DELAYED':
        print(f"    [PASS] WO-QUICK-003: DELAYED (reason={wo003.reason_code})")
    else:
        print(f"    [FAIL] WO-QUICK-003: Expected DELAYED status, got {wo003.status if wo003 else 'None'}")

    print("\n[SUCCESS] Test completed!")
    print(f"\nCheck admin: http://localhost:8000/admin/aps/unplannedreason/")


if __name__ == '__main__':
    run_test()
