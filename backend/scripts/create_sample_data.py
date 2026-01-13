"""
Sample Data Generator for Smart SPC System
Creates initial data for testing and development
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_spc.settings')
django.setup()

from dashboard.models import DashboardKPI, TopDefect, Alert, AIInsight
from qcost.models import QCostCategory, QCostItem, QCostEntry
from inspection.models import ProcessFlow, ProcessStep, InspectionRun, InspectionResult
from spc.models import SamplingRule, SpcChartDefinition, SpcPoint, SpcEvent
from qa.models import QaProcess, Capa


def create_sample_dashboard_data():
    """Create sample dashboard data for current month"""
    print("Creating dashboard data...")
    current_period = datetime.now().strftime('%Y-%m')

    # KPIs
    DashboardKPI.objects.create(
        period=current_period,
        copq_rate=0.0342,
        total_copq=41000000,
        total_qcost=62000000,
        oos_count=18,
        spc_open_events=6
    )

    # Top Defects
    defects = [
        ('스크래치', 61, 8000000),
        ('치수불량', 45, 5000000),
        ('이물', 28, 2000000),
        ('색상불량', 15, 1000000),
        ('기타', 12, 500000)
    ]
    for defect, count, cost in defects:
        TopDefect.objects.create(
            period=current_period,
            defect=defect,
            count=count,
            cost=cost
        )

    # Alerts
    Alert.objects.create(
        event_id='evt-001',
        type='TREND',
        severity=4,
        title='내경 추세 발생',
        description='X-bar 관리도에서 추세 이상 감지됨'
    )
    Alert.objects.create(
        event_id='evt-002',
        type='OOS',
        severity=5,
        title='외경 규격 이탈',
        description='외경 측정값이 상한 규격 초과'
    )
    Alert.objects.create(
        event_id='evt-003',
        type='RULE_1',
        severity=3,
        title='3σ 벗어남',
        description='연속 1점이 3σ 밖으로 이탈'
    )

    # AI Insights
    AIInsight.objects.create(
        ai_id='ai-001',
        period=current_period,
        title='COPQ 주요 원인 분석',
        summary='치수불량이 전체 COPQ의 40% 차지. CNC 가공 공정에서 온도 보정 주기를 단축할 것을 권장합니다.',
        confidence=0.86,
        insight_type='OPTIMIZATION',
        actionable=True
    )
    AIInsight.objects.create(
        ai_id='ai-002',
        period=current_period,
        title='세척 공정 개선 효과',
        summary='세척 시간 연장으로 이물 부착률이 15% 감소했습니다.',
        confidence=0.92,
        insight_type='OPTIMIZATION',
        actionable=True
    )

    print(f"  ✓ Dashboard data for {current_period}")


def create_sample_qcost_data():
    """Create sample Q-COST data"""
    print("Creating Q-COST data...")

    # Categories
    categories = [
        ('CAT-001', 'PREVENTION', '교육 훈련', '품질 교육 및 훈련 비용'),
        ('CAT-002', 'PREVENTION', '품질 공학', '공정 설계 및 개선'),
        ('CAT-003', 'APPRAISAL', '검사 비용', '검사원 인건비 및 장비'),
        ('CAT-004', 'APPRAISAL', '시험 비용', '시험 및 측정 비용'),
        ('CAT-005', 'INTERNAL_FAILURE', '스크래치', '스크래치 불량 비용'),
        ('CAT-006', 'INTERNAL_FAILURE', '치수불량', '치수 불량 비용'),
        ('CAT-007', 'EXTERNAL_FAILURE', '클레임', '고객 클레임 비용'),
        ('CAT-008', 'EXTERNAL_FAILURE', '반품 처리', '반품 및 교환 비용'),
    ]

    for cat_id, cat_type, name, desc in categories:
        QCostCategory.objects.create(
            category_id=cat_id,
            category_type=cat_type,
            name=name,
            description=desc
        )

    # Items
    for cat_id, item_id, code, name, unit in [
        ('CAT-001', 'ITEM-001', 'EDU-001', '신규 교육', '시간'),
        ('CAT-003', 'ITEM-002', 'INSP-001', '정검사', '시간'),
        ('CAT-005', 'ITEM-003', 'DEF-001', '스크래치 재작업', '개'),
    ]:
        category = QCostCategory.objects.get(category_id=cat_id)
        QCostItem.objects.create(
            item_id=item_id,
            category=category,
            code=code,
            name=name,
            unit=unit
        )

    # Entries
    base_date = datetime.now() - timedelta(days=30)
    items = list(QCostItem.objects.all())
    for i in range(20):
        item = random.choice(items)
        quantity = random.randint(1, 100)
        unit_cost = random.randint(10000, 50000)
        total_cost = int(quantity * unit_cost)
        QCostEntry.objects.create(
            entry_id=f'ENTRY-{i+1:03d}',
            item=item,
            occurred_at=base_date + timedelta(days=i),
            quantity=quantity,
            unit_cost=unit_cost,
            total_cost=total_cost
        )

    print("  ✓ Q-COST data created")


def create_sample_inspection_data():
    """Create sample inspection data"""
    print("Creating inspection data...")

    # Process Flow
    flow = ProcessFlow.objects.create(
        flow_id='FLOW-001',
        product_id='PROD-001',
        version='v1.0',
        is_active=True
    )

    # Process Steps
    steps = [
        (1, 'IQC', '입고검사', {'dimension': '10.0±0.1', 'visual': '无伤痕'}),
        (2, 'IPQC', '공정검사1', {'dimension': '20.0±0.1'}),
        (3, 'IPQC', '공정검사2', {'dimension': '30.0±0.15'}),
        (4, 'FQC', '최종검사', {'dimension': '50.0±0.2', 'visual': '无划伤'}),
    ]

    for step_order, insp_type, step_name, criteria in steps:
        ProcessStep.objects.create(
            step_id=f'STEP-{step_order}',
            flow=flow,
            step_order=step_order,
            step_name=step_name,
            inspection_type=insp_type,
            criteria=criteria
        )

    # Inspection Run
    run = InspectionRun.objects.create(
        run_id='RUN-001',
        flow=flow,
        run_type='NORMAL',
        inspector_id='INSPECTOR-001',
        started_at=datetime.now() - timedelta(hours=2),
        status='OPEN'
    )

    # Inspection Results
    steps = list(ProcessStep.objects.filter(flow=flow))
    for i in range(50):
        step = random.choice(steps)
        InspectionResult.objects.create(
            result_id=f'RESULT-{i+1:03d}',
            run=run,
            step=step,
            sample_id=f'SAMPLE-{i+1:03d}',
            measurement_value=round(random.uniform(9.8, 10.2), 3),
            is_oos=random.choice([False, False, False, True]),
            measured_at=datetime.now() - timedelta(hours=2) + timedelta(minutes=i*2)
        )

    print("  ✓ Inspection data created")


def create_sample_spc_data():
    """Create sample SPC data"""
    print("Creating SPC data...")

    # Sampling Rules
    SamplingRule.objects.create(
        rule_id='RULE-001',
        standard='MIL-STD-105E',
        aql=1.5,
        lot_size_from=1,
        lot_size_to=500,
        sample_size=50,
        accept_limit=2,
        reject_limit=3
    )

    # Chart Definition
    chart = SpcChartDefinition.objects.create(
        chart_def_id='CHART-001',
        parameter_id='PARAM-001',
        chart_type='XBAR_R',
        sample_size=5,
        ucl=10.15,
        cl=10.0,
        lcl=9.85
    )

    # SPC Points
    base_time = datetime.now() - timedelta(days=7)
    for i in range(100):
        sample_values = [round(random.uniform(9.9, 10.1), 3) for _ in range(5)]
        mean = round(sum(sample_values) / 5, 3)
        range_val = round(max(sample_values) - min(sample_values), 3)

        SpcPoint.objects.create(
            point_id=f'POINT-{i+1:03d}',
            chart_def=chart,
            timestamp=base_time + timedelta(hours=i*2),
            sample_id=f'SAMPLE-{i+1:03d}',
            value=sample_values[0],
            mean=mean,
            range_val=range_val
        )

    # SPC Event
    SpcEvent.objects.create(
        event_id='EVT-001',
        chart_def=chart,
        event_type='OOS',
        triggered_at=datetime.now() - timedelta(hours=5),
        description='규격 이탈 발생',
        severity=5,
        status='OPEN'
    )

    print("  ✓ SPC data created")


def create_sample_qa_data():
    """Create sample QA data"""
    print("Creating QA data...")

    # QA Process
    qa_process = QaProcess.objects.create(
        qa_process_id='QA-001',
        process_type='AUDIT',
        title='2025년 1분기 내부 심사',
        description='정기 내부 품질 시스템 심사',
        scheduled_at=datetime.now() + timedelta(days=30),
        status='PLANNED'
    )

    # CAPA
    Capa.objects.create(
        capa_id='CAPA-001',
        source_type='SPC_EVENT',
        source_id='EVT-001',
        title='내경 규격 이탈 조치',
        description='내경 측정값이 상한 규격 초과',
        severity='MAJOR',
        assigned_to='USER-001',
        target_date=datetime.now() + timedelta(days=7),
        status='OPEN'
    )

    print("  ✓ QA data created")


def main():
    """Main function to create all sample data"""
    print("=" * 50)
    print("Smart SPC Sample Data Generator")
    print("=" * 50)
    print()

    try:
        create_sample_dashboard_data()
        create_sample_qcost_data()
        create_sample_inspection_data()
        create_sample_spc_data()
        create_sample_qa_data()

        print()
        print("=" * 50)
        print("✓ Sample data created successfully!")
        print("=" * 50)
        print()
        print("You can now:")
        print("  1. Login to Django Admin: http://localhost:8000/admin/")
        print("  2. Test the API endpoints")
        print("  3. View data in the frontend")

    except Exception as e:
        print(f"\n✗ Error creating sample data: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
