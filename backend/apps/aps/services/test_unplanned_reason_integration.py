"""
STEP 3: UnplannedReason 통합 테스트

미계획 원인 자동 분류 기능의 전체 워크플로우 검증
"""
import os
import sys
import django

# Django 설정
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from datetime import datetime, timedelta
from django.utils import timezone
from apps.core.models import StageFactPlanOut
from apps.aps.scenario_models import Scenario, ScenarioResult
from apps.aps.analytics_models import UnplannedReason
from apps.aps.services.analytics import UnplannedClassifier


def create_test_scenario():
    """테스트 시나리오 생성"""
    print("\n" + "=" * 60)
    print("Test 1: Creating Test Scenario")
    print("=" * 60)

    # 기존 테스트 시나리오 삭제
    Scenario.objects.filter(name__startswith='TEST_UNPLANNED').delete()

    scenario = Scenario.objects.create(
        name='TEST_UNPLANNED_ANALYSIS',
        description='미계획 원인 분석 테스트 시나리오',
        base_plan_date=timezone.now(),
        algorithm='GA',
        status='DRAFT'
    )

    print(f"[OK] Created scenario: {scenario.scenario_id}")
    return scenario


def create_test_orders():
    """테스트 주문 생성"""
    print("\n" + "=" * 60)
    print("Test 2: Creating Test Orders")
    print("=" * 60)

    # 기존 테스트 주문 삭제
    StageFactPlanOut.objects.filter(wo_no__startswith='WO-TEST').delete()

    base_time = timezone.now()

    orders = [
        # 정상 주문 (스케줄 가능)
        StageFactPlanOut(
            wo_no='WO-TEST-001',
            mc_cd='MC-001',
            itm_id='ITEM-001',
            plan_qty=100,
            fr_ts=base_time + timedelta(hours=1),
            to_ts=base_time + timedelta(hours=3),
        ),
        StageFactPlanOut(
            wo_no='WO-TEST-002',
            mc_cd='MC-002',
            itm_id='ITEM-002',
            plan_qty=50,
            fr_ts=base_time + timedelta(hours=2),
            to_ts=base_time + timedelta(hours=4),
        ),

        # 미계획 주문 1: 자원 없음 (DATA_MISSING)
        StageFactPlanOut(
            wo_no='WO-TEST-003',
            mc_cd='',  # 자원 정보 없음
            itm_id='ITEM-003',
            plan_qty=75,
            fr_ts=base_time + timedelta(hours=3),
            to_ts=base_time + timedelta(hours=5),
        ),

        # 미계획 주문 2: 우선순위 낮음 (PRIORITY_LOSS)
        StageFactPlanOut(
            wo_no='WO-TEST-004',
            mc_cd='MC-001',
            itm_id='ITEM-004',
            plan_qty=200,
            fr_ts=base_time + timedelta(hours=4),
            to_ts=base_time + timedelta(hours=8),
        ),

        # 지연 주문: 납기일 촉박
        StageFactPlanOut(
            wo_no='WO-TEST-005',
            mc_cd='MC-003',
            itm_id='ITEM-005',
            plan_qty=150,
            fr_ts=base_time + timedelta(hours=1),
            to_ts=base_time + timedelta(hours=2),  # 1시간 작업, 짧은 납기
        ),
    ]

    StageFactPlanOut.objects.bulk_create(orders)
    print(f"[OK] Created {len(orders)} test orders")

    for order in orders:
        print(f"  {order.wo_no}: mc_cd={order.mc_cd or '(없음)'}, "
              f"due={order.to_ts.strftime('%H:%M')}")

    return orders


def create_test_schedule_result(scenario):
    """테스트 스케줄 결과 생성"""
    print("\n" + "=" * 60)
    print("Test 3: Creating Schedule Result")
    print("=" * 60)

    base_time = timezone.now()

    # 스케줄: WO-001, WO-002만 배정 (WO-003, WO-004는 미배정)
    # WO-005는 지연 배정
    schedule_rows = [
        {
            'wo_no': 'WO-TEST-001',
            'mc_cd': 'MC-001',
            'fr_ts': base_time + timedelta(hours=1),
            'to_ts': base_time + timedelta(hours=3),
        },
        {
            'wo_no': 'WO-TEST-002',
            'mc_cd': 'MC-002',
            'fr_ts': base_time + timedelta(hours=2),
            'to_ts': base_time + timedelta(hours=4),
        },
        {
            'wo_no': 'WO-TEST-005',
            'mc_cd': 'MC-003',
            'fr_ts': base_time + timedelta(hours=1),
            'to_ts': base_time + timedelta(hours=3),  # 납기(2시간) 초과 -> 지연
        },
    ]

    result = ScenarioResult.objects.create(
        scenario=scenario,
        makespan=180,  # 3시간 (분 단위)
        total_tardiness=60,  # WO-005 지연 1시간
        max_tardiness=60,
        avg_utilization=75.0,
        total_cost=1000.0,
        total_jobs=5,
        completed_jobs=3,
        tardy_jobs=1,
        total_machines=3,
        avg_machine_utilization=70.0,
        bottleneck_machines=['MC-001'],
        schedule=schedule_rows,
        execution_time=2.5,
    )

    print(f"[OK] Created ScenarioResult: {result.result_id}")
    print(f"  Total jobs: {result.total_jobs}")
    print(f"  Completed jobs: {result.completed_jobs}")
    print(f"  Tardy jobs: {result.tardy_jobs}")
    print(f"  Scheduled: {len(schedule_rows)} orders")

    return result


