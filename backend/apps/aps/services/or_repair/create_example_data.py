"""
CP-SAT Repair Engine - 예제 데이터 생성 스크립트

Phase 4-6 모델 테스트용 예제 데이터 생성
"""
import sys
import os
from decimal import Decimal

# Django setup
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.erp.models import MasterItem, MasterMachine
from apps.erp.models_setup import ItemSetupTime, ItemFamily, BatchConfig


def create_item_families():
    """품목 패밀리 생성"""
    print("\n" + "="*60)
    print("Creating Item Families...")
    print("="*60)

    families = [
        {
            'family_cd': 'FAM-SIZE-S',
            'family_nm': '소형 품목',
            'family_type': 'SIZE',
            'intra_family_setup_minutes': 5,
            'inter_family_setup_minutes': 20,
            'description': '소형 크기 품목 그룹'
        },
        {
            'family_cd': 'FAM-SIZE-M',
            'family_nm': '중형 품목',
            'family_type': 'SIZE',
            'intra_family_setup_minutes': 10,
            'inter_family_setup_minutes': 30,
            'description': '중형 크기 품목 그룹'
        },
        {
            'family_cd': 'FAM-SIZE-L',
            'family_nm': '대형 품목',
            'family_type': 'SIZE',
            'intra_family_setup_minutes': 15,
            'inter_family_setup_minutes': 40,
            'description': '대형 크기 품목 그룹'
        },
        {
            'family_cd': 'FAM-COLOR-RED',
            'family_nm': '적색 품목',
            'family_type': 'COLOR',
            'intra_family_setup_minutes': 8,
            'inter_family_setup_minutes': 25,
            'description': '적색 계열 품목 그룹'
        },
        {
            'family_cd': 'FAM-COLOR-BLUE',
            'family_nm': '청색 품목',
            'family_type': 'COLOR',
            'intra_family_setup_minutes': 8,
            'inter_family_setup_minutes': 25,
            'description': '청색 계열 품목 그룹'
        },
    ]

    created_count = 0
    for fam_data in families:
        fam, created = ItemFamily.objects.get_or_create(
            family_cd=fam_data['family_cd'],
            defaults=fam_data
        )
        if created:
            print(f"  [+] Created: {fam}")
            created_count += 1
        else:
            print(f"  [=] Exists: {fam}")

    print(f"\n[OK] {created_count} families created, {len(families) - created_count} already exist")
    return created_count


def create_setup_times():
    """Setup Time 데이터 생성"""
    print("\n" + "="*60)
    print("Creating Setup Times...")
    print("="*60)

    # 기존 데이터 확인
    machines = list(MasterMachine.objects.all()[:3])
    items = list(MasterItem.objects.all()[:5])

    if not machines or not items:
        print("[WARNING] No machines or items found. Please create master data first.")
        return 0

    print(f"Found {len(machines)} machines and {len(items)} items")

    # Setup time 매트릭스 생성 (품목 간 전환 시간)
    setup_times = []

    for machine in machines:
        for i, from_item in enumerate(items):
            for j, to_item in enumerate(items):
                if from_item.itm_id == to_item.itm_id:
                    continue  # 동일 품목 전환은 제외

                # Setup 시간 계산 (예: 품목 순서 차이에 비례)
                base_time = 15
                diff_factor = abs(i - j) * 5
                setup_minutes = base_time + diff_factor

                # Setup 유형 결정
                if setup_minutes <= 15:
                    setup_type = 'QUICK'
                elif setup_minutes <= 25:
                    setup_type = 'STANDARD'
                else:
                    setup_type = 'COMPLEX'

                setup_times.append({
                    'machine': machine,
                    'from_item': from_item,
                    'to_item': to_item,
                    'setup_minutes': setup_minutes,
                    'setup_cost': Decimal(str(setup_minutes * 100)),  # 분당 100원
                    'setup_type': setup_type,
                    'requires_worker': True,
                    'required_workers': 1 if setup_type == 'QUICK' else 2,
                    'description': f'{from_item.itm_id} → {to_item.itm_id} 전환'
                })

    created_count = 0
    for setup_data in setup_times:
        setup, created = ItemSetupTime.objects.get_or_create(
            machine=setup_data['machine'],
            from_item=setup_data['from_item'],
            to_item=setup_data['to_item'],
            defaults=setup_data
        )
        if created:
            created_count += 1

    print(f"[OK] {created_count} setup times created, {len(setup_times) - created_count} already exist")

    # 샘플 출력
    print("\nSample Setup Times:")
    for setup in ItemSetupTime.objects.all()[:5]:
        print(f"  {setup}")

    return created_count


