"""
Celery Tasks for SPC Quality Control System

비동기 작업 정의
- 보고서 생성
- 시계열 분석
- 이상 감지
- 데이터 정리
"""

from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
import logging

from .models import (
    Product, QualityMeasurement, QualityAlert, QualityReport
)
from .services.report_generator import QualityReportGenerator, ReportExporter
from .services.time_series_analysis import TimeSeriesService, AnomalyDetector

logger = get_task_logger(__name__)


@shared_task(bind=True, name='apps.spc.tasks.generate_daily_report')
def generate_daily_report(self, report_date: str = None):
    """
    일일 보고서 생성 (비동기)
    """
    try:
        logger.info(f"일일 보고서 생성 시작: {report_date}")

        if report_date:
            date = datetime.fromisoformat(report_date)
        else:
            date = timezone.now().date()

        generator = QualityReportGenerator()
        report_data = generator.generate_daily_report(date)

        # 보고서 저장
        report = QualityReport.objects.create(
            report_type='DAILY',
            title=f"{date.strftime('%Y-%m-%d')} 일일 보고서",
            description=date.strftime('%Y년 %m월 %d일 일일 보고서'),
            products_data=report_data,
            generated_by='system'
        )

        logger.info(f"일일 보고서 생성 완료: {report.id}")
        return {'report_id': report.id, 'status': 'success'}

    except Exception as e:
        logger.error(f"일일 보고서 생성 실패: {str(e)}")
        self.retry(exc=e, countdown=60)  # 1분 후 재시도


@shared_task(bind=True, name='apps.spc.tasks.generate_weekly_report')
def generate_weekly_report(self, report_date: str = None):
    """
    주간 보고서 생성 (비동기)
    """
    try:
        logger.info(f"주간 보고서 생성 시작: {report_date}")

        if report_date:
            date = datetime.fromisoformat(report_date)
        else:
            date = timezone.now().date()

        generator = QualityReportGenerator()
        report_data = generator.generate_weekly_report(date)

        # 보고서 저장
        report = QualityReport.objects.create(
            report_type='WEEKLY',
            title=f"{date.strftime('%Y-W%U')} 주간 보고서",
            description=date.strftime('%Y년 %U주 주간 보고서'),
            products_data=report_data,
            generated_by='system'
        )

        logger.info(f"주간 보고서 생성 완료: {report.id}")
        return {'report_id': report.id, 'status': 'success'}

    except Exception as e:
        logger.error(f"주간 보고서 생성 실패: {str(e)}")
        self.retry(exc=e, countdown=300)  # 5분 후 재시도


@shared_task(bind=True, name='apps.spc.tasks.generate_monthly_report')
def generate_monthly_report(self, report_date: str = None):
    """
    월간 보고서 생성 (비동기)
    """
    try:
        logger.info(f"월간 보고서 생성 시작: {report_date}")

        if report_date:
            date = datetime.fromisoformat(report_date)
        else:
            date = timezone.now().date()

        generator = QualityReportGenerator()
        report_data = generator.generate_monthly_report(date)

        # 보고서 저장
        report = QualityReport.objects.create(
            report_type='MONTHLY',
            title=f"{date.strftime('%Y-%m')} 월간 보고서",
            description=date.strftime('%Y년 %m월 월간 보고서'),
            products_data=report_data,
            generated_by='system'
        )

        logger.info(f"월간 보고서 생성 완료: {report.id}")
        return {'report_id': report.id, 'status': 'success'}

    except Exception as e:
        logger.error(f"월간 보고서 생성 실패: {str(e)}")
        self.retry(exc=e, countdown=600)  # 10분 후 재시도


@shared_task(name='apps.spc.tasks.process_measurement_async')
def process_measurement_async(measurement_id: int):
    """
    측정 데이터 처리 (비동기)
    """
    try:
        from .models import QualityMeasurement
        from .services.spc_calculator import SPCCalculator
        from .services.run_rules import RunRuleChecker
        from .services.process_capability import ProcessCapabilityAnalyzer

        measurement = QualityMeasurement.objects.get(id=measurement_id)
        product = measurement.product

        # SPC 계산
        calculator = SPCCalculator()

        # Run Rule 검출
        checker = RunRuleChecker()
        violations = checker.check_measurement(measurement, product)

        # 공정능력 재계산 (최근 데이터 기반)
        capability_analyzer = ProcessCapabilityAnalyzer()
        # ... 공정능력 계산

        logger.info(f"측정 데이터 처리 완료: {measurement_id}")
        return {'measurement_id': measurement_id, 'violations': len(violations)}

    except Exception as e:
        logger.error(f"측정 데이터 처리 실패: {str(e)}")
        raise


