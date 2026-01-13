"""
Time Series Analysis Service
시계열 분석 및 예측 기능 (ARIMA, Prophet 스타일)
"""
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from collections import deque

from django.db.models import Avg, StdDev, Count
from apps.spc.models import QualityMeasurement, Product


class TimeSeriesAnalyzer:
    """시계열 데이터 분석기"""

    def __init__(self):
        self.min_samples = 10  # 최소 샘플 수

    def analyze_trend(
        self,
        measurements: List[float],
        timestamps: List[datetime]
    ) -> Dict[str, Any]:
        """
        추세 분석 (Trend Analysis)

        Args:
            measurements: 측정값 리스트
            timestamps: 타임스탬프 리스트

        Returns:
            추세 분석 결과
        """
        if len(measurements) < self.min_samples:
            return {
                'trend': 'unknown',
                'slope': 0,
                'correlation': 0,
                'interpretation': '데이터 부족',
            }

        # 선형 회귀로 추세 계산
        x = np.arange(len(measurements))
        y = np.array(measurements)

        # 1차 다항식 적합
        coefficients = np.polyfit(x, y, 1)
        slope = coefficients[0]
        intercept = coefficients[1]

        # 상관계수 (R²)
        y_pred = np.polyval(coefficients, x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        # 추세 판정
        if abs(slope) < 0.001:
            trend = "stable"
            interpretation = "안정적인 추세"
        elif slope > 0:
            trend = "increasing"
            if r_squared > 0.7:
                interpretation = f"상승 추세 (기울기: {slope:.6f}, 강도: 강함)"
            else:
                interpretation = f"약간 상승 추세 (기울기: {slope:.6f})"
        else:
            trend = "decreasing"
            if r_squared > 0.7:
                interpretation = f"하락 추세 (기울기: {slope:.6f}, 강도: 강함)"
            else:
                interpretation = f"약간 하락 추세 (기울기: {slope:.6f})"

        return {
            'trend': trend,
            'slope': float(slope),
            'intercept': float(intercept),
            'r_squared': float(r_squared),
            'correlation': float(np.sqrt(r_squared)),
            'interpretation': interpretation,
        }

    def detect_seasonality(
        self,
        measurements: List[float],
        period: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        계절성 검출 (Seasonality Detection)

        Args:
            measurements: 측정값 리스트
            period: 예상 주기 (None이면 자동 감지)

        Returns:
            계절성 분석 결과
        """
        if len(measurements) < 20:
            return {
                'has_seasonality': False,
                'period': None,
                'strength': 0,
                'interpretation': '데이터 부족',
            }

        measurements_array = np.array(measurements)
        n = len(measurements_array)

        # 자동 주기 감지 (FFT 기반)
        if period is None:
            fft = np.fft.fft(measurements_array - np.mean(measurements_array))
            freqs = np.fft.fftfreq(n)
            power = np.abs(fft) ** 2

            # 주파수 제외 (DC 성분)
            power[0] = 0

            # 가장 강한 주파수 선택
            dominant_freq_idx = np.argmax(power)
            dominant_freq = freqs[dominant_freq_idx]

            if dominant_freq > 0:
                period = int(1 / dominant_freq)
                period = min(period, n // 2)  # 너무 긴 주기 방지
            else:
                period = None

        if period is None or period <= 1:
            return {
                'has_seasonality': False,
                'period': None,
                'strength': 0,
                'interpretation': '계절성 없음',
            }

        # 계절성 강도 계산 (분산 분석)
        if period > 0 and period < n:
            # 주기별 평균 계산
            seasonal_means = []
            for i in range(period):
                indices = range(i, n, period)
                period_data = measurements_array[indices]
                if len(period_data) > 0:
                    seasonal_means.append(np.mean(period_data))

            overall_mean = np.mean(measurements_array)
            seasonal_variance = np.var(seasonal_means) if len(seasonal_means) > 1 else 0
            total_variance = np.var(measurements_array)

            strength = seasonal_variance / total_variance if total_variance > 0 else 0
        else:
            strength = 0

        has_seasonality = strength > 0.1

        return {
            'has_seasonality': has_seasonality,
            'period': period if has_seasonality else None,
            'strength': float(strength),
            'interpretation': f"주기 {period} 계절성 발견" if has_seasonality else "계절성 없음",
        }

    def decompose(
        self,
        measurements: List[float]
    ) -> Dict[str, Any]:
        """
        시계열 분해 (Trend + Seasonal + Residual)

        Args:
            measurements: 측정값 리스트

        Returns:
            분해된 성분들
        """
        measurements_array = np.array(measurements)
        n = len(measurements_array)

        # 이동평균 (추세)
        window_size = min(7, n // 4)
        if window_size < 3:
            window_size = 3

        trend = np.convolve(
            measurements_array,
            np.ones(window_size) / window_size,
            mode='same'
        )

        # 계절성 (추세 제거 후)
        detrended = measurements_array - trend
        seasonal = np.zeros_like(detrended)

        period = 7  # 일주일 주기 가정
        if n >= period * 2:
            for i in range(period):
                indices = range(i, n, period)
                period_mean = np.mean(detrended[list(indices)])
                for j in indices:
                    if j < n:
                        seasonal[j] = period_mean

        # 잔차 (Residual)
        residual = measurements_array - trend - seasonal

        return {
            'trend': trend.tolist(),
            'seasonal': seasonal.tolist(),
            'residual': residual.tolist(),
            'trend_strength': float(np.var(trend) / np.var(measurements_array)) if np.var(measurements_array) > 0 else 0,
            'seasonal_strength': float(np.var(seasonal) / np.var(measurements_array)) if np.var(measurements_array) > 0 else 0,
            'residual_strength': float(np.var(residual) / np.var(measurements_array)) if np.var(measurements_array) > 0 else 0,
        }


class ForecastEngine:
    """예측 엔진 (ARIMA 단순화 버전)"""

    def __init__(self):
        self.analyzer = TimeSeriesAnalyzer()

    def simple_ma_forecast(
        self,
        measurements: List[float],
        forecast_steps: int = 5,
        window_size: int = 7
    ) -> Dict[str, Any]:
        """
        단순 이동평균 예측 (Simple Moving Average)

        Args:
            measurements: 과거 측정값
            forecast_steps: 예측할 미래 개수
            window_size: 이동평균 윈도우

        Returns:
            예측 결과
        """
        if len(measurements) < window_size:
            window_size = len(measurements)

        # 최근 window_size개의 평균으로 예측
        last_values = measurements[-window_size:]
        forecast_value = np.mean(last_values)

        # 신뢙 구간 예측
        forecast = [forecast_value] * forecast_steps

        # 표준편차 (불로 예측 구간)
        std = np.std(last_values)
        upper_bound = [forecast_value + 1.96 * std] * forecast_steps
        lower_bound = [forecast_value - 1.96 * std] * forecast_steps

        return {
            'method': 'Simple Moving Average',
            'forecast': forecast,
            'upper_bound': upper_bound,
            'lower_bound': lower_bound,
            'confidence': 0.95,
            'window_size': window_size,
        }

    def exponential_smoothing_forecast(
        self,
        measurements: List[float],
        forecast_steps: int = 5,
        alpha: float = 0.3
    ) -> Dict[str, Any]:
        """
        지수평활법 (Exponential Smoothing)

        Args:
            measurements: 과거 측정값
            forecast_steps: 예측할 미래 개수
            alpha: 평활 계수 (0-1)

        Returns:
            예측 결과
        """
        # 초기값 (초기 3개의 평균)
        level = np.mean(measurements[:3])

        # 관측값에 대한 level 업데이트
        for value in measurements:
            level = alpha * value + (1 - alpha) * level

        # 예측
        forecast = [level] * forecast_steps

        # 예측 오차 추정
        errors = [abs(measurements[i] - measurements[i-1]) for i in range(1, len(measurements))]
        mad = np.mean(errors)  # Mean Absolute Deviation
        std_estimate = mad * 1.25  # MAD → std 변환

        upper_bound = [level + 1.96 * std_estimate] * forecast_steps
        lower_bound = [level - 1.96 * std_estimate] * forecast_steps

        return {
            'method': 'Exponential Smoothing',
            'forecast': forecast,
            'upper_bound': upper_bound,
            'lower_bound': lower_bound,
            'confidence': 0.95,
            'alpha': alpha,
            'final_level': float(level),
        }

    def linear_trend_forecast(
        self,
        measurements: List[float],
        forecast_steps: int = 5
    ) -> Dict[str, Any]:
        """
        선형 추세 예측 (Linear Trend Forecast)

        Args:
            measurements: 과거 측정값
            forecast_steps: 예측할 미래 개수

        Returns:
            예측 결과
        """
        x = np.arange(len(measurements))
        y = np.array(measurements)

        # 선형 회귀
        coefficients = np.polyfit(x, y, 1)
        slope, intercept = coefficients

        # 예측
        last_x = len(measurements) - 1
        forecast_x = np.arange(last_x + 1, last_x + 1 + forecast_steps)
        forecast = np.polyval(coefficients, forecast_x)

        # 잔차 표준편차
        y_pred = np.polyval(coefficients, x)
        residuals = y - y_pred
        std = np.std(residuals)

        # 예측 구간
        upper_bound = forecast + 1.96 * std
        lower_bound = forecast - 1.96 * std

        return {
            'method': 'Linear Trend',
            'forecast': forecast.tolist(),
            'upper_bound': upper_bound.tolist(),
            'lower_bound': lower_bound.tolist(),
            'confidence': 0.95,
            'slope': float(slope),
            'intercept': float(intercept),
            'r_squared': float(1 - np.var(residuals) / np.var(y)),
        }

    def combined_forecast(
        self,
        measurements: List[float],
        forecast_steps: int = 5
    ) -> Dict[str, Any]:
        """
        결합 예측 (앙상블)

        Args:
            measurements: 과거 측정값
            forecast_steps: 예측할 미래 개수

        Returns:
            결합 예측 결과
        """
        # 세 가지 방법으로 예측
        ma_result = self.simple_ma_forecast(measurements, forecast_steps)
        es_result = self.exponential_smoothing_forecast(measurements, forecast_steps)
        lt_result = self.linear_trend_forecast(measurements, forecast_steps)

        # 앙상블 (단순 평균)
        ma_forecast = np.array(ma_result['forecast'])
        es_forecast = np.array(es_result['forecast'])
        lt_forecast = np.array(lt_result['forecast'])

        combined_forecast = (ma_forecast + es_forecast + lt_forecast) / 3

        # 결합 신뢰 구간
        ma_upper = np.array(ma_result['upper_bound'])
        es_upper = np.array(es_result['upper_bound'])
        lt_upper = np.array(lt_result['upper_bound'])

        ma_lower = np.array(ma_result['lower_bound'])
        es_lower = np.array(es_result['lower_bound'])
        lt_lower = np.array(lt_result['lower_bound'])

        combined_upper = (ma_upper + es_upper + lt_upper) / 3
        combined_lower = (ma_lower + es_lower + lt_lower) / 3

        return {
            'method': 'Combined (Ensemble)',
            'forecast': combined_forecast.tolist(),
            'upper_bound': combined_upper.tolist(),
            'lower_bound': combined_lower.tolist(),
            'confidence': 0.95,
            'components': {
                'moving_average': ma_result['forecast'],
                'exponential_smoothing': es_result['forecast'],
                'linear_trend': lt_result['forecast'],
            },
        }


class AnomalyDetector:
    """이상 감지 (Anomaly Detection)"""

    def __init__(self, threshold: float = 3.0):
        """
        Args:
            threshold: Z-score 임계값 (기본 3σ)
        """
        self.threshold = threshold

    def detect_statistical_anomalies(
        self,
        measurements: List[QualityMeasurement]
    ) -> List[Dict[str, Any]]:
        """
        통계적 이상 감지 (Z-score 기반)

        Args:
            measurements: QualityMeasurement 객체 리스트

        Returns:
            이상 감지된 포인트 리스트
        """
        anomalies = []
        values = [m.measurement_value for m in measurements]

        if len(values) < 5:
            return []

        # Z-score 계산
        mean = np.mean(values)
        std = np.std(values)

        if std == 0:
            return []

        for i, measurement in enumerate(measurements):
            z_score = abs((measurement.measurement_value - mean) / std)

            if z_score > self.threshold:
                anomalies.append({
                    'index': i,
                    'measurement_id': measurement.id,
                    'value': float(measurement.measurement_value),
                    'z_score': float(z_score),
                    'timestamp': measurement.measured_at.isoformat(),
                    'type': 'statistical_outlier',
                    'severity': 'high' if z_score > 5 else 'medium',
                })

        return anomalies

    def detect_pattern_anomalies(
        self,
        measurements: List[QualityMeasurement]
    ) -> List[Dict[str, Any]]:
        """
        패턴 기반 이상 감지

        - 급격한 변화 (Spike)
        - 방향 변화 (Trend Change)
        - 이상 패턴 (Cyclic/Periodic)

        Args:
            measurements: QualityMeasurement 객체 리스트

        Returns:
            이상 감지된 패턴 리스트
        """
        anomalies = []
        values = [m.measurement_value for m in measurements]

        if len(values) < 10:
            return []

        # 1. 급격한 변화 (Spike) 감지
        mean = np.mean(values)
        std = np.std(values)

        for i in range(1, len(values)):
            delta = abs(values[i] - values[i-1])

            # 이전 값과의 차이가 3σ 이상인 경우
            if delta > 3 * std:
                anomalies.append({
                    'index': i,
                    'type': 'spike',
                    'value': float(values[i]),
                    'previous_value': float(values[i-1]),
                    'delta': float(delta),
                    'timestamp': measurements[i].measured_at.isoformat(),
                    'severity': 'high' if delta > 5 * std else 'medium',
                })

        # 2. 방향 변화 감지 (Cumulative Sum)
        if len(values) >= 20:
            half = len(values) // 2
            first_half_mean = np.mean(values[:half])
            second_half_mean = np.mean(values[half:])

            # 전반부와 후반부의 평균 차이가 큰 경우
            if abs(second_half_mean - first_half_mean) > 2 * std:
                anomalies.append({
                    'type': 'trend_shift',
                    'first_half_mean': float(first_half_mean),
                    'second_half_mean': float(second_half_mean),
                    'shift': float(second_half_mean - first_half_mean),
                    'severity': 'medium',
                })

        return anomalies

    def calculate_anomaly_score(
        self,
        measurement: QualityMeasurement,
        historical_values: List[float]
    ) -> float:
        """
        단일 측정값의 이상 점수 계산

        0-100 사이의 점수 (높을수록 정상)

        Args:
            measurement: 평가할 측정값
            historical_values: 과거 측정값 리스트

        Returns:
            이상 점수 (0-100)
        """
        if len(historical_values) < 5:
            return 100  # 데이터 부족시 정상으로 간주

        mean = np.mean(historical_values)
        std = np.std(historical_values)

        if std == 0:
            return 100

        # Z-score 기반 점수
        z_score = abs((measurement.measurement_value - mean) / std)

        # Z-score를 0-100 점수로 변환
        # Z-score가 0이면 100점, 3이면 0점
        score = max(0, 100 - (z_score * 33.33))

        return float(score)


class PredictiveMaintenance:
    """예측 유지보수 (Predictive Maintenance)"""

    def calculate_equipment_health(
        self,
        measurements: List[QualityMeasurement],
        target_value: float,
        tolerance: float
    ) -> Dict[str, Any]:
        """
        설비 건전성 지수 계산

        Args:
            measurements: 최근 측정값들
            target_value: 목표값
            tolerance: 허용 오차

        Returns:
            건전성 분석 결과
        """
        if not measurements:
            return {
                'health_score': 0,
                'status': 'unknown',
                'interpretation': '데이터 없음',
            }

        values = [m.measurement_value for m in measurements]
        mean = np.mean(values)
        std = np.std(values)

        # 목표값에서의 편차
        deviation = abs(mean - target_value)

        # 건전성 점수 (0-100)
        # 편차가 0이면 100점, tolerance 이상이면 0점
        if tolerance > 0:
            health_score = max(0, 100 * (1 - deviation / tolerance))
        else:
            health_score = 100 if deviation == 0 else 0

        # 상태 판정
        if health_score >= 90:
            status = 'excellent'
            interpretation = '양호'
        elif health_score >= 70:
            status = 'good'
            interpretation = '정상'
        elif health_score >= 50:
            status = 'warning'
            interpretation = '주의 필요'
        elif health_score >= 30:
            status = 'critical'
            interpretation = '즉시 점검 필요'
        else:
            status = 'failure'
            interpretation = '고장 가능성 높음'

        # 추세 분석
        trend_analysis = self.analyze_degradation_trend(measurements)

        return {
            'health_score': float(health_score),
            'status': status,
            'interpretation': interpretation,
            'mean': float(mean),
            'std_deviation': float(std),
            'target_value': target_value,
            'deviation': float(deviation),
            'trend': trend_analysis,
        }

    def analyze_degradation_trend(
        self,
        measurements: List[QualityMeasurement],
        window_size: int = 5
    ) -> Dict[str, Any]:
        """
        열화 추세 분석 (Degradation Trend)

        Args:
            measurements: 측정값 리스트
            window_size: 이동평균 윈도

        Returns:
            열화 추세 분석
        """
        if len(measurements) < window_size * 2:
            return {
                'trend': 'unknown',
                'degradation_rate': 0,
                'remaining_useful_life': None,
            }

        values = [m.measurement_value for m in measurements]
        n = len(values)

        # 이동평균 계산
        moving_avg = []
        for i in range(window_size, n + 1):
            window = values[i - window_size:i]
            moving_avg.append(np.mean(window))

        # 선형 회귀로 열화율 계산
        x = np.arange(len(moving_avg))
        y = np.array(moving_avg)

        coefficients = np.polyfit(x, y, 1)
        degradation_rate = coefficients[0]  # 기울기

        # 추세 판정
        if abs(degradation_rate) < 0.001:
            trend = 'stable'
        elif degradation_rate > 0:
            trend = 'degrading'
        else:
            trend = 'improving'

        return {
            'trend': trend,
            'degradation_rate': float(degradation_rate),
            'r_squared': float(np.corrcoef(x, y)[0] ** 2) if len(x) > 1 else 0,
        }

    def predict_failure_time(
        self,
        measurements: List[QualityMeasurement],
        usl: float,
        lsl: float
    ) -> Dict[str, Any]:
        """
        고장 예측 시간 계산

        Args:
            measurements: 측정값 리스트
            usl: 상한 규격
            lsl: 하한 규격

        Returns:
            고장 예측 결과
        """
        values = [m.measurement_value for m in measurements]

        if len(values) < 5:
            return {
                'predicted_failure': None,
                'confidence': 'low',
                'interpretation': '데이터 부족',
            }

        # 선형 추세 추정
        x = np.arange(len(values))
        y = np.array(values)

        coefficients = np.polyfit(x, y, 1)
        slope = coefficients[0]
        intercept = coefficients[1]

        # 현재값
        current_value = values[-1]

        # 상한/하한까지의 거리
        distance_to_usl = usl - current_value if slope > 0 else float('inf')
        distance_to_lsl = current_value - lsl if slope < 0 else float('inf')

        # 예측 시간 계산
        steps_to_failure = None
        failure_type = None

        if slope > 0:
            # 상승 추세 - USL 초과 예상
            if distance_to_usl > 0 and slope > 0.0001:
                steps_to_failure = distance_to_usl / slope
                failure_type = 'upper_spec_exceeded'
        elif slope < 0:
            # 하락 추세 - LSL 미달 예상
            if distance_to_lsl > 0 and slope < -0.0001:
                steps_to_failure = distance_to_lsl / abs(slope)
                failure_type = 'lower_spec_exceeded'

        # 신뢰도 계산
        y_pred = np.polyval(coefficients, x)
        r_squared = 1 - np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)

        confidence = 'high' if r_squared > 0.7 else 'medium' if r_squared > 0.4 else 'low'

        return {
            'predicted_failure_steps': int(steps_to_failure) if steps_to_failure is not None else None,
            'failure_type': failure_type,
            'confidence': confidence,
            'r_squared': float(r_squared),
            'trend_slope': float(slope),
            'interpretation': self._interpret_failure_prediction(steps_to_failure, failure_type, confidence),
        }

    def _interpret_failure_prediction(
        self,
        steps: Optional[float],
        failure_type: Optional[str],
        confidence: str
    ) -> str:
        """고장 예측 결과 해석"""
        if steps is None:
            return "예측 가능한 규격 이탈 없음 (안정)"

        if confidence == 'low':
            return f"예측 신뢰도 낮음 ({steps:.0f} 측정 후 {failure_type} 가능성)"

        if steps > 50:
            return f"안정 ({steps:.0f} 측정 후 {failure_type} 예상)"
        elif steps > 20:
            return f"주의 필요 ({steps:.0f} 측정 후 {failure_type} 예상)"
        elif steps > 10:
            return f"조기 점검 권장 ({steps:.0f} 측정 후 {failure_type} 예상)"
        else:
            return f"즉시 조치 필요 ({steps:.0f} 측정 후 {failure_type} 예상)"


class TimeSeriesService:
    """시계열 분석 서비스 (메인 인터페이스)"""

    def __init__(self):
        self.analyzer = TimeSeriesAnalyzer()
        self.forecast_engine = ForecastEngine()
        self.anomaly_detector = AnomalyDetector()
        self.predictive_maintenance = PredictiveMaintenance()

    def analyze_product_timeseries(
        self,
        product_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        제품별 시계열 분석

        Args:
            product_id: 제품 ID
            days: 분석 기간 (일)

        Returns:
            종합 분석 결과
        """
        from datetime import timedelta

        start_date = datetime.now() - timedelta(days=days)

        measurements = QualityMeasurement.objects.filter(
            product_id=product_id,
            measured_at__gte=start_date
        ).order_by('measured_at')

        if measurements.count() < 10:
            return {
                'error': '데이터 부족',
                'message': f'최소 {10}개 이상의 측정 데이터가 필요합니다.',
                'available_data': measurements.count(),
            }

        values = list(measurements.values_list('measurement_value', flat=True))
        timestamps = list(measurements.values_list('measured_at', flat=True))

        # 추세 분석
        trend_analysis = self.analyzer.analyze_trend(values, timestamps)

        # 계절성 분석
        seasonality_analysis = self.analyzer.detect_seasonality(values)

        # 시계열 분해
        decomposition = self.analyzer.decompose(values)

        # 예측
        forecast = self.forecast_engine.combined_forecast(values, forecast_steps=5)

        # 이상 감지
        anomalies = self.anomaly_detector.detect_statistical_anomalies(measurements)
        pattern_anomalies = self.anomaly_detector.detect_pattern_anomalies(measurements)

        return {
            'product_id': product_id,
            'analysis_period': f'{days} days',
            'data_points': len(values),
            'statistics': {
                'mean': float(np.mean(values)),
                'std_dev': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'cv': float(np.std(values) / np.mean(values)) if np.mean(values) != 0 else 0,
            },
            'trend_analysis': trend_analysis,
            'seasonality': seasonality_analysis,
            'decomposition': decomposition,
            'forecast': forecast,
            'anomalies': {
                'statistical': anomalies,
                'pattern': pattern_anomalies,
                'total_count': len(anomalies) + len(pattern_anomalies),
            },
        }

    def get_maintenance_prediction(
        self,
        product_id: int
    ) -> Dict[str, Any]:
        """
        유지보수 예측

        Args:
            product_id: 제품 ID

        Returns:
            유지보수 예측 결과
        """
        from datetime import timedelta

        # 제품 정보
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return {
                'error': 'Product not found',
                'product_id': product_id,
            }

        # 최근 데이터
        start_date = datetime.now() - timedelta(days=30)
        measurements = QualityMeasurement.objects.filter(
            product_id=product_id,
            measured_at__gte=start_date
        ).order_by('measured_at')

        if measurements.count() < 10:
            return {
                'error': '데이터 부족',
                'message': '최소 30일간 10개 이상의 측정 데이터가 필요합니다.',
                'available_data': measurements.count(),
            }

        # 건전성 분석
        health = self.predictive_maintenance.calculate_equipment_health(
            measurements,
            product.target_value,
            (product.usl - product.lsl) / 2  # 규격 폭의 절반을 tolerance로 사용
        )

        # 고장 예측
        failure_prediction = self.predictive_maintenance.predict_failure_time(
            measurements,
            product.usl,
            product.lsl
        )

        # 이상 감지
        anomalies = self.anomaly_detector.detect_statistical_anomalies(measurements)

        return {
            'product_id': product_id,
            'product_code': product.product_code,
            'product_name': product.product_name,
            'analysis_date': datetime.now().isoformat(),
            'data_points': measurements.count(),
            'health_status': health,
            'failure_prediction': failure_prediction,
            'recent_anomalies': anomalies[:10],  # 최근 10개
            'recommendations': self._generate_maintenance_recommendations(health, failure_prediction),
        }

    def _generate_maintenance_recommendations(
        self,
        health: Dict[str, Any],
        failure_prediction: Dict[str, Any]
    ) -> List[str]:
        """유지보수 권장사항 생성"""
        recommendations = []

        health_score = health.get('health_score', 100)
        status = health.get('status', '')

        # 건전성 점수 기반 권장
        if health_score < 30:
            recommendations.append("🔴 긴급: 설비 즉시 정지 및 점검 필요")
            recommendations.append("🔴 전문가 상담 권장")
        elif health_score < 50:
            recommendations.append("🟡 주의: 다음 정기 점검 시 세밀히 확인 필요")
            recommendations.append("🟡 측정 빈도 증가 권장")
        elif health_score < 70:
            recommendations.append("🟢 정상: 정기 점검 유지")
        else:
            recommendations.append("✅ 양호: 현재 상태 유지")

        # 고장 예측 기반 권장
        steps = failure_prediction.get('predicted_failure_steps')
        if steps is not None and steps < 20:
            recommendations.append(f"⚠️ 예측된 {steps} 측정 내 규격 이탈 가능성")

        return recommendations