def create_batch_configs():
    """Batch 설정 생성"""
    print("\n" + "="*60)
    print("Creating Batch Configurations...")
    print("="*60)

    machines = list(MasterMachine.objects.all()[:3])
    items = list(MasterItem.objects.all()[:3])

    if not machines or not items:
        print("[WARNING] No machines or items found. Please create master data first.")
        return 0

    batch_configs = []

    for machine in machines:
        for item in items:
            batch_configs.append({
                'machine': machine,
                'item': item,
                'min_batch_size': 1,
                'max_batch_size': 10,
                'optimal_batch_size': 5,
                'batch_setup_minutes': 30,
                'unit_process_minutes': Decimal('10.0'),
                'allow_partial_batch': True,
                'batch_priority': 1,
                'description': f'{machine.mc_cd} - {item.itm_id} Batch 설정'
            })

    created_count = 0
    for batch_data in batch_configs:
        batch, created = BatchConfig.objects.get_or_create(
            machine=batch_data['machine'],
            item=batch_data['item'],
            defaults=batch_data
        )
        if created:
            print(f"  [+] Created: {batch}")
            created_count += 1
        else:
            print(f"  [=] Exists: {batch}")

    print(f"\n[OK] {created_count} batch configs created, {len(batch_configs) - created_count} already exist")

    # Batch 효율성 계산 예제
    print("\nBatch Efficiency Example:")
    if created_count > 0:
        sample_batch = BatchConfig.objects.first()
        if sample_batch:
            print(f"  Config: {sample_batch}")
            print(f"  Batch size 5: {sample_batch.calculate_batch_duration(5)} minutes")
            print(f"  vs Individual 5: {5 * (sample_batch.batch_setup_minutes + int(float(sample_batch.unit_process_minutes)))} minutes")
            efficiency = (5 * (sample_batch.batch_setup_minutes + int(float(sample_batch.unit_process_minutes)))) / sample_batch.calculate_batch_duration(5)
            print(f"  Efficiency gain: {efficiency:.1f}x")

    return created_count


def show_statistics():
    """통계 정보 출력"""
    print("\n" + "="*60)
    print("Database Statistics")
    print("="*60)

    print(f"Item Families: {ItemFamily.objects.count()}")
    print(f"Setup Times: {ItemSetupTime.objects.count()}")
    print(f"Batch Configs: {BatchConfig.objects.count()}")

    # Setup time 분석
    if ItemSetupTime.objects.exists():
        avg_setup = ItemSetupTime.objects.aggregate(
            avg=django.db.models.Avg('setup_minutes')
        )['avg']
        print(f"\nAverage Setup Time: {avg_setup:.1f} minutes")

        print("\nSetup Time by Type:")
        for setup_type, _ in ItemSetupTime._meta.get_field('setup_type').choices:
            count = ItemSetupTime.objects.filter(setup_type=setup_type).count()
            if count > 0:
                print(f"  {setup_type}: {count}")


def run_all():
    """모든 예제 데이터 생성"""
    print("\n" + "="*60)
    print("CP-SAT Repair Engine - Example Data Creation")
    print("="*60)

    try:
        family_count = create_item_families()
        setup_count = create_setup_times()
        batch_count = create_batch_configs()

        show_statistics()

        print("\n" + "="*60)
        print("Summary")
        print("="*60)
        print(f"Item Families created: {family_count}")
        print(f"Setup Times created: {setup_count}")
        print(f"Batch Configs created: {batch_count}")
        print("\n[SUCCESS] Example data creation completed!")

        return True

    except Exception as e:
        print(f"\n[ERROR] Failed to create example data: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import django.db.models
    success = run_all()
    sys.exit(0 if success else 1)
