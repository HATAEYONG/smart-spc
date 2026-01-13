"""
DOWN_RISK 예측 엔진

설비별 비가동 위험도 예측 (MVP: 통계 기반)
"""
import numpy as np
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg, Count, Q
from apps.aps.execution_models import OperationActual, ExecutionEvent
from apps.aps.ai_llm_models import Prediction, PredictiveModel
import logging

logger = logging.getLogger(__name__)


class DownRiskPredictor:
    """
    DOWN_RISK 예측기

    MVP 접근법: IQR + p95 기반 통계적 위험도 계산
    """

    def __init__(self, lookback_days=60, min_samples=10):
        """
        Args:
            lookback_days: 과거 데이터 조회 기간 (기본 60일)
            min_samples: 최소 샘플 수 (부족 시 기본 위험도 반환)
        """
        self.lookback_days = lookback_days
        self.min_samples = min_samples

    def calculate_resource_risk(self, resource_code):
        """
        설비별 DOWN_RISK 계산

        Args:
            resource_code: 설비 코드 (e.g., 'MC-001')

        Returns:
            dict: {
                'risk_value': float (0~1),
                'confidence': float (0~1),
                'explanation': str,
                'stats': dict
            }
        """
        logger.info(f"Calculating DOWN_RISK for {resource_code}")

        # 1. 과거 작업 데이터 조회
        start_date = timezone.now() - timedelta(days=self.lookback_days)

        operations = OperationActual.objects.filter(
            resource_code=resource_code,
            actual_start_dt__gte=start_date,
            status='COMPLETED'
        ).values_list('proc_time_hr', flat=True)

        proc_times = list(operations)

        # 2. 데이터 부족 시 기본 위험도
        if len(proc_times) < self.min_samples:
            logger.warning(
                f"{resource_code}: Insufficient data ({len(proc_times)} < {self.min_samples}), "
                "returning default risk"
            )
            return {
                'risk_value': 0.5,
                'confidence': 0.3,
                'explanation': f'데이터 부족 ({len(proc_times)}개 샘플). 기본 위험도 적용.',
                'stats': {
                    'sample_count': len(proc_times),
                    'min_required': self.min_samples
                }
            }

        # 3. IQR 기반 이상치 탐지
        q1, q3 = np.percentile(proc_times, [25, 75])
        iqr = q3 - q1
        upper_bound = q3 + 1.5 * iqr

        abnormal_count = sum(1 for t in proc_times if t > upper_bound)
        iqr_ratio = abnormal_count / len(proc_times)

        # 4. p95 초과 비율
        p95 = np.percentile(proc_times, 95)
        p95_exceed = sum(1 for t in proc_times if t > p95) / len(proc_times)

        # 5. 최근 추세 (최근 7일 vs 전체)
        recent_start = timezone.now() - timedelta(days=7)
        recent_ops = OperationActual.objects.filter(
            resource_code=resource_code,
            actual_start_dt__gte=recent_start,
            status='COMPLETED'
        ).aggregate(
            recent_avg=Avg('proc_time_hr'),
            recent_abnormal=Count('actual_id', filter=Q(is_abnormal=True))
        )

        overall_avg = np.mean(proc_times)
        recent_avg = recent_ops['recent_avg'] or overall_avg
        trend_factor = min(2.0, recent_avg / overall_avg) if overall_avg > 0 else 1.0

        # 6. Down 이벤트 빈도 (있는 경우)
        down_events = ExecutionEvent.objects.filter(
            resource_code=resource_code,
            start_dt__gte=start_date,
            event_type__startswith='DOWN_'
        ).count()

        down_factor = min(1.0, down_events / 30)  # 월 30회 이상이면 최대

        # 7. 종합 위험도 계산
        risk_value = self._calculate_composite_risk(
            iqr_ratio=iqr_ratio,
            p95_exceed=p95_exceed,
            trend_factor=trend_factor,
            down_factor=down_factor
        )

        # 8. 신뢰도 계산
        confidence = self._calculate_confidence(len(proc_times))

        # 9. 설명 생성
        explanation = self._generate_explanation(
            resource_code=resource_code,
            risk_value=risk_value,
            iqr_ratio=iqr_ratio,
            p95_exceed=p95_exceed,
            sample_count=len(proc_times),
            down_events=down_events
        )

        stats = {
            'sample_count': len(proc_times),
            'iqr_ratio': round(iqr_ratio, 3),
            'p95_exceed': round(p95_exceed, 3),
            'trend_factor': round(trend_factor, 3),
            'down_events': down_events,
            'q1': round(q1, 2),
            'q3': round(q3, 2),
            'p95': round(p95, 2),
            'mean': round(overall_avg, 2),
            'recent_mean': round(recent_avg, 2),
        }

        logger.info(f"{resource_code}: risk={risk_value:.3f}, confidence={confidence:.2f}")

        return {
            'risk_value': risk_value,
            'confidence': confidence,
            'explanation': explanation,
            'stats': stats
        }

    def _calculate_composite_risk(self, iqr_ratio, p95_exceed, trend_factor, down_factor):
        """
        종합 위험도 계산

        가중 평균: IQR(40%) + p95(30%) + 최근추세(20%) + Down이벤트(10%)
        """
        risk = (
            0.40 * iqr_ratio * 2.0 +       # IQR 이상치 비율 (가중치 2배)
            0.30 * p95_exceed * 2.0 +      # p95 초과 비율 (가중치 2배)
            0.20 * (trend_factor - 1.0) +  # 최근 증가 추세
            0.10 * down_factor             # Down 이벤트 빈도
        )

        # 0~1 범위로 클리핑
        return max(0.0, min(1.0, risk))

    def _calculate_confidence(self, sample_count):
        """
        신뢰도 계산

        샘플 수가 많을수록 신뢰도 증가
        """
        if sample_count < self.min_samples:
            return 0.3

        # Sigmoid curve: 100개 샘플에서 0.8, 200개에서 0.9
        confidence = 1.0 / (1.0 + np.exp(-(sample_count - 100) / 50))
        return round(min(0.95, max(0.5, confidence)), 2)

    def _generate_explanation(self, resource_code, risk_value, iqr_ratio,
                              p95_exceed, sample_count, down_events):
        """설명 텍스트 생성"""
        risk_level = (
            "높음" if risk_value > 0.7 else
            "보통" if risk_value > 0.4 else
            "낮음"
        )

        explanation = (
            f"{resource_code}의 과거 {self.lookback_days}일 데이터({sample_count}개 작업) 분석 결과 "
            f"위험도 {risk_value:.1%} ({risk_level}). "
        )

        if iqr_ratio > 0.1:
            explanation += f"비정상 작업 비율 {iqr_ratio:.1%}, "

        if p95_exceed > 0.05:
            explanation += f"p95 초과 비율 {p95_exceed:.1%}, "

        if down_events > 0:
            explanation += f"다운타임 이벤트 {down_events}회 발생."

        return explanation.strip()

    def build_all_predictions(self, scenario_id=None, resource_codes=None):
        """
        모든 설비에 대한 DOWN_RISK 예측 생성

        Args:
            scenario_id: 시나리오 ID (optional)
            resource_codes: 설비 코드 리스트 (None이면 전체)

        Returns:
            list[Prediction]: 생성된 Prediction 객체 리스트
        """
        logger.info(f"Building DOWN_RISK predictions (scenario_id={scenario_id})")

        # 1. 대상 설비 목록 조회
        if resource_codes is None:
            # OperationActual에서 활성 설비 추출
            resource_codes = (
                OperationActual.objects
                .filter(
                    actual_start_dt__gte=timezone.now() - timedelta(days=self.lookback_days)
                )
                .values_list('resource_code', flat=True)
                .distinct()
            )

        # 2. PredictiveModel 생성 또는 조회
        model, created = PredictiveModel.objects.get_or_create(
            model_name='DOWN_RISK_MVP',
            defaults={
                'model_type': 'MAINTENANCE_PREDICTION',
                'algorithm': 'IQR_P95_Statistical',
                'description': (
                    f'IQR + p95 기반 설비 다운타임 위험 예측 '
                    f'(lookback={self.lookback_days}days)'
                ),
                'status': 'ACTIVE',
                'version': '1.0'
            }
        )

        if created:
            logger.info(f"Created new PredictiveModel: {model}")

        # 3. 각 설비별 예측 생성
        predictions = []

        for resource_code in resource_codes:
            try:
                # 위험도 계산
                result = self.calculate_resource_risk(resource_code)

                # Prediction 레코드 생성
                prediction = Prediction.objects.create(
                    model=model,
                    prediction_type='DOWN_RISK',
                    target_entity=f'RES:{resource_code}',
                    target_id=scenario_id,
                    predicted_value=result['risk_value'],
                    confidence_score=result['confidence'],
                    predicted_date=timezone.now(),
                    features_used=result['stats'],
                    explanation=result['explanation']
                )

                predictions.append(prediction)
                logger.info(f"  Created prediction for {resource_code}: risk={result['risk_value']:.3f}")

            except Exception as e:
                logger.error(f"  Failed to create prediction for {resource_code}: {e}")
                continue

        logger.info(f"Created {len(predictions)} DOWN_RISK predictions")
        return predictions


def get_resource_risk(resource_code, predictions=None):
    """
    설비의 DOWN_RISK 조회 (헬퍼 함수)

    Args:
        resource_code: 설비 코드
        predictions: Prediction QuerySet (optional, 제공 시 여기서 조회)

    Returns:
        float: 위험도 (0~1), 없으면 0.5
    """
    try:
        if predictions is not None:
            # QuerySet에서 조회
            pred = predictions.filter(target_entity=f'RES:{resource_code}').first()
        else:
            # DB에서 최신 예측 조회
            pred = Prediction.objects.filter(
                prediction_type='DOWN_RISK',
                target_entity=f'RES:{resource_code}'
            ).order_by('-created_at').first()

        if pred:
            return pred.predicted_value
        else:
            logger.warning(f"No DOWN_RISK prediction for {resource_code}, using default 0.5")
            return 0.5

    except Exception as e:
        logger.error(f"Error getting risk for {resource_code}: {e}")
        return 0.5
