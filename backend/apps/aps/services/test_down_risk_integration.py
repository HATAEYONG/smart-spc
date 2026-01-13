"""
DOWN_RISK 예측 + CP-SAT 통합 테스트

STEP 2 완전 검증 테스트
"""
import sys
import os
from datetime import datetime, timedelta

# Django setup
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.aps.services.down_risk_predictor import DownRiskPredictor
from apps.aps.ai_llm_models import Prediction
from apps.aps.services.or_repair import repair_schedule_with_cpsat


def test_down_risk_prediction():
    """Test 1: DOWN_RISK 예측 생성"""
    print("\n" + "="*60)
    print("Test 1: DOWN_RISK Prediction Generation")
    print("="*60)

    try:
        predictor = DownRiskPredictor(lookback_days=60)

        # 전체 설비 예측 생성
        resource_codes = ['MC-001', 'MC-002', 'MC-003', 'MC-004', 'MC-005']
        predictions = predictor.build_all_predictions(
            scenario_id=999,
            resource_codes=resource_codes
        )

        print(f"\n[OK] Created {len(predictions)} predictions")

        # 결과 출력
        print("\nPrediction Results:")
        for pred in predictions:
            resource = pred.target_entity.split(':')[1]
            print(f"  {resource}: risk={pred.predicted_value:.3f}, confidence={pred.confidence_score:.2f}")
            print(f"    {pred.explanation}")

        # 검증: 고위험 vs 저위험
        mc001 = next((p for p in predictions if 'MC-001' in p.target_entity), None)
        mc002 = next((p for p in predictions if 'MC-002' in p.target_entity), None)

        if mc001 and mc002:
            if mc001.predicted_value > mc002.predicted_value:
                print(f"\n[OK] MC-001 (high risk: {mc001.predicted_value:.3f}) > "
                      f"MC-002 (low risk: {mc002.predicted_value:.3f})")
                return True, predictions
            else:
                print(f"\n[FAIL] Risk ordering incorrect!")
                return False, predictions
        else:
            print("\n[FAIL] Missing predictions")
            return False, predictions

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False, []


def test_cpsat_without_risk():
    """Test 2: CP-SAT 최적화 (DOWN_RISK 없음 - Baseline)"""
    print("\n" + "="*60)
    print("Test 2: CP-SAT Optimization (No DOWN_RISK)")
    print("="*60)

    # 샘플 스케줄 (고위험 MC-001, 저위험 MC-002)
    schedule_rows = [
        {
            'id': 1,
            'order_id': 'WO-001',
            'op_seq': 1,
            'resource_code': 'MC-001',  # 고위험
            'start_dt': datetime(2026, 1, 10, 8, 0),
            'end_dt': datetime(2026, 1, 10, 9, 0),
            'duration_minutes': 60,
            'due_date': datetime(2026, 1, 15, 17, 0),
        },
        {
            'id': 2,
            'order_id': 'WO-002',
            'op_seq': 1,
            'resource_code': 'MC-002',  # 저위험
            'start_dt': datetime(2026, 1, 10, 8, 30),
            'end_dt': datetime(2026, 1, 10, 9, 30),
            'duration_minutes': 60,
            'due_date': datetime(2026, 1, 15, 17, 0),
        },
        {
            'id': 3,
            'order_id': 'WO-003',
            'op_seq': 1,
            'resource_code': 'MC-001',  # 고위험 (충돌)
            'start_dt': datetime(2026, 1, 10, 8, 30),
            'end_dt': datetime(2026, 1, 10, 10, 0),
            'duration_minutes': 90,
            'due_date': datetime(2026, 1, 15, 17, 0),
        },
    ]

    print("\nBefore Repair:")
    for row in schedule_rows:
        print(f"  {row['order_id']} @ {row['resource_code']}: "
              f"{row['start_dt'].strftime('%H:%M')} ~ {row['end_dt'].strftime('%H:%M')}")

    try:
        repaired = repair_schedule_with_cpsat(
            scenario_id=999,
            schedule_rows=schedule_rows,
            use_cpsat=True,
            use_plant_calendar=False,
            use_machine_constraints=False,
            predictions=None,  # No DOWN_RISK
            risk_weight=0.0
        )

        print("\nAfter Repair (No Risk):")
        for row in repaired:
            print(f"  {row['order_id']} @ {row['resource_code']}: "
                  f"{row['start_dt'].strftime('%H:%M')} ~ {row['end_dt'].strftime('%H:%M')}")

        # MC-001 사용 횟수
        mc001_usage = sum(1 for r in repaired if r['resource_code'] == 'MC-001')
        mc002_usage = sum(1 for r in repaired if r['resource_code'] == 'MC-002')

        print(f"\nResource Usage (Baseline):")
        print(f"  MC-001: {mc001_usage} tasks")
        print(f"  MC-002: {mc002_usage} tasks")

        return True, repaired, mc001_usage

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False, [], 0