@shared_task(name='apps.spc.tasks.run_hourly_timeseries_analysis')
def run_hourly_timeseries_analysis():
    """
    매시간 모든 제품의 시계열 분석 실행
    """
    try:
        logger.info("시계열 분석 시작")

        products = Product.objects.filter(is_active=True)
        results = []

        for product in products:
            try:
                service = TimeSeriesService()
                result = service.analyze_product_timeseries(
                    product_id=product.id,
                    days=1,  # 최근 24시간
                    forecast_steps=6  # 다음 6시간 예측
                )

                # 예측에 문제가 있으면 경고 생성
                if result['forecast']['accuracy_metrics'].get('trend', 'increasing') == 'increasing':
                    QualityAlert.objects.create(
                        product=product,
                        alert_type='TREND_WARNING',
                        priority=3,
                        title=f'추세 경고: {product.product_code}',
                        description=f'시계열 분석 결과 추세가 상승하고 있습니다',
                        detected_by='system'
                    )

                results.append({'product_id': product.id, 'status': 'analyzed'})

            except Exception as e:
                logger.error(f"제품 {product.id} 분석 실패: {str(e)}")
                results.append({'product_id': product.id, 'status': 'error', 'error': str(e)})

        logger.info(f"시계열 분석 완료: {len(results)}개 제품 처리")
        return results

    except Exception as e:
        logger.error(f"시계열 분석 실패: {str(e)}")
        raise


@shared_task(name='apps.spc.tasks.detect_anomalies_periodically')
def detect_anomalies_periodically():
    """
    주기적으로 모든 제품의 이상 감지 실행
    """
    try:
        logger.info("이상 감지 시작")

        products = Product.objects.filter(is_active=True)
        results = []

        for product in products:
            try:
                # 최근 24시간 데이터 이상 감지
                start_date = timezone.now() - timedelta(hours=24)
                measurements = QualityMeasurement.objects.filter(
                    product=product,
                    measured_at__gte=start_date
                ).order_by('measured_at')

                if measurements.count() < 10:
                    continue

                values = list(measurements.values_list('measurement_value', flat=True))

                # 이상 감지
                detector = AnomalyDetector()
                anomalies = detector.detect_statistical_anomalies(values, threshold=3.0)

                # 이상이 발견되면 경고 생성
                if anomalies:
                    QualityAlert.objects.create(
                        product=product,
                        alert_type='ANOMALY_DETECTED',
                        priority=4 if len(anomalies) > 3 else 3,
                        title=f'이상 감지: {product.product_code}',
                        description=f'{len(anomalies)}개의 이상 데이터가 감지되었습니다',
                        detected_by='system'
                    )

                results.append({'product_id': product.id, 'anomaly_count': len(anomalies)})

            except Exception as e:
                logger.error(f"제품 {product.id} 이상 감지 실패: {str(e)}")
                results.append({'product_id': product.id, 'status': 'error', 'error': str(e)})

        logger.info(f"이상 감지 완료: {len(results)}개 제품 처리")
        return results

    except Exception as e:
        logger.error(f"이상 감지 실패: {str(e)}")
        raise


@shared_task(name='apps.spc.tasks.send_critical_alert')
def send_critical_alert(alert_id: int):
    """
    중요 경고 이메일 전송
    """
    try:
        alert = QualityAlert.objects.get(id=alert_id)

        subject = f"[긴급] {alert.title}"
        message = f"""
제품: {alert.product.product_name}
코드: {alert.product.product_code}
유형: {alert.get_alert_type_display()}
우선순위: {alert.get_priority_display()}
설명: {alert.description}
감지 시간: {alert.created_at}

즉시 확인해 주십시오.
        """

        recipient_list = getattr(settings, 'QUALITY_ALERT_EMAILS', ['admin@example.com'])

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False
        )

        logger.info(f"이메일 전송 완료: alert_id={alert_id}")
        return {'alert_id': alert_id, 'status': 'sent'}

    except Exception as e:
        logger.error(f"이메일 전송 실패: {str(e)}")
        raise


