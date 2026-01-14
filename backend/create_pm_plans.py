"""
예방 보전 계획 샘플 데이터 생성 스크립트
"""
import os
import django
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_spc.settings')
django.setup()

from predictive_maintenance.models import Equipment, MaintenancePlan
from django.contrib.auth import get_user_model

User = get_user_model()

def create_sample_plans():
    """샘플 예방 보전 계획 생성"""

    # 사용자 가져오기
    try:
        technician = User.objects.filter(is_staff=True).first()
        if not technician:
            technician = User.objects.create_user(
                username='tech01',
                email='tech01@example.com',
                first_name='기술',
                last_name='자님'
            )
    except:
        technician = None

    # 설비별 예방 보전 계획 생성
    equipment_list = Equipment.objects.all()

    plans_data = [
        {
            'name': '일일 점검 및 청소',
            'description': '설비 일일 외관 점검 및 이물질 제거',
            'frequency': 'DAILY',
            'frequency_days': 1,
            'tasks': '외관 청소, 오염 확인, 윤활 상태 확인, 이상 유무 점검',
            'estimated_hours': 0.5,
        },
        {
            'name': '주간 정밀 점검',
            'description': '설비 주간 세부 점검 및 부품 상태 확인',
            'frequency': 'WEEKLY',
            'frequency_days': 7,
            'tasks': '볼트 체결, 베어링 상태, 오일 교환, 필터 교체, 진동 확인',
            'estimated_hours': 2,
        },
        {
            'name': '월간 예방 보전',
            'description': '설비 월간 종합 정비 및 성능 점검',
            'frequency': 'MONTHLY',
            'frequency_days': 30,
            'tasks': '전체 분해 점검, 마모 부품 교체, 정밀도 측정, 보정 작업',
            'estimated_hours': 8,
        },
        {
            'name': '분기별 대정비',
            'description': '설비 분기별 전수 정비',
            'frequency': 'QUARTERLY',
            'frequency_days': 90,
            'tasks': '완전 분해, 부품 교체, 성능 복원, 안전 점검',
            'estimated_hours': 24,
        },
    ]

    created_count = 0
    for equipment in equipment_list:
        for plan_data in plans_data:
            # 다음 예정일 계산 (랜덤하게 1-14일 사이)
            days_ahead = (hash(f"{equipment.id}_{plan_data['name']}") % 14) + 1
            next_due_date = timezone.now().date() + timedelta(days=days_ahead)

            # 비용 계산
            estimated_cost = plan_data['estimated_hours'] * 50000  # 시간당 5만원

            plan, created = MaintenancePlan.objects.get_or_create(
                equipment=equipment,
                name=plan_data['name'],
                defaults={
                    'description': plan_data['description'],
                    'frequency': plan_data['frequency'],
                    'frequency_days': plan_data['frequency_days'],
                    'status': 'ACTIVE',
                    'tasks': plan_data['tasks'],
                    'estimated_hours': plan_data['estimated_hours'],
                    'estimated_cost': estimated_cost,
                    'assigned_to': technician,
                    'next_due_date': next_due_date,
                    'last_performed_date': timezone.now().date() - timedelta(days=plan_data['frequency_days']),
                }
            )

            if created:
                created_count += 1
                print(f"✓ 생성: {equipment.code} - {plan.name}")

    print(f"\n총 {created_count}개의 예방 보전 계획이 생성되었습니다.")

    # 다가오는 일정 확인
    from datetime import timedelta
    upcoming_date = timezone.now().date() + timedelta(days=7)

    upcoming_plans = MaintenancePlan.objects.filter(
        status='ACTIVE',
        next_due_date__lte=upcoming_date
    ).order_by('next_due_date')

    print(f"\n📅 다가오는 일정 (7일 이내): {upcoming_plans.count()}건")
    for plan in upcoming_plans:
        days_until = (plan.next_due_date - timezone.now().date()).days
        print(f"  • {plan.equipment.code} - {plan.name}: {plan.next_due_date} (D-{days_until})")

if __name__ == '__main__':
    print("=" * 50)
    print("예방 보전 계획 샘플 데이터 생성")
    print("=" * 50)
    create_sample_plans()
    print("\n✅ 완료!")
