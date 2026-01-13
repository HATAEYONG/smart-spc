"""
SPC 샘플 데이터 생성 스크립트
테스트용 제품, 측정 데이터, 공정능력 분석 생성
"""
import os
import sys

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import django
from datetime import datetime, timedelta
import numpy as np

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.spc.models import (
    Product,
    InspectionPlan,
    QualityMeasurement,
    ControlChart,
    ProcessCapability,
    QualityAlert,
)
from apps.spc.services.spc_calculator import SPCCalculator
from apps.spc.services.process_capability import ProcessCapabilityAnalyzer


def create_sample_products():
    """샘플 제품 생성"""
    products = [
        {
            'product_code': 'BOLT-M10',
            'product_name': 'M10 볼트',
            'usl': 10.5,
            'lsl': 9.5,
            'target_value': 10.0,
            'unit': 'mm',
            'description': '직경 10mm 볼트',
        },
        {
            'product_code': 'SHAFT-20',
            'product_name': '샤프트 Ø20',
            'usl': 20.05,
            'lsl': 19.95,
            'target_value': 20.0,
            'unit': 'mm',
            'description': '직경 20mm 샤프트',
        },
        {
            'product_code': 'GEAR-T50',
            'product_name': '기어 T50',
            'usl': 50.1,
            'lsl': 49.9,
            'target_value': 50.0,
            'unit': 'mm',
            'description': '톱니수 50 기어',
        },
    ]

    created_products = []
    for prod_data in products:
        product, created = Product.objects.get_or_create(
            product_code=prod_data['product_code'],
            defaults=prod_data
        )
        if created:
            print(f"✅ 제품 생성: {product.product_code} - {product.product_name}")
        else:
            print(f"ℹ️  제품 존재: {product.product_code}")
        created_products.append(product)

    return created_products


def create_inspection_plans(products):
    """검사 계획 생성"""
    plans = []
    for product in products:
        plan, created = InspectionPlan.objects.get_or_create(
            product=product,
            plan_name=f"{product.product_code} 정기 검사",
            defaults={
                'frequency': 'HOURLY',
                'sample_size': 5,
                'subgroup_size': 5,
                'sampling_method': 'RANDOM',
                'characteristic': '직경',
                'is_active': True,
            }
        )
        if created:
            print(f"✅ 검사 계획 생성: {plan.plan_name}")
        plans.append(plan)

    return plans


def generate_measurements(product, inspection_plan, num_subgroups=30):
    """측정 데이터 생성 (정규분포)"""
    print(f"\n📊 측정 데이터 생성 중: {product.product_code}")

    measurements = []
    base_time = datetime.now() - timedelta(hours=num_subgroups)

    # 공정 평균과 표준편차 (약간의 변동 추가)
    process_mean = product.target_value or (product.usl + product.lsl) / 2
    process_std = (product.usl - product.lsl) / 12  # Cp ≈ 2.0 수준

    for subgroup in range(1, num_subgroups + 1):
        # 부분군마다 약간의 평균 변동 (추세 시뮬레이션)
        if subgroup > 20:
            # 후반부에 공정 평균 이동 (트렌드)
            subgroup_mean = process_mean + 0.05 * (subgroup - 20)
        else:
            subgroup_mean = process_mean

        for sample in range(1, inspection_plan.sample_size + 1):
            # 정규분포 샘플링
            value = np.random.normal(subgroup_mean, process_std)

            # 규격 판정
            is_within_spec = product.lsl <= value <= product.usl

            measurement = QualityMeasurement.objects.create(
                product=product,
                inspection_plan=inspection_plan,
                measurement_value=value,
                sample_number=sample,
                subgroup_number=subgroup,
                measured_at=base_time + timedelta(hours=subgroup - 1),
                measured_by='auto_script',
                machine_id='MACHINE_01',
                lot_number=f'LOT_{subgroup:03d}',
                is_within_spec=is_within_spec,
            )
            measurements.append(measurement)

    print(f"✅ {len(measurements)}개 측정 데이터 생성 완료")
    return measurements


def calculate_control_limits(product, inspection_plan):
    """관리 한계선 계산"""
    print(f"\n📈 관리 한계선 계산 중: {product.product_code}")

    # 측정 데이터 조회
    measurements = QualityMeasurement.objects.filter(
        product=product,
        inspection_plan=inspection_plan
    ).order_by('subgroup_number', 'sample_number')

    if measurements.count() == 0:
        print("❌ 측정 데이터가 없습니다")
        return None

    # 부분군별 집계
    from collections import defaultdict
    subgroups_dict = defaultdict(list)

    for m in measurements:
        subgroups_dict[m.subgroup_number].append(m.measurement_value)

    subgroups = [subgroups_dict[key] for key in sorted(subgroups_dict.keys())]

    # SPC Calculator 사용
    calculator = SPCCalculator()

    try:
        xbar_limits, r_limits = calculator.calculate_xbar_r_limits(subgroups)

        # ControlChart 저장
        control_chart, created = ControlChart.objects.update_or_create(
            product=product,
            inspection_plan=inspection_plan,
            chart_type='XBAR_R',
            is_active=True,
            defaults={
                'xbar_ucl': xbar_limits.ucl,
                'xbar_cl': xbar_limits.cl,
                'xbar_lcl': xbar_limits.lcl,
                'r_ucl': r_limits.ucl,
                'r_cl': r_limits.cl,
                'r_lcl': r_limits.lcl,
                'subgroup_size': inspection_plan.subgroup_size,
                'num_subgroups': len(subgroups),
            }
        )

        print(f"✅ 관리 한계선 계산 완료:")
        print(f"   X-bar: UCL={xbar_limits.ucl:.4f}, CL={xbar_limits.cl:.4f}, LCL={xbar_limits.lcl:.4f}")
        print(f"   R:     UCL={r_limits.ucl:.4f}, CL={r_limits.cl:.4f}, LCL={r_limits.lcl:.4f}")

        return control_chart

    except Exception as e:
        print(f"❌ 관리 한계선 계산 실패: {e}")
        return None