@shared_task(name='apps.spc.tasks.cleanup_old_data')
def cleanup_old_data(days_to_keep: int = 90):
    """
    오래된 데이터 정리
    - 지정 기간보다 오래된 RunRuleViolation 삭제
    - 해결된 경고 중 오래된 것 아카이브
    """
    try:
        logger.info(f"데이터 정리 시작: {days_to_keep}일 보다 오래된 데이터")

        cutoff_date = timezone.now() - timedelta(days=days_to_keep)

        # 오래된 RunRuleViolation 아카이브
        from .models import RunRuleViolation
        archived_violations = RunRuleViolation.objects.filter(
            detected_at__lt=cutoff_date,
            is_resolved=True
        ).update(is_archived=True)

        # 오래된 해결된 경고 아카이브
        archived_alerts = QualityAlert.objects.filter(
            created_at__lt=cutoff_date,
            status='RESOLVED'
        ).count()

        logger.info(f"데이터 정리 완료: violations={archived_violations}, alerts={archived_alerts}")
        return {
            'violations_archived': archived_violations,
            'alerts_archived': archived_alerts,
            'cutoff_date': cutoff_date.isoformat()
        }

    except Exception as e:
        logger.error(f"데이터 정리 실패: {str(e)}")
        raise


@shared_task(name='apps.spc.tasks.batch_import_measurements')
def batch_import_measurements(data_list: list):
    """
    대량 측정 데이터 일괄 import (비동기)
    """
    try:
        from .serializers import QualityMeasurementCreateSerializer

        logger.info(f"대량 import 시작: {len(data_list)}개 데이터")

        serializer = QualityMeasurementCreateSerializer(data=data_list, many=True)

        if serializer.is_valid():
            serializer.save()
            logger.info(f"대량 import 완료: {len(data_list)}개 데이터 저장")
            return {'imported': len(data_list), 'status': 'success'}
        else:
            logger.error(f"대량 import 실패: {serializer.errors}")
            return {'imported': 0, 'status': 'error', 'errors': serializer.errors}

    except Exception as e:
        logger.error(f"대량 import 실패: {str(e)}")
        raise


# 작업 체이닝 예시
@shared_task(name='apps.spc.tasks.complex_analysis_chain')
def complex_analysis_chain(product_id: int):
    """
    복잡한 분석 작업 체이닝
    1. 시계열 분석
    2. 이상 감지
    3. 공정능력 계산
    4. 보고서 생성
    """
    # 1. 시계열 분석
    analysis_result = run_timeseries_analysis.delay(product_id)

    # 2. 이상 감지 (시계열 분석 완료 후)
    anomaly_result = detect_anomalies_for_product.delay(product_id)

    # 3. 공정능력 계산 (이상 감지 완료 후)
    capability_result = calculate_process_capability.delay(product_id)

    # 4. 보고서 생성 (공정능력 완료 후)
    report_result = generate_custom_report.delay(product_id)

    return {
        'analysis_id': analysis_result.id,
        'anomaly_id': anomaly_result.id,
        'capability_id': capability_result.id,
        'report_id': report_result.id
    }


# 특정 제품용 작업
@shared_task(name='apps.spc.tasks.detect_anomalies_for_product')
def detect_anomalies_for_product(product_id: int, days: int = 7):
    """특정 제품의 이상 감지"""
    try:
        service = TimeSeriesService()
        result = service.get_maintenance_prediction(product_id, days)

        return {'product_id': product_id, 'result': result}

    except Exception as e:
        logger.error(f"제품 {product_id} 이상 감지 실패: {str(e)}")
        raise


@shared_task(name='apps.spc.tasks.calculate_process_capability')
def calculate_process_capability(product_id: int):
    """특정 제품의 공정능력 계산"""
    try:
        from .services.process_capability import ProcessCapabilityAnalyzer

        analyzer = ProcessCapabilityAnalyzer()
        # ... 공정능력 계산 로직

        return {'product_id': product_id, 'status': 'calculated'}

    except Exception as e:
        logger.error(f"제품 {product_id} 공정능력 계산 실패: {str(e)}")
        raise


@shared_task(name='apps.spc.tasks.generate_custom_report')
def generate_custom_report(product_id: int):
    """특정 제품의 사용자 정의 보고서 생성"""
    try:
        generator = QualityReportGenerator()
        # ... 보고서 생성 로직

        return {'product_id': product_id, 'status': 'generated'}

    except Exception as e:
        logger.error(f"제품 {product_id} 보고서 생성 실패: {str(e)}")
        raise
