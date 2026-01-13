"""
OperationActual 샘플 데이터 생성 스크립트

DOWN_RISK 예측 테스트를 위한 시뮬레이션 데이터 생성
"""
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import random
import numpy as np

# Django setup
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.utils import timezone
from apps.aps.execution_models import OperationActual, ExecutionEvent
from apps.erp.models import MasterMachine


def create_operation_actuals(
    days=60,
    operations_per_day=10,
    resource_codes=None
):
    """
    OperationActual 샘플 데이터 생성

    Args:
        days: 생성할 기간 (기본 60일)
        operations_per_day: 일일 작업 수 (기본 10개)
        resource_codes: 설비 코드 리스트 (None이면 기본 설비 사용)

    Returns:
        int: 생성된 레코드 수
    """
    print("\n" + "="*60)
    print("Creating OperationActual Sample Data")
    print("="*60)

    if resource_codes is None:
        # 기본 설비 코드 (고위험/중위험/저위험)
        resource_codes = [
            'MC-001',  # 고위험: 노후 설비
            'MC-002',  # 저위험: 신규 설비
            'MC-003',  # 중위험: 보통 설비
            'MC-004',  # 고위험: 문제 많은 설비
            'MC-005',  # 저위험: 안정적 설비
        ]

    # 설비별 특성 정의
    machine_profiles = {
        'MC-001': {  # 고위험 설비
            'base_proc_time': 60,  # 기본 60분
            'variability': 0.5,     # 50% 변동성 (높음)
            'abnormal_rate': 0.25,  # 25% 비정상 작업
            'down_event_rate': 0.15 # 15% Down 이벤트
        },
        'MC-002': {  # 저위험 설비
            'base_proc_time': 60,
            'variability': 0.1,     # 10% 변동성 (낮음)
            'abnormal_rate': 0.05,  # 5% 비정상 작업
            'down_event_rate': 0.02 # 2% Down 이벤트
        },
        'MC-003': {  # 중위험 설비
            'base_proc_time': 60,
            'variability': 0.25,    # 25% 변동성
            'abnormal_rate': 0.12,  # 12% 비정상 작업
            'down_event_rate': 0.07 # 7% Down 이벤트
        },
        'MC-004': {  # 고위험 설비
            'base_proc_time': 60,
            'variability': 0.6,     # 60% 변동성 (매우 높음)
            'abnormal_rate': 0.30,  # 30% 비정상 작업
            'down_event_rate': 0.20 # 20% Down 이벤트
        },
        'MC-005': {  # 저위험 설비
            'base_proc_time': 60,
            'variability': 0.08,    # 8% 변동성
            'abnormal_rate': 0.03,  # 3% 비정상 작업
            'down_event_rate': 0.01 # 1% Down 이벤트
        },
    }

    # 기존 데이터 삭제 (테스트용)
    OperationActual.objects.all().delete()
    ExecutionEvent.objects.all().delete()
    print(f"Cleared existing data")

    start_date = timezone.now() - timedelta(days=days)
    created_count = 0
    event_count = 0

    # 날짜별, 설비별로 데이터 생성
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)

        for resource_code in resource_codes:
            if resource_code not in machine_profiles:
                continue

            profile = machine_profiles[resource_code]

            # 하루 작업 수 (정규 분포)
            daily_ops = max(5, int(np.random.normal(operations_per_day, 2)))

            for op_idx in range(daily_ops):
                # 작업 시작 시간 (08:00 ~ 16:00 사이 랜덤)
                hour = random.randint(8, 16)
                minute = random.randint(0, 59)
                planned_start = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

                # 계획 작업 시간 (기본값 + 약간의 변동)
                base_time = profile['base_proc_time']
                planned_duration = int(np.random.normal(base_time, base_time * 0.1))
                planned_duration = max(30, min(120, planned_duration))  # 30~120분

                planned_end = planned_start + timedelta(minutes=planned_duration)

                # 실제 작업 시간 생성
                is_abnormal = random.random() < profile['abnormal_rate']

                if is_abnormal:
                    # 비정상 작업: 계획 대비 크게 지연 (1.5 ~ 3배)
                    actual_duration = int(planned_duration * random.uniform(1.5, 3.0))
                else:
                    # 정상 작업: 변동성 범위 내
                    variance = planned_duration * profile['variability']
                    actual_duration = int(np.random.normal(planned_duration, variance))
                    actual_duration = max(planned_duration * 0.8, min(planned_duration * 1.3, actual_duration))

                actual_start = planned_start + timedelta(minutes=random.randint(-5, 15))
                actual_end = actual_start + timedelta(minutes=actual_duration)
                proc_time_hr = actual_duration / 60.0

                # 수량 (양품 + 불량)
                target_qty = Decimal('100')
                if is_abnormal:
                    good_qty = Decimal(str(random.uniform(60, 90)))
                    defect_qty = target_qty - good_qty
                else:
                    good_qty = Decimal(str(random.uniform(95, 100)))
                    defect_qty = target_qty - good_qty

                # WO 번호 생성
                wo_no = f"WO-{current_date.strftime('%Y%m%d')}-{resource_code}-{op_idx+1:03d}"

                # OperationActual 생성
                op_actual = OperationActual.objects.create(
                    wo_no=wo_no,
                    op_seq=1,
                    operation_nm=f"작업-{op_idx+1}",
                    resource_code=resource_code,
                    planned_start_dt=planned_start,
                    planned_end_dt=planned_end,
                    planned_duration_minutes=planned_duration,
                    actual_start_dt=actual_start,
                    actual_end_dt=actual_end,
                    actual_duration_minutes=actual_duration,
                    proc_time_hr=proc_time_hr,
                    planned_qty=target_qty,
                    actual_qty=target_qty,
                    good_qty=good_qty,
                    defect_qty=defect_qty,
                    status='COMPLETED',
                    is_abnormal=is_abnormal,
                    delay_minutes=actual_duration - planned_duration,
                    delay_reason='설비 지연' if is_abnormal else None
                )

                created_count += 1

                # Down 이벤트 생성 (확률 기반)
                if random.random() < profile['down_event_rate']:
                    down_types = [
                        'DOWN_BREAKDOWN',
                        'DOWN_MAINTENANCE',
                        'DOWN_MATERIAL',
                        'DOWN_QUALITY'
                    ]
                    event_type = random.choice(down_types)

                    # Down 시간 (작업 중간에 발생)
                    actual_dur_int = int(actual_duration)
                    if actual_dur_int > 30:
                        down_start = actual_start + timedelta(minutes=random.randint(10, actual_dur_int-20))
                        down_duration = random.randint(15, 60)
                        down_end = down_start + timedelta(minutes=down_duration)
                    else:
                        # 작업이 짧으면 Down 이벤트 생략
                        continue

                    ExecutionEvent.objects.create(
                        event_type=event_type,
                        resource_code=resource_code,
                        start_dt=down_start,
                        end_dt=down_end,
                        duration_minutes=down_duration,
                        operation_actual=op_actual,
                        wo_no=wo_no,
                        reason='시뮬레이션 Down 이벤트',
                        severity='HIGH' if down_duration > 30 else 'MEDIUM',
                        is_resolved=True
                    )

                    event_count += 1

    print(f"\n[OK] Created {created_count} OperationActual records")
    print(f"[OK] Created {event_count} ExecutionEvent records")

    # 통계 출력
    print("\n" + "="*60)
    print("Statistics by Resource")
    print("="*60)

    for resource_code in resource_codes:
        ops = OperationActual.objects.filter(resource_code=resource_code)
        if not ops.exists():
            continue

        total = ops.count()
        abnormal = ops.filter(is_abnormal=True).count()
        avg_proc = ops.aggregate(avg=django.db.models.Avg('proc_time_hr'))['avg']
        events = ExecutionEvent.objects.filter(resource_code=resource_code).count()

        print(f"\n{resource_code}:")
        print(f"  Total ops: {total}")
        print(f"  Abnormal: {abnormal} ({abnormal/total*100:.1f}%)")
        print(f"  Avg proc time: {avg_proc:.2f} hrs")
        print(f"  Down events: {events}")

    return created_count


def run_all():
    """전체 샘플 데이터 생성"""
    print("\n" + "="*60)
    print("OperationActual Sample Data Generation")
    print("="*60)

    try:
        count = create_operation_actuals(
            days=60,
            operations_per_day=10
        )

        print("\n" + "="*60)
        print("Summary")
        print("="*60)
        print(f"Total records created: {count}")
        print("\n[SUCCESS] Sample data generation completed!")

        return True

    except Exception as e:
        print(f"\n[ERROR] Failed to create sample data: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import django.db.models
    success = run_all()
    sys.exit(0 if success else 1)
