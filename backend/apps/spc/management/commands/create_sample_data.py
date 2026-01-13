"""
Django Management Command: Create Sample Data for SPC System

Usage:
    python manage.py create_sample_data

This command generates comprehensive sample data for the entire SPC system including:
- Products with specifications
- Quality measurements
- Inspection plans
- Control charts
- Process capability studies
- Run rule violations
- Quality alerts
- Users with different roles
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random
import numpy as np

from apps.spc.models import (
    Product, InspectionPlan, QualityMeasurement, ControlChart,
    ProcessCapability, RunRuleViolation, QualityAlert, QualityReport
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Create comprehensive sample data for the SPC Quality Control System'

    def add_arguments(self, parser):
        parser.add_argument(
            '--products',
            type=int,
            default=5,
            help='Number of products to create (default: 5)',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days of historical data (default: 30)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new sample data',
        )

    def handle(self, *args, **options):
        num_products = options['products']
        num_days = options['days']
        clear_data = options['clear']

        if clear_data:
            self.stdout.write(self.style.WARNING('Clearing existing sample data...'))
            self.clear_existing_data()

        self.stdout.write(self.style.SUCCESS(f'Creating sample data: {num_products} products, {num_days} days'))

        # Create users
        self.create_users()

        # Create products with specifications
        products = self.create_products(num_products)

        # Create comprehensive data for each product
        for product in products:
            # Create inspection plan
            inspection_plan = self.create_inspection_plan(product)

            # Create quality measurements
            self.create_quality_measurements(product, inspection_plan, num_days)

            # Create control chart
            control_chart = self.create_control_chart(product, inspection_plan)

            # Create process capability
            self.create_process_capability(product, control_chart)

            # Create run rule violations
            self.create_run_rule_violations(control_chart)

            # Create quality alerts
            self.create_quality_alerts(product)

            # Create quality report
            self.create_quality_report(product)

        self.stdout.write(self.style.SUCCESS('✅ Sample data creation completed successfully!'))
        self.print_summary()

    def clear_existing_data(self):
        """Clear all existing SPC data"""
        QualityReport.objects.all().delete()
        QualityAlert.objects.all().delete()
        RunRuleViolation.objects.all().delete()
        ProcessCapability.objects.all().delete()
        ControlChart.objects.all().delete()
        QualityMeasurement.objects.all().delete()
        InspectionPlan.objects.all().delete()
        Product.objects.all().delete()
        User.objects.filter(username__startswith=['demo_', 'admin_']).delete()

    def create_users(self):
        """Create demo users with different roles"""
        self.stdout.write('Creating users...')

        users = [
            {
                'username': 'admin_spc',
                'email': 'admin@spc.com',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Admin',
                'last_name': 'SPC',
            },
            {
                'username': 'demo_manager',
                'email': 'manager@spc.com',
                'is_staff': True,
                'is_superuser': False,
                'first_name': 'Manager',
                'last_name': 'Demo',
            },
            {
                'username': 'demo_engineer',
                'email': 'engineer@spc.com',
                'is_staff': True,
                'is_superuser': False,
                'first_name': 'Engineer',
                'last_name': 'Demo',
            },
            {
                'username': 'demo_operator',
                'email': 'operator@spc.com',
                'is_staff': False,
                'is_superuser': False,
                'first_name': 'Operator',
                'last_name': 'Demo',
            },
        ]

        for user_data in users:
            if not User.objects.filter(username=user_data['username']).exists():
                User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password='demo1234',
                    is_staff=user_data['is_staff'],
                    is_superuser=user_data['is_superuser'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                )
                self.stdout.write(f'  ✓ Created user: {user_data["username"]}')

    def create_products(self, count):
        """Create sample products with specifications"""
        self.stdout.write('Creating products...')

        product_templates = [
            {
                'product_code': 'BATT-A001',
                'product_name': '배터리 셀 A-Type',
                'description': '리튬이온 배터리 셀 전압',
                'unit': 'V',
                'target': 3.7,
                'usl': 3.85,
                'lsl': 3.55,
            },
            {
                'product_code': 'PCB-B002',
                'product_name': 'PCB 보드 B-Type',
                'description': '회로기판 두께',
                'unit': 'mm',
                'target': 1.6,
                'usl': 1.68,
                'lsl': 1.52,
            },
            {
                'product_code': 'SENS-C003',
                'product_name': '센서 모듈 C-Type',
                'description': '온도 센서 정밀도',
                'unit': '°C',
                'target': 25.0,
                'usl': 25.5,
                'lsl': 24.5,
            },
            {
                'product_code': 'CONN-D004',
                'product_name': '커넥터 D-Type',
                'description': '커넥터 핀 저항',
                'unit': 'mΩ',
                'target': 10.0,
                'usl': 12.0,
                'lsl': 8.0,
            },
            {
                'product_code': 'IC-E005',
                'product_name': 'IC 칩 E-Type',
                'description': '집적회로 동작 전압',
                'unit': 'V',
                'target': 1.2,
                'usl': 1.26,
                'lsl': 1.14,
            },
        ]

        products = []
        for i in range(count):
            template = product_templates[i % len(product_templates)]
            product = Product.objects.create(
                product_code=f"{template['product_code']}-{i+1:02d}",
                product_name=f"{template['product_name']} #{i+1}",
                description=template['description'],
                unit=template['unit'],
                target_value=template['target'],
                usl=template['usl'],
                lsl=template['lsl'],
                is_active=True,
            )
            products.append(product)
            self.stdout.write(
                f'  ✓ Created product: {product.product_code} - {product.product_name} '
                f'({product.lsl} ~ {product.target_value} ~ {product.usl} {product.unit})'
            )

        return products

    def create_inspection_plan(self, product):
        """Create inspection plan for product"""
        self.stdout.write(f'  Creating inspection plan for {product.product_code}...')

        plan = InspectionPlan.objects.create(
            product=product,
            plan_name=f'{product.product_code} 검사 계획',
            frequency=random.choice(['HOURLY', 'SHIFT', 'DAILY']),
            sample_size=random.choice([5, 10, 20]),
            subgroup_size=random.choice([3, 5, 7]),
            sampling_method='RANDOM',
            characteristic=f'{product.description} 측정',
            measurement_method='자동 측정기',
            is_active=True,
        )

        self.stdout.write(f'    ✓ Created inspection plan: {plan.plan_name}')
        return plan

    def create_quality_measurements(self, product, inspection_plan, days):
        """Create historical quality measurement records with realistic patterns"""
        self.stdout.write(f'  Creating measurements for {product.product_code}...')

        # Generate measurements with different patterns
        patterns = ['stable', 'trend_up', 'trend_down', 'cycle', 'shift']
        pattern = random.choice(patterns)

        measurements_per_day = random.randint(24, 96)  # Every 15-60 minutes
        total_measurements = days * measurements_per_day

        base_value = product.target_value
        usl = product.usl
        lsl = product.lsl
        range_width = usl - lsl
        std_dev = range_width / 6  # Assuming 6-sigma process

        now = timezone.now()
        batch_start = now - timedelta(days=days)

        measurements = []
        sample_num = 1
        subgroup_num = 1

        for i in range(total_measurements):
            # Generate timestamp
            timestamp = batch_start + timedelta(minutes=i * (24 * 60 // total_measurements))

            # Apply pattern
            if pattern == 'stable':
                value = np.random.normal(base_value, std_dev)
            elif pattern == 'trend_up':
                trend = (i / total_measurements) * std_dev * 2
                value = np.random.normal(base_value + trend, std_dev * 0.8)
            elif pattern == 'trend_down':
                trend = (i / total_measurements) * std_dev * 2
                value = np.random.normal(base_value - trend, std_dev * 0.8)
            elif pattern == 'cycle':
                cycle = np.sin(2 * np.pi * i / (total_measurements / 5)) * std_dev
                value = np.random.normal(base_value + cycle, std_dev * 0.7)
            elif pattern == 'shift':
                shift_point = total_measurements // 2
                if i < shift_point:
                    value = np.random.normal(base_value - std_dev, std_dev * 0.8)
                else:
                    value = np.random.normal(base_value + std_dev, std_dev * 0.8)
            else:
                value = np.random.normal(base_value, std_dev)

            # Clamp to reasonable bounds
            value = max(lsl - range_width * 0.2, min(usl + range_width * 0.2, value))

            # Randomly create out-of-spec values (2% chance)
            is_oos = False
            if random.random() < 0.02:
                is_oos = True
                if random.random() < 0.5:
                    value = usl + random.uniform(0, range_width * 0.1)
                else:
                    value = lsl - random.uniform(0, range_width * 0.1)

            # Update sample/subgroup numbers
            sample_num += 1
            if sample_num > inspection_plan.subgroup_size:
                sample_num = 1
                subgroup_num += 1

            measurement = QualityMeasurement(
                product=product,
                inspection_plan=inspection_plan,
                measurement_value=round(value, 4),
                sample_number=sample_num,
                subgroup_number=subgroup_num,
                measured_at=timestamp,
                measured_by=self.get_random_operator(),
                machine_id=f'MC-{random.randint(1, 5):02d}',
                lot_number=f'LOT-{datetime.now().strftime("%Y%m%d")}-{random.randint(1, 100):03d}',
                is_within_spec=not is_oos,
                is_within_control=not is_oos,
                metadata={
                    'pattern': pattern,
                    'equipment': f'Equipment-{random.randint(1, 3)}',
                },
            )
            measurements.append(measurement)

        # Bulk create for performance
        QualityMeasurement.objects.bulk_create(measurements, batch_size=1000)

        oos_count = sum(1 for m in measurements if not m.is_within_spec)
        self.stdout.write(
            f'    ✓ Created {len(measurements)} measurements '
            f'(pattern: {pattern}, OOS: {oos_count})'
        )

    def create_control_chart(self, product, inspection_plan):
        """Create control chart for product"""
        self.stdout.write(f'  Creating control chart for {product.product_code}...')

        measurements = QualityMeasurement.objects.filter(product=product).order_by('measured_at')

        if not measurements.exists():
            return None

        # Calculate control limits using last 100 measurements
        recent_measurements = measurements[:100]
        values = [m.measurement_value for m in recent_measurements]

        # Calculate X-bar chart statistics
        subgroup_size = inspection_plan.subgroup_size
        subgroups = []
        for i in range(0, len(values), subgroup_size):
            subgroup = values[i:i+subgroup_size]
            if len(subgroup) == subgroup_size:
                subgroups.append(subgroup)

        xbars = [np.mean(sg) for sg in subgroups]
        ranges = [max(sg) - min(sg) for sg in subgroups]

        overall_xbar = np.mean(xbars)
        overall_rbar = np.mean(ranges)

        # Control chart factors (A2, D3, D4) for n=5
        n = subgroup_size
        if n == 3:
            A2, D3, D4 = 1.023, 0, 2.574
        elif n == 5:
            A2, D3, D4 = 0.577, 0, 2.114
        elif n == 7:
            A2, D3, D4 = 0.419, 0.076, 1.924
        else:
            A2, D3, D4 = 0.577, 0, 2.114  # Default to n=5

        # Calculate control limits
        xbar_ucl = overall_xbar + A2 * overall_rbar
        xbar_lcl = overall_xbar - A2 * overall_rbar
        r_ucl = D4 * overall_rbar
        r_lcl = D3 * overall_rbar

        control_chart = ControlChart.objects.create(
            product=product,
            inspection_plan=inspection_plan,
            chart_type='XBAR_R',
            xbar_ucl=xbar_ucl,
            xbar_cl=overall_xbar,
            xbar_lcl=xbar_lcl,
            r_ucl=r_ucl,
            r_cl=overall_rbar,
            r_lcl=r_lcl,
            subgroup_size=subgroup_size,
            num_subgroups=len(subgroups),
            is_active=True,
        )

        self.stdout.write(
            f'    ✓ X-bar: UCL={xbar_ucl:.4f}, CL={overall_xbar:.4f}, LCL={xbar_lcl:.4f}'
        )
        return control_chart

    def create_process_capability(self, product, control_chart):
        """Create process capability study"""
        self.stdout.write(f'  Creating process capability for {product.product_code}...')

        measurements = QualityMeasurement.objects.filter(
            product=product
        ).order_by('-measured_at')[:100]

        if not measurements:
            return None

        values = [m.measurement_value for m in measurements]
        mean = np.mean(values)
        std_dev = np.std(values)

        usl = product.usl
        lsl = product.lsl

        # Calculate capability indices
        cp = (usl - lsl) / (6 * std_dev) if std_dev > 0 else 0
        cpk = min((usl - mean) / (3 * std_dev), (mean - lsl) / (3 * std_dev)) if std_dev > 0 else 0
        cpu = (usl - mean) / (3 * std_dev) if std_dev > 0 else 0
        cpl = (mean - lsl) / (3 * std_dev) if std_dev > 0 else 0

        # Long-term capability (using total variability)
        pp = cp  # Simplified
        ppk = cpk  # Simplified

        # Normality test (simplified - using Anderson-Darling approximation)
        is_normal = True  # Assume normal for generated data

        now = timezone.now()
        month_ago = now - timedelta(days=30)

        ProcessCapability.objects.create(
            product=product,
            control_chart=control_chart,
            cp=cp,
            cpk=cpk,
            cpu=cpu,
            cpl=cpl,
            pp=pp,
            ppk=ppk,
            mean=mean,
            std_deviation=std_dev,
            sample_size=len(values),
            is_normal=is_normal,
            normality_test_statistic=0.5,
            normality_test_p_value=0.8,
            analysis_start=month_ago,
            analysis_end=now,
            notes=f'공정능력 {"우수" if cpk >= 1.33 else "양호" if cpk >= 1.0 else "개선 필요"}',
        )

        self.stdout.write(f'    ✓ Cp: {cp:.3f}, Cpk: {cpk:.3f}')

    def create_run_rule_violations(self, control_chart):
        """Create run rule violations"""
        self.stdout.write(f'  Creating run rule violations for {control_chart.product.product_code}...')

        if not control_chart:
            return

        measurements = QualityMeasurement.objects.filter(
            product=control_chart.product
        ).order_by('measured_at')

        if not measurements.exists():
            return

        violations = []
        values = [m.measurement_value for m in measurements]
        xbar_cl = control_chart.xbar_cl
        xbar_ucl = control_chart.xbar_ucl
        xbar_lcl = control_chart.xbar_lcl

        # Rule 1: Points outside control limits
        for i, value in enumerate(values):
            if value > xbar_ucl or value < xbar_lcl:
                violations.append({
                    'measurement': measurements[i],
                    'rule_type': 'RULE_1',
                    'description': f'값 {value:.4f}이(가) 관리 한계를 벗어남',
                    'severity': 4,
                })

        # Rule 2: 9 consecutive points on same side
        for i in range(len(values) - 9):
            if all(v > xbar_cl for v in values[i:i+9]) or all(v < xbar_cl for v in values[i:i+9]):
                violations.append({
                    'measurement': measurements[i+8],
                    'rule_type': 'RULE_2',
                    'description': '9개 연속 점이 중심선 한쪽에 위치',
                    'severity': 3,
                })
                break

        # Rule 3: 6 consecutive points increasing or decreasing
        for i in range(len(values) - 6):
            if all(values[j] < values[j+1] for j in range(i, i+6)):
                violations.append({
                    'measurement': measurements[i+5],
                    'rule_type': 'RULE_3',
                    'description': '6개 연속 점이 증가함',
                    'severity': 2,
                })
                break

        # Create violation records (limit to 10 per control chart)
        violation_objects = []
        for v in violations[:10]:
            violation_objects.append(
                RunRuleViolation(
                    control_chart=control_chart,
                    measurement=v['measurement'],
                    rule_type=v['rule_type'],
                    description=v['description'],
                    severity=v['severity'],
                    violation_data={
                        'value': float(v['measurement'].measurement_value),
                        'ucl': float(xbar_ucl),
                        'lcl': float(xbar_lcl),
                        'cl': float(xbar_cl),
                    },
                )
            )

        if violation_objects:
            RunRuleViolation.objects.bulk_create(violation_objects)
            self.stdout.write(f'    ✓ Created {len(violation_objects)} run rule violations')

    def create_quality_alerts(self, product):
        """Create quality alerts for the product"""
        self.stdout.write(f'  Creating quality alerts for {product.product_code}...')

        measurements = QualityMeasurement.objects.filter(product=product)

        if not measurements.exists():
            return

        alerts = []

        # OOS (Out of Spec) alerts
        oos_measurements = measurements.filter(is_within_spec=False)
        if oos_measurements.exists():
            count = oos_measurements.count()
            alerts.append(QualityAlert(
                product=product,
                measurement=oos_measurements.first(),
                alert_type='OUT_OF_SPEC',
                title=f'규격 이탈: {product.product_name}',
                description=f'{count}개의 측정값이 규격({product.lsl}~{product.usl})을 벗어났습니다.',
                priority=4,
                status='NEW',
                assigned_to='demo_engineer',
                alert_data={'oos_count': count, 'usl': product.usl, 'lsl': product.lsl},
            ))

        # OOC (Out of Control) alerts
        ooc_measurements = measurements.filter(is_within_control=False)
        if ooc_measurements.exists():
            count = ooc_measurements.count()
            alerts.append(QualityAlert(
                product=product,
                measurement=ooc_measurements.first(),
                alert_type='OUT_OF_CONTROL',
                title=f'관리 한계 이탈: {product.product_name}',
                description=f'{count}개의 측정값이 관리 한계를 벗어났습니다.',
                priority=3,
                status='NEW',
                assigned_to='demo_engineer',
                alert_data={'ooc_count': count},
            ))

        # Run Rule alerts
        violations = RunRuleViolation.objects.filter(
            control_chart__product=product,
            is_resolved=False
        )
        if violations.exists():
            alerts.append(QualityAlert(
                product=product,
                alert_type='RUN_RULE',
                title=f'Run Rule 위반: {product.product_name}',
                description=f'{violations.count()}건의 Run Rule 위반이 감지되었습니다.',
                priority=2,
                status='ACKNOWLEDGED',
                assigned_to='demo_manager',
                acknowledged_at=timezone.now(),
                acknowledged_by='demo_manager',
                alert_data={'violation_count': violations.count()},
            ))

        # Trend alerts (based on recent measurements)
        recent_values = [m.measurement_value for m in measurements.order_by('-measured_at')[:20]]
        if len(recent_values) >= 10:
            # Simple linear trend detection
            x = list(range(len(recent_values)))
            z = np.polyfit(x, recent_values, 1)
            slope = z[0]

            if abs(slope) > 0.01:  # Significant trend
                trend_dir = '상승' if slope > 0 else '하락'
                alerts.append(QualityAlert(
                    product=product,
                    alert_type='TREND',
                    title=f'트렌드 경고: {product.product_name}',
                    description=f'측정값에서 {trend_dir} 추세가 감지되었습니다.',
                    priority=2,
                    status='NEW',
                    assigned_to='demo_engineer',
                    alert_data={'trend_slope': float(slope), 'direction': trend_dir},
                ))

        # Bulk create alerts
        if alerts:
            QualityAlert.objects.bulk_create(alerts)
            self.stdout.write(f'    ✓ Created {len(alerts)} quality alerts')

    def create_quality_report(self, product):
        """Create daily quality report"""
        self.stdout.write(f'  Creating quality report for {product.product_code}...')

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)

        measurements = QualityMeasurement.objects.filter(
            product=product,
            measured_at__gte=yesterday_start,
            measured_at__lt=today_start,
        )

        total_count = measurements.count()
        oos_count = measurements.filter(is_within_spec=False).count()
        ooc_count = measurements.filter(is_within_control=False).count()
        alert_count = QualityAlert.objects.filter(
            product=product,
            created_at__gte=yesterday_start,
        ).count()

        report = QualityReport.objects.create(
            report_type='DAILY',
            title=f'일일 품질 보고서 - {product.product_name} ({yesterday_start.date()})',
            start_date=yesterday_start,
            end_date=today_start,
            summary=f'{product.product_name}의 일일 품질 현황입니다. 총 {total_count}건의 측정값 중 {oos_count}건이 규격 이탈했습니다.',
            key_findings=[
                f'총 측정수: {total_count}건',
                f'규격 이탈: {oos_count}건 ({oos_count/total_count*100 if total_count > 0 else 0:.1f}%)',
                f'관리 한계 이탈: {ooc_count}건',
                f'경고 발생: {alert_count}건',
            ],
            recommendations=[
                '규격 이탈 원인 분석 필요',
                '공정 안정화 점검 권장',
                '정기적 모니터링 강화',
            ],
            total_measurements=total_count,
            out_of_spec_count=oos_count,
            out_of_control_count=ooc_count,
            alert_count=alert_count,
            generated_by='admin_spc',
        )

        # Add product to many-to-many field
        report.products.add(product)

        self.stdout.write(f'    ✓ Created report: {report.title}')

    def get_random_operator(self):
        """Get random operator user"""
        operators = User.objects.filter(username='demo_operator')
        if operators.exists():
            return operators.first().username
        return 'System'

    def print_summary(self):
        """Print summary of created data"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 Sample Data Summary'))
        self.stdout.write('='*60)

        counts = {
            'Users': User.objects.count(),
            'Products': Product.objects.count(),
            'Inspection Plans': InspectionPlan.objects.count(),
            'Quality Measurements': QualityMeasurement.objects.count(),
            'Control Charts': ControlChart.objects.count(),
            'Process Capabilities': ProcessCapability.objects.count(),
            'Run Rule Violations': RunRuleViolation.objects.count(),
            'Quality Alerts': QualityAlert.objects.count(),
            'Quality Reports': QualityReport.objects.count(),
        }

        for model, count in counts.items():
            self.stdout.write(f'  {model}: {count:,}')

        self.stdout.write('='*60)

        # Demo credentials
        self.stdout.write('\n🔑 Demo Credentials:')
        self.stdout.write('  Admin: admin_spc / demo1234')
        self.stdout.write('  Manager: demo_manager / demo1234')
        self.stdout.write('  Engineer: demo_engineer / demo1234')
        self.stdout.write('  Operator: demo_operator / demo1234')
        self.stdout.write('\n')