def analyze_process_capability(product, measurements):
    """공정능력 분석"""
    print(f"\n🎯 공정능력 분석 중: {product.product_code}")

    if len(measurements) < 30:
        print("❌ 측정 데이터가 부족합니다 (최소 30개)")
        return None

    # 데이터 준비
    data = [m.measurement_value for m in measurements]

    # 부분군 데이터
    from collections import defaultdict
    subgroups_dict = defaultdict(list)
    for m in measurements:
        subgroups_dict[m.subgroup_number].append(m.measurement_value)
    subgroups = [subgroups_dict[key] for key in sorted(subgroups_dict.keys())]

    # 분석 실행
    analyzer = ProcessCapabilityAnalyzer()

    try:
        result = analyzer.analyze(
            data=data,
            usl=product.usl,
            lsl=product.lsl,
            target=product.target_value,
            subgroup_data=subgroups
        )

        # 저장
        capability = ProcessCapability.objects.create(
            product=product,
            cp=result.cp,
            cpk=result.cpk,
            cpu=result.cpu,
            cpl=result.cpl,
            pp=result.pp,
            ppk=result.ppk,
            mean=result.mean,
            std_deviation=result.std_dev,
            sample_size=result.sample_size,
            is_normal=result.is_normal,
            normality_test_statistic=result.test_statistic,
            normality_test_p_value=result.p_value,
            analysis_start=measurements[0].measured_at,
            analysis_end=measurements[-1].measured_at,
        )

        print(f"✅ 공정능력 분석 완료:")
        print(f"   Cp:  {result.cp:.3f}")
        print(f"   Cpk: {result.cpk:.3f}")
        print(f"   정규성: {result.is_normal} (p-value: {result.p_value:.4f})")
        print(f"   예상 불량률: {result.expected_ppm_total:.2f} PPM")

        # Cpk 평가
        interpretation = analyzer.interpret_cpk(result.cpk)
        print(f"   평가: {interpretation['rating']} - {interpretation['description']}")

        return capability

    except Exception as e:
        print(f"❌ 공정능력 분석 실패: {e}")
        return None


def create_sample_alerts(product):
    """샘플 경고 생성"""
    print(f"\n⚠️  품질 경고 생성 중: {product.product_code}")

    alerts = [
        {
            'alert_type': 'OUT_OF_SPEC',
            'title': '규격 이탈 감지',
            'description': f'{product.product_code} 제품에서 규격 이탈이 감지되었습니다.',
            'priority': 4,
            'status': 'NEW',
        },
        {
            'alert_type': 'RUN_RULE',
            'title': '9개 연속 중심선 한쪽',
            'description': 'Run Rule 2번 위반: 9개 연속 점이 중심선 위에 위치',
            'priority': 3,
            'status': 'ACKNOWLEDGED',
        },
    ]

    created_alerts = []
    for alert_data in alerts:
        alert = QualityAlert.objects.create(
            product=product,
            **alert_data
        )
        created_alerts.append(alert)
        print(f"✅ 경고 생성: {alert.title} (우선순위: {alert.get_priority_display()})")

    return created_alerts


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("SPC 샘플 데이터 생성 스크립트")
    print("=" * 60)

    # 1. 제품 생성
    print("\n[1단계] 제품 생성")
    products = create_sample_products()

    # 2. 검사 계획 생성
    print("\n[2단계] 검사 계획 생성")
    plans = create_inspection_plans(products)

    # 3. 각 제품별 데이터 생성
    for product, plan in zip(products, plans):
        print("\n" + "=" * 60)
        print(f"제품: {product.product_code}")
        print("=" * 60)

        # 측정 데이터 생성
        measurements = generate_measurements(product, plan, num_subgroups=30)

        # 관리 한계선 계산
        control_chart = calculate_control_limits(product, plan)

        # 공정능력 분석
        capability = analyze_process_capability(product, measurements)

        # 샘플 경고 생성 (첫 번째 제품만)
        if product == products[0]:
            alerts = create_sample_alerts(product)

    # 4. 요약
    print("\n" + "=" * 60)
    print("✅ 샘플 데이터 생성 완료!")
    print("=" * 60)
    print(f"제품: {Product.objects.filter(is_active=True).count()}개")
    print(f"검사 계획: {InspectionPlan.objects.filter(is_active=True).count()}개")
    print(f"측정 데이터: {QualityMeasurement.objects.count()}개")
    print(f"관리도: {ControlChart.objects.filter(is_active=True).count()}개")
    print(f"공정능력 분석: {ProcessCapability.objects.count()}개")
    print(f"품질 경고: {QualityAlert.objects.count()}개")
    print("\n🚀 이제 Frontend에서 확인할 수 있습니다!")
    print("   http://localhost:3000")


if __name__ == '__main__':
    main()