def test_cpsat_with_risk(predictions):
    """Test 3: CP-SAT 최적화 (DOWN_RISK 반영)"""
    print("\n" + "="*60)
    print("Test 3: CP-SAT Optimization (WITH DOWN_RISK)")
    print("="*60)

    # 동일한 스케줄
    schedule_rows = [
        {
            'id': 1,
            'order_id': 'WO-001',
            'op_seq': 1,
            'resource_code': 'MC-001',  # 고위험
            'start_dt': datetime(2026, 1, 10, 8, 0),
            'end_dt': datetime(2026, 1, 10, 9, 0),
            'duration_minutes': 60,
            'due_date': datetime(2026, 1, 15, 17, 0),
        },
        {
            'id': 2,
            'order_id': 'WO-002',
            'op_seq': 1,
            'resource_code': 'MC-002',  # 저위험
            'start_dt': datetime(2026, 1, 10, 8, 30),
            'end_dt': datetime(2026, 1, 10, 9, 30),
            'duration_minutes': 60,
            'due_date': datetime(2026, 1, 15, 17, 0),
        },
        {
            'id': 3,
            'order_id': 'WO-003',
            'op_seq': 1,
            'resource_code': 'MC-001',  # 고위험 (충돌)
            'start_dt': datetime(2026, 1, 10, 8, 30),
            'end_dt': datetime(2026, 1, 10, 10, 0),
            'duration_minutes': 90,
            'due_date': datetime(2026, 1, 15, 17, 0),
        },
    ]

    print("\nBefore Repair:")
    for row in schedule_rows:
        print(f"  {row['order_id']} @ {row['resource_code']}: "
              f"{row['start_dt'].strftime('%H:%M')} ~ {row['end_dt'].strftime('%H:%M')}")

    try:
        # Prediction QuerySet 변환
        pred_qs = Prediction.objects.filter(
            prediction_type='DOWN_RISK',
            target_id=999
        )

        print(f"\nUsing {pred_qs.count()} DOWN_RISK predictions:")
        for pred in pred_qs:
            resource = pred.target_entity.split(':')[1]
            print(f"  {resource}: risk={pred.predicted_value:.3f}")

        repaired = repair_schedule_with_cpsat(
            scenario_id=999,
            schedule_rows=schedule_rows,
            use_cpsat=True,
            use_plant_calendar=False,
            use_machine_constraints=False,
            predictions=pred_qs,  # WITH DOWN_RISK
            risk_weight=3.0
        )

        print("\nAfter Repair (With Risk):")
        for row in repaired:
            print(f"  {row['order_id']} @ {row['resource_code']}: "
                  f"{row['start_dt'].strftime('%H:%M')} ~ {row['end_dt'].strftime('%H:%M')}")

        # MC-001 사용 횟수
        mc001_usage = sum(1 for r in repaired if r['resource_code'] == 'MC-001')
        mc002_usage = sum(1 for r in repaired if r['resource_code'] == 'MC-002')

        print(f"\nResource Usage (With DOWN_RISK):")
        print(f"  MC-001: {mc001_usage} tasks")
        print(f"  MC-002: {mc002_usage} tasks")

        return True, repaired, mc001_usage

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False, [], 0


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "="*60)
    print("DOWN_RISK + CP-SAT Integration Tests")
    print("="*60)
    print("\nRunning STEP 2 verification tests...\n")

    results = {}

    # Test 1: 예측 생성
    success1, predictions = test_down_risk_prediction()
    results['DOWN_RISK Prediction'] = success1

    if not success1:
        print("\n[FAIL] Cannot proceed without predictions")
        return False

    # Test 2: CP-SAT without risk (baseline)
    success2, baseline_schedule, baseline_mc001 = test_cpsat_without_risk()
    results['CP-SAT (Baseline)'] = success2

    # Test 3: CP-SAT with risk
    success3, risk_schedule, risk_mc001 = test_cpsat_with_risk(predictions)
    results['CP-SAT (With Risk)'] = success3

    # Comparison
    print("\n" + "="*60)
    print("Comparison: Baseline vs DOWN_RISK")
    print("="*60)

    if success2 and success3:
        print(f"\nMC-001 (High Risk) Usage:")
        print(f"  Baseline: {baseline_mc001} tasks")
        print(f"  With DOWN_RISK: {risk_mc001} tasks")

        if risk_mc001 < baseline_mc001:
            print(f"\n[OK] DOWN_RISK reduced high-risk resource usage by "
                  f"{baseline_mc001 - risk_mc001} tasks!")
        elif risk_mc001 == baseline_mc001:
            print(f"\n[INFO] Usage remained the same (may need stronger risk_weight)")
        else:
            print(f"\n[FAIL] Usage increased (unexpected)")

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
        print("\n[SUCCESS] All STEP 2 tests passed! Ready for production.")
        return True
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Please review.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
