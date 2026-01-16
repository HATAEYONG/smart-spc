"""
샘플 데이터 생성 스크립트
개발용 테스트 데이터 생성
"""
import os
import django
from datetime import date, datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_spc.settings')
django.setup()

from django.contrib.auth.models import User
from quality_issues.models import QualityIssue, IssueAnalysis4M, ProblemSolvingStep
from equipment.models import Equipment, EquipmentPart, EquipmentManual, EquipmentRepairHistory, PreventiveMaintenance
from tools.models import Tool, ToolRepairHistory
from work_orders.models import WorkOrder, WorkOrderTool, WorkOrderProgress
from integration.models import ERPIntegration, IntegrationHistory, ManualQualityInput


def create_sample_data():
    print("=" * 50)
    print("샘플 데이터 생성 시작")
    print("=" * 50)

    # 1. 품질 이슈 생성
    print("\n1. 품질 이슈 생성 중...")
    for i in range(1, 6):
        issue = QualityIssue.objects.create(
            issue_number=f'QI-2025-{i:03d}',
            title=f'품질 이슈 #{i}: 치수 불량',
            description=f'제품의 치수 불량 발생. 원인 파악 필요.',
            product_code=f'P-{1000+i}',
            product_name=f'제품 {chr(64+i)}-시리즈',
            defect_type='치수 불량',
            severity=random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
            status=random.choice(['OPEN', 'INVESTIGATING', 'IN_PROGRESS', 'RESOLVED']),
            department='생산부',
            defect_quantity=random.randint(1, 50),
            cost_impact=random.randint(10000, 500000),
            responsible_person='김담당자',
            target_resolution_date=date.today() + timedelta(days=random.randint(1, 30))
        )

        # 4M 분석 생성
        IssueAnalysis4M.objects.create(
            issue=issue,
            category='MAN',
            description=f'작업자 숙련도 부족'
        )
        IssueAnalysis4M.objects.create(
            issue=issue,
            category='MACHINE',
            description=f'설비 정밀도 저하'
        )

        # 8단계 문제 해결 생성
        for step_num in range(1, 9):
            ProblemSolvingStep.objects.create(
                issue=issue,
                step_number=step_num,
                step_name=f'단계 {step_num}',
                content=f'단계 {step_num} 내용',
                completed=random.choice([True, False])
            )

    print(f"   -> {QualityIssue.objects.count()}개 품질 이슈 생성 완료")

    # 2. 설비 생성
    print("\n2. 설비 생성 중...")
    for i in range(1, 11):
        equipment = Equipment.objects.create(
            code=f'EQ-{i:03d}',
            name=f'CNC 머신 {i}호기',
            type='CNC',
            manufacturer='FANUC',
            model=f'GF-{2000+i}',
            serial_number=f'SN-{20250000+i}',
            location=f'A구역-{i}라인',
            installation_date=date(2023, 1, 1) + timedelta(days=i*30),
            status=random.choice(['OPERATIONAL', 'MAINTENANCE', 'DAMAGED']),
            department='생산부',
            cost=random.randint(50000000, 150000000),
            specifications={'max_rpm': 12000, 'power': '15kW'},
            health_score=random.randint(60, 100),
            predicted_failure_days=random.randint(30, 365)
        )

        # 설비 부품 생성
        for j in range(1, 4):
            EquipmentPart.objects.create(
                equipment=equipment,
                code=f'PART-{i:03d}-{j}',
                name=f'부품 {j}',
                part_number=f'PN-{i*100+j}',
                specifications=f'사양 정보 {j}',
                stock_quantity=random.randint(5, 50),
                min_stock=10,
                unit_price=random.randint(100000, 500000),
                supplier='공급사 A',
                location=f'창고-A-{j}'
            )

        # 예방 보전 작업 생성
        PreventiveMaintenance.objects.create(
            equipment=equipment,
            task_number=f'PM-{20250100+i}',
            task_name=f'정기 점검 {i}호기',
            description='월간 정기 점검 및 정비',
            frequency=random.choice(['DAILY', 'WEEKLY', 'MONTHLY']),
            scheduled_date=date.today() + timedelta(days=random.randint(1, 30)),
            status=random.choice(['PENDING', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED']),
            estimated_duration=random.randint(60, 240),
            priority='MEDIUM',
            next_due=date.today() + timedelta(days=30)
        )

    print(f"   -> {Equipment.objects.count()}개 설비 생성 완료")

    # 3. 치공구 생성
    print("\n3. 치공구 생성 중...")
    for i in range(1, 11):
        tool = Tool.objects.create(
            code=f'TL-{i:03d}',
            name=f'절삭 공구 {i}형',
            type='절삭공구',
            manufacturer='Sandvik',
            model=f'CT-{100+i}',
            serial_number=f'TSN-{20250000+i}',
            location=f'공구함-A-{i}',
            purchase_date=date(2024, 1, 1) + timedelta(days=i*20),
            status=random.choice(['AVAILABLE', 'IN_USE', 'MAINTENANCE', 'DAMAGED']),
            department='생산부',
            cost=random.randint(500000, 5000000),
            specifications={'diameter': f'{10+i}mm', 'material': 'Carbide'},
            expected_life_days=random.randint(90, 180),
            predicted_remaining_days=random.randint(10, 100),
            usage_count=random.randint(20, 150)
        )

        # 치공구 수리 이력 생성
        if random.random() > 0.5:
            ToolRepairHistory.objects.create(
                tool=tool,
                repair_date=date.today() - timedelta(days=random.randint(1, 60)),
                repair_type=random.choice(['CORRECTIVE', 'PREVENTIVE', 'REPLACEMENT']),
                description='연마 교체',
                status='COMPLETED',
                total_cost=random.randint(100000, 500000),
                downtime_hours=random.randint(2, 8)
            )

    print(f"   -> {Tool.objects.count()}개 치공구 생성 완료")

    # 4. 작업지시 생성
    print("\n4. 작업지시 생성 중...")
    equipment_list = list(Equipment.objects.all())
    tool_list = list(Tool.objects.filter(status='AVAILABLE'))

    for i in range(1, 11):
        work_order = WorkOrder.objects.create(
            order_number=f'WO-{20250100+i}',
            product_code=f'P-{1000+i}',
            product_name=f'제품 {chr(64+i)}',
            quantity=random.randint(100, 1000),
            status=random.choice(['PENDING', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED']),
            priority=random.choice(['LOW', 'MEDIUM', 'HIGH']),
            start_date=date.today() + timedelta(days=random.randint(0, 7)),
            target_end_date=date.today() + timedelta(days=random.randint(7, 30)),
            equipment=random.choice(equipment_list) if equipment_list else None,
            estimated_cost=random.randint(1000000, 10000000),
            progress_percentage=random.randint(0, 100),
            predicted_completion_risk=random.choice(['LOW', 'MEDIUM', 'HIGH']),
            notes=f'작업지시 비고 {i}'
        )

        # 작업지시-치공구 연결
        if tool_list and random.random() > 0.3:
            tool = random.choice(tool_list)
            WorkOrderTool.objects.create(
                work_order=work_order,
                tool=tool,
                quantity_required=1,
                usage_hours=random.randint(1, 10)
            )

        # 진행 상황 로그 생성
        if work_order.status in ['IN_PROGRESS', 'COMPLETED']:
            WorkOrderProgress.objects.create(
                work_order=work_order,
                status=work_order.status,
                progress_percentage=work_order.progress_percentage,
                completed_quantity=int(work_order.quantity * work_order.progress_percentage / 100),
                notes=f'진행 상황 업데이트'
            )

    print(f"   -> {WorkOrder.objects.count()}개 작업지시 생성 완료")

    # 5. ERP 연계 생성
    print("\n5. ERP 연계 생성 중...")
    for i in range(1, 4):
        integration = ERPIntegration.objects.create(
            name=f'{["SAP ERP", "MES 시스템", "PLM 시스템"][i-1]}',
            system_type=["ERP", "MES", "PLM"][i-1],
            description=f'{["SAP ERP 연동", "MES 시스템 연동", "PLM 시스템 연동"][i-1]}',
            endpoint_url=f'https://api.example-{i}.com/v1',
            auth_method='API_KEY',
            api_key=f'key_{i}_abcdefg12345',
            sync_frequency_minutes=60,
            auto_sync=True,
            data_types=['생산주문', '자재정보', 'BOM'],
            status=random.choice(['CONNECTED', 'DISCONNECTED']),
            is_active=True
        )

        # 동기화 이력 생성
        for j in range(1, 6):
            IntegrationHistory.objects.create(
                integration=integration,
                sync_id=f'SYNC-202501{j:02d}-00{i}',
                sync_type=random.choice(['FULL', 'INCREMENTAL', 'MANUAL']),
                start_time=datetime.now() - timedelta(days=j, hours=random.randint(1, 23)),
                end_time=datetime.now() - timedelta(days=j, hours=random.randint(1, 23)),
                duration_seconds=random.randint(30, 300),
                status=random.choice(['SUCCESS', 'FAILED', 'PARTIAL']),
                records_processed=random.randint(100, 5000),
                records_success=random.randint(90, 5000),
                records_failed=random.randint(0, 100),
                data_types=['생산주문', '자재정보']
            )

    print(f"   -> {ERPIntegration.objects.count()}개 ERP 연계 생성 완료")

    # 6. 자체 입력 생성
    print("\n6. 자체 입력 생성 중...")
    inspector = User.objects.filter(username='admin').first()

    for i in range(1, 11):
        ManualQualityInput.objects.create(
            record_number=f'QR-202501{random.randint(10, 99)}',
            inspection_type=random.choice(['INCOMING', 'PROCESS', 'FINAL', 'OUTGOING']),
            inspection_date=date.today() - timedelta(days=random.randint(0, 30)),
            product_code=f'P-{1000+i}',
            product_name=f'제품 {chr(64+i)}',
            batch_number=f'B{20250100+i}',
            lot_number=f'L{20250100+i}',
            sample_size=random.randint(10, 100),
            defect_count=random.randint(0, 10),
            defect_rate=round(random.uniform(0, 5), 2),
            characteristics=[
                {
                    'name': '길이',
                    'target': 100.0,
                    'tolerance': 0.5,
                    'measured': round(100.0 + random.uniform(-0.5, 0.5), 2),
                    'status': 'OK'
                }
            ],
            defect_details=[
                {
                    'type': '긁힘',
                    'count': random.randint(0, 5),
                    'description': '표면 긁힘'
                }
            ],
            inspector=inspector,
            department='품질부',
            status=random.choice(['PENDING', 'APPROVED', 'REJECTED'])
        )

    print(f"   -> {ManualQualityInput.objects.count()}개 자체 입력 생성 완료")

    print("\n" + "=" * 50)
    print("샘플 데이터 생성 완료!")
    print("=" * 50)
    print("\n생성된 데이터 요약:")
    print(f"  - 품질 이슈: {QualityIssue.objects.count()}개")
    print(f"  - 설비: {Equipment.objects.count()}개")
    print(f"  - 치공구: {Tool.objects.count()}개")
    print(f"  - 작업지시: {WorkOrder.objects.count()}개")
    print(f"  - ERP 연계: {ERPIntegration.objects.count()}개")
    print(f"  - 자체 입력: {ManualQualityInput.objects.count()}개")
    print(f"\nAdmin 접속: http://localhost:8000/admin/")
    print(f"ID: admin / PW: admin123")


if __name__ == '__main__':
    create_sample_data()
