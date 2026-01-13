from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone
from datetime import datetime, timedelta
from apps.spc.models import Product, QualityMeasurement, RunRuleViolation, ControlChart
import random

class Command(BaseCommand):
    help = 'Generate sample Run Rule violations with AI predictions'

    def handle(self, *args, **options):
        self.stdout.write('Generating Run Rule violation data...')

        # Check if database is available
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Database connection failed: {e}'))
            return

        # Clear existing Run Rule violations
        RunRuleViolation.objects.all().delete()
        self.stdout.write('Cleared existing Run Rule violations')

        # Get or create products
        product, _ = Product.objects.get_or_create(
            product_code='BOLT-M10',
            defaults={
                'product_name': 'M10 볼트',
                'usl': 10.5,
                'lsl': 9.5,
                'target_value': 10.0,
                'unit': 'mm',
                'is_active': True
            }
        )

        # Create a simple control chart for the violations
        control_chart, _ = ControlChart.objects.get_or_create(
            product=product,
            chart_type='XBAR_R',
            defaults={
                'chart_name': f'{product.product_code} Xbar-R Chart',
                'sample_size': 5,
                'ucl': 10.3,
                'lcl': 9.7,
                'center_line': 10.0,
                'is_active': True
            }
        )

        # Generate quality measurements with violations
        self.stdout.write('\nGenerating measurements with Run Rule violations...')

        violations_data = []
        base_time = timezone.now() - timedelta(days=7)

        # Rule 1: Point beyond 3σ
        for i in range(3):
            measurement = QualityMeasurement.objects.create(
                product=product,
                measurement_value=10.85 if i % 2 == 0 else 9.15,
                sample_number=i+1,
                subgroup_number=i+1,
                measured_at=base_time + timedelta(hours=i*2),
                measured_by='OP-001',
                remarks='규격 이탈 측정'
            )

            violation = RunRuleViolation.objects.create(
                control_chart=control_chart,
                measurement=measurement,
                rule_type='RULE_1',
                description=f'측정값 {measurement.measurement_value}이 3σ 한계를 벗어남',
                severity=4 if i == 0 else 3,
                is_resolved=i < 2,
                resolved_at=base_time + timedelta(hours=i*2, minutes=30) if i < 2 else None,
                resolution_notes='공정 조정으로 해결' if i < 2 else '',
                detected_at=base_time + timedelta(hours=i*2, minutes=5),
                violation_data={
                    'measurement_value': float(measurement.measurement_value),
                    'ucl': 10.3,
                    'lcl': 9.7,
                    'ai_predicted': True,
                    'ai_confidence': 0.95,
                    'ai_recommendation': '공정 중단 및 원인 분석 필요'
                }
            )
            violations_data.append(violation)
            self.stdout.write(f'  - Rule 1 Violation {i+1}: {measurement.measurement_value}mm (CRITICAL)')

        # Rule 2: 9 points on same side
        measurements = []
        for i in range(9):
            measurement = QualityMeasurement.objects.create(
                product=product,
                measurement_value=10.1 + (i * 0.02),
                sample_number=i+10,
                subgroup_number=i+10,
                measured_at=base_time + timedelta(days=1, hours=i),
                measured_by='OP-002'
            )
            measurements.append(measurement)

        violation = RunRuleViolation.objects.create(
            control_chart=control_chart,
            measurement=measurements[8],
            rule_type='RULE_2',
            description='9개의 연속된 점이 중심선 상측에 위치',
            severity=3,
            is_resolved=False,
            detected_at=measurements[8].measured_at + timedelta(minutes=5),
            violation_data={
                'start_index': 0,
                'end_index': 8,
                'side': 'above',
                'ai_predicted': True,
                'ai_confidence': 0.88,
                'ai_recommendation': '공정 평균이 상향 이동. 조정 필요'
            }
        )
        violations_data.append(violation)
        self.stdout.write(f'  - Rule 2 Violation: 9 points above centerline (HIGH)')

        # Rule 3: 6 points increasing
        measurements = []
        for i in range(6):
            measurement = QualityMeasurement.objects.create(
                product=product,
                measurement_value=10.0 + (i * 0.08),
                sample_number=i+20,
                subgroup_number=i+20,
                measured_at=base_time + timedelta(days=2, hours=i*2),
                measured_by='OP-003'
            )
            measurements.append(measurement)

        violation = RunRuleViolation.objects.create(
            control_chart=control_chart,
            measurement=measurements[5],
            rule_type='RULE_3',
            description='6개의 연속된 점이 증가 추세',
            severity=3,
            is_resolved=False,
            detected_at=measurements[5].measured_at + timedelta(minutes=5),
            violation_data={
                'start_index': 0,
                'end_index': 5,
                'trend': 'increasing',
                'ai_predicted': True,
                'ai_confidence': 0.82,
                'ai_recommendation': '공정 트렌드 상향. 원인 분석 필요'
            }
        )
        violations_data.append(violation)
        self.stdout.write(f'  - Rule 3 Violation: 6 points increasing (HIGH)')

        # Rule 4: 14 points alternating
        measurements = []
        for i in range(14):
            measurement = QualityMeasurement.objects.create(
                product=product,
                measurement_value=10.0 + (0.3 if i % 2 == 0 else -0.3),
                sample_number=i+30,
                subgroup_number=i+30,
                measured_at=base_time + timedelta(days=3, hours=i),
                measured_by='OP-004'
            )
            measurements.append(measurement)

        violation = RunRuleViolation.objects.create(
            control_chart=control_chart,
            measurement=measurements[13],
            rule_type='RULE_4',
            description='14개 점이 상하 교차 패턴',
            severity=2,
            is_resolved=True,
            resolved_at=measurements[13].measured_at + timedelta(hours=2),
            resolution_notes='측정 시스템 재보정으로 해결',
            detected_at=measurements[13].measured_at + timedelta(minutes=5),
            violation_data={
                'start_index': 0,
                'end_index': 13,
                'alternations': 10,
                'ai_predicted': True,
                'ai_confidence': 0.75,
                'ai_recommendation': '측정 시스템 교정 필요'
            }
        )
        violations_data.append(violation)
        self.stdout.write(f'  - Rule 4 Violation: 14 points alternating (MEDIUM)')

        # Rule 5: 3 of 4 points beyond 2σ
        measurements = []
        for i in range(4):
            measurement = QualityMeasurement.objects.create(
                product=product,
                measurement_value=10.2 + (i * 0.1),
                sample_number=i+50,
                subgroup_number=i+50,
                measured_at=base_time + timedelta(days=4, hours=i*3),
                measured_by='OP-005'
            )
            measurements.append(measurement)

        violation = RunRuleViolation.objects.create(
            control_chart=control_chart,
            measurement=measurements[3],
            rule_type='RULE_5',
            description='4개 연속 점 중 3개가 2σ 영역 밖',
            severity=2,
            is_resolved=False,
            detected_at=measurements[3].measured_at + timedelta(minutes=5),
            violation_data={
                'start_index': 0,
                'end_index': 3,
                'beyond_count': 3,
                'ai_predicted': True,
                'ai_confidence': 0.78,
                'ai_recommendation': '공정 산포 증가. 변이 조사 필요'
            }
        )
        violations_data.append(violation)
        self.stdout.write(f'  - Rule 5 Violation: 3 of 4 beyond 2σ (MEDIUM)')

        # Rule 6: 5 of 6 points beyond 1σ
        measurements = []
        for i in range(6):
            measurement = QualityMeasurement.objects.create(
                product=product,
                measurement_value=10.05 + (i * 0.02),
                sample_number=i+60,
                subgroup_number=i+60,
                measured_at=base_time + timedelta(days=5, hours=i*2),
                measured_by='OP-006'
            )
            measurements.append(measurement)

        violation = RunRuleViolation.objects.create(
            control_chart=control_chart,
            measurement=measurements[5],
            rule_type='RULE_6',
            description='6개 연속 점 중 5개가 1σ 영역 밖',
            severity=2,
            is_resolved=False,
            detected_at=measurements[5].measured_at + timedelta(minutes=5),
            violation_data={
                'start_index': 0,
                'end_index': 5,
                'beyond_count': 5,
                'ai_predicted': True,
                'ai_confidence': 0.70,
                'ai_recommendation': '공정 이탈 징후. 주의 필요'
            }
        )
        violations_data.append(violation)
        self.stdout.write(f'  - Rule 6 Violation: 5 of 6 beyond 1σ (MEDIUM)')

        # Generate some additional measurements without violations
        self.stdout.write('\nGenerating normal measurements...')
        for i in range(50):
            QualityMeasurement.objects.create(
                product=product,
                measurement_value=10.0 + random.uniform(-0.2, 0.2),
                sample_number=i+70,
                subgroup_number=i+70,
                measured_at=base_time + timedelta(hours=i, minutes=random.randint(0, 59)),
                measured_by=f'OP-{random.randint(1, 10):03d}'
            )

        self.stdout.write(self.style.SUCCESS('\n[OK] Sample data generation complete!'))
        self.stdout.write('\nSummary:')
        self.stdout.write(f'  - Total Measurements: {QualityMeasurement.objects.count()}')
        self.stdout.write(f'  - Run Rule Violations: {RunRuleViolation.objects.count()}')
        self.stdout.write(f'  - Violations by Severity:')
        self.stdout.write(f'    - CRITICAL (4): {RunRuleViolation.objects.filter(severity=4).count()}')
        self.stdout.write(f'    - HIGH (3): {RunRuleViolation.objects.filter(severity=3).count()}')
        self.stdout.write(f'    - MEDIUM (2): {RunRuleViolation.objects.filter(severity=2).count()}')
        self.stdout.write(f'    - LOW (1): {RunRuleViolation.objects.filter(severity=1).count()}')
        self.stdout.write(f'  - AI Predicted: {sum(1 for v in RunRuleViolation.objects.all() if v.violation_data.get("ai_predicted"))}')
        self.stdout.write(f'  - Resolved: {RunRuleViolation.objects.filter(is_resolved=True).count()}')
        self.stdout.write(f'  - Open: {RunRuleViolation.objects.filter(is_resolved=False).count()}')