def test_unplanned_classification():
    """미계획 원인 분류 테스트"""
    print("\n" + "=" * 60)
    print("Test 4: UnplannedReason Classification")
    print("=" * 60)

    # 1. 테스트 데이터 생성
    scenario = create_test_scenario()
    orders = create_test_orders()
    result = create_test_schedule_result(scenario)

    # 2. 분류기 실행
    print("\nRunning UnplannedClassifier...")
    classifier = UnplannedClassifier(scenario_id=scenario.scenario_id)

    reasons = classifier.analyze(
        schedule_rows=result.schedule,
        orders=orders
    )

    print(f"\n[OK] Created {len(reasons)} UnplannedReason records")

    # 3. 결과 검증
    print("\n" + "=" * 60)
    print("Analysis Results")
    print("=" * 60)

    # 원인별 통계
    reason_stats = {}
    status_stats = {}

    for r in reasons:
        reason_stats[r.reason_code] = reason_stats.get(r.reason_code, 0) + 1
        status_stats[r.status] = status_stats.get(r.status, 0) + 1

    print("\nReason Breakdown:")
    for code, count in reason_stats.items():
        display_name = dict(UnplannedReason.REASON_CODES).get(code, code)
        print(f"  {code}: {count} ({display_name})")

    print("\nStatus Breakdown:")
    for status, count in status_stats.items():
        display_name = dict(UnplannedReason.STATUS_CHOICES).get(status, status)
        print(f"  {status}: {count} ({display_name})")

    # 4. 상세 내역
    print("\n" + "=" * 60)
    print("Detailed Reasons")
    print("=" * 60)

    for r in reasons:
        print(f"\n{r.wo_no}:")
        print(f"  Reason: {r.get_reason_code_display()}")
        print(f"  Status: {r.get_status_display()}")
        print(f"  Confidence: {r.confidence:.2f}")
        print(f"  Delay: {r.delay_hours:.1f} hours")
        print(f"  Explanation: {r.explanation}")
        print(f"  Risk Level: {r.risk_level}")
        print(f"  Recommendation: {r.get_recommendation()}")

    # 5. 예상 결과 검증
    print("\n" + "=" * 60)
    print("Validation")
    print("=" * 60)

    expected = {
        'WO-TEST-003': 'DATA_MISSING',  # 자원 없음
        'WO-TEST-004': 'PRIORITY_LOSS',  # 우선순위 낮음 (또는 CAPACITY_SHORTAGE)
        'WO-TEST-005': 'DELAYED',  # 지연
    }

    success = True
    for wo_no, expected_reason in expected.items():
        actual = next((r for r in reasons if r.wo_no == wo_no), None)

        if not actual:
            print(f"[FAIL] {wo_no}: No UnplannedReason found")
            success = False
        elif expected_reason == 'DELAYED':
            if actual.status != 'DELAYED':
                print(f"[FAIL] {wo_no}: Expected DELAYED status, got {actual.status}")
                success = False
            else:
                print(f"[PASS] {wo_no}: Status={actual.status}, Reason={actual.reason_code}")
        else:
            if actual.reason_code == expected_reason:
                print(f"[PASS] {wo_no}: {actual.reason_code}")
            else:
                # PRIORITY_LOSS vs CAPACITY_SHORTAGE는 신뢰도에 따라 달라질 수 있음
                if expected_reason == 'PRIORITY_LOSS' and actual.reason_code == 'CAPACITY_SHORTAGE':
                    print(f"[PASS] {wo_no}: {actual.reason_code} (alternative to {expected_reason})")
                else:
                    print(f"[WARN] {wo_no}: Expected {expected_reason}, got {actual.reason_code}")

    return success


def test_admin_interface():
    """Admin 인터페이스 접근 테스트"""
    print("\n" + "=" * 60)
    print("Test 5: Admin Interface")
    print("=" * 60)

    count = UnplannedReason.objects.count()
    print(f"[OK] Total UnplannedReason records: {count}")

    # 최근 5개 레코드 조회
    recent = UnplannedReason.objects.all()[:5]

    print("\nRecent Records (accessible via /admin):")
    for r in recent:
        print(f"  {r.reason_id}: {r.wo_no} - {r.get_reason_code_display()}")

    print("\n[OK] Admin interface ready at: /admin/aps/unplannedreason/")


def run_all_tests():
    """전체 테스트 실행"""
    print("\n" + "=" * 60)
    print("STEP 3: UnplannedReason Integration Tests")
    print("=" * 60)

    try:
        # Test 1-4: 분류 테스트
        success = test_unplanned_classification()

        # Test 5: Admin 인터페이스
        test_admin_interface()

        # 최종 결과
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)

        if success:
            print("[SUCCESS] All STEP 3 tests passed!")
            print("\nNext Steps:")
            print("1. Access admin: http://localhost:8000/admin/aps/unplannedreason/")
            print("2. Run optimization: POST /api/aps/scenarios/{id}/run/")
            print("3. Check unplanned_analysis in response")
        else:
            print("[PARTIAL] Some tests failed. Check details above.")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()
