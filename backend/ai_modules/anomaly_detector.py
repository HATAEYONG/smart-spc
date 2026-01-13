"""
이상 탐지 모델
Isolation Forest 기반 실시간 품질 이상 탐지
"""
import numpy as np
import pickle
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.covariance import EllipticEnvelope
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not installed")


@dataclass
class AnomalyDetectionResult:
    """이상 탐지 결과"""
    is_anomaly: bool
    anomaly_score: float  # -1 ~ 1 (음수일수록 이상)
    severity: int  # 1=낮음, 2=보통, 3=높음
    explanation: str
    detected_at: datetime
    features_analyzed: Dict


class IsolationForestDetector:
    """Isolation Forest 기반 이상 탐지"""

    def __init__(
        self,
        contamination: float = 0.1,
        n_estimators: int = 100,
        random_state: int = 42
    ):
        """
        Args:
            contamination: 예상 이상치 비율 (0.0 ~ 0.5)
            n_estimators: 트리 개수
            random_state: 랜덤 시드
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required")

        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=random_state,
            max_samples='auto',
            max_features=1.0
        )
        self.scaler = StandardScaler()
        self.is_fitted = False

        # 정상 데이터 통계 (설명 생성용)
        self.feature_means = None
        self.feature_stds = None

    def fit(self, X: np.ndarray) -> Dict:
        """
        정상 데이터로 모델 학습

        Args:
            X: 정상 데이터 (n_samples, n_features)

        Returns:
            학습 결과 메트릭
        """
        if X.shape[0] < 10:
            raise ValueError("최소 10개의 샘플이 필요합니다")

        # 특징 스케일링
        X_scaled = self.scaler.fit_transform(X)

        # 모델 학습
        self.model.fit(X_scaled)
        self.is_fitted = True

        # 정상 데이터 통계 저장
        self.feature_means = np.mean(X, axis=0)
        self.feature_stds = np.std(X, axis=0)

        # 학습 데이터에서 이상치 개수 파악
        predictions = self.model.predict(X_scaled)
        n_anomalies = np.sum(predictions == -1)

        return {
            'training_samples': X.shape[0],
            'detected_anomalies': n_anomalies,
            'anomaly_rate': n_anomalies / X.shape[0]
        }

    def detect(self, features: np.ndarray) -> AnomalyDetectionResult:
        """
        이상 탐지 실행

        Args:
            features: 특징 배열 (n_features,)

        Returns:
            AnomalyDetectionResult
        """
        if not self.is_fitted:
            raise ValueError("모델이 학습되지 않았습니다")

        # 스케일링
        features_scaled = self.scaler.transform(features.reshape(1, -1))

        # 예측
        prediction = self.model.predict(features_scaled)[0]  # -1 or 1
        anomaly_score = self.model.score_samples(features_scaled)[0]

        is_anomaly = (prediction == -1)

        # 심각도 계산
        severity = self._calculate_severity(anomaly_score)

        # 설명 생성
        explanation = self._generate_explanation(features, anomaly_score, is_anomaly)

        return AnomalyDetectionResult(
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            severity=severity,
            explanation=explanation,
            detected_at=datetime.now(),
            features_analyzed={'features': features.tolist(), 'score': float(anomaly_score)}
        )

    def _calculate_severity(self, anomaly_score: float) -> int:
        """
        이상 점수 기반 심각도 계산

        Args:
            anomaly_score: Isolation Forest 점수 (음수일수록 이상)

        Returns:
            1=낮음, 2=보통, 3=높음
        """
        if anomaly_score > -0.1:
            return 1  # 정상 또는 경미한 이상
        elif anomaly_score > -0.3:
            return 2  # 보통 이상
        else:
            return 3  # 높은 이상

    def _generate_explanation(
        self,
        features: np.ndarray,
        score: float,
        is_anomaly: bool
    ) -> str:
        """이상 탐지 설명 생성"""
        if not is_anomaly:
            return f"정상 범위 내 (점수: {score:.3f})"

        # 정상 범위와 비교
        if self.feature_means is not None and self.feature_stds is not None:
            deviations = np.abs(features - self.feature_means) / (self.feature_stds + 1e-10)
            max_deviation_idx = np.argmax(deviations)
            max_deviation = deviations[max_deviation_idx]

            return (
                f"이상 패턴 감지 (점수: {score:.3f}). "
                f"특징 {max_deviation_idx}가 정상 범위에서 {max_deviation:.1f}σ 벗어남."
            )
        else:
            return f"이상 패턴 감지 (점수: {score:.3f})"

    def save_model(self, filepath: str):
        """모델 저장"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'is_fitted': self.is_fitted,
                'feature_means': self.feature_means,
                'feature_stds': self.feature_stds
            }, f)

    def load_model(self, filepath: str):
        """모델 로드"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.scaler = data['scaler']
            self.is_fitted = data['is_fitted']
            self.feature_means = data['feature_means']
            self.feature_stds = data['feature_stds']


class StatisticalAnomalyDetector:
    """통계적 이상 탐지 (Multivariate Gaussian)"""

    def __init__(self):
        """Mahalanobis Distance 기반 이상 탐지"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required")

        self.model = EllipticEnvelope(contamination=0.1, support_fraction=0.8)
        self.is_fitted = False

    def fit(self, X: np.ndarray) -> Dict:
        """
        정상 데이터로 모델 학습

        Args:
            X: 정상 데이터

        Returns:
            학습 결과
        """
        self.model.fit(X)
        self.is_fitted = True

        predictions = self.model.predict(X)
        n_anomalies = np.sum(predictions == -1)

        return {
            'training_samples': X.shape[0],
            'detected_anomalies': n_anomalies
        }

    def detect(self, features: np.ndarray) -> AnomalyDetectionResult:
        """이상 탐지"""
        if not self.is_fitted:
            raise ValueError("모델이 학습되지 않았습니다")

        prediction = self.model.predict(features.reshape(1, -1))[0]
        mahalanobis_dist = self.model.mahalanobis(features.reshape(1, -1))[0]

        is_anomaly = (prediction == -1)
        severity = 3 if mahalanobis_dist > 10 else (2 if mahalanobis_dist > 5 else 1)

        explanation = (
            f"Mahalanobis Distance: {mahalanobis_dist:.2f}. "
            f"{'이상 패턴 감지' if is_anomaly else '정상 범위'}"
        )

        return AnomalyDetectionResult(
            is_anomaly=is_anomaly,
            anomaly_score=-mahalanobis_dist,  # 음수로 변환 (일관성 위해)
            severity=severity,
            explanation=explanation,
            detected_at=datetime.now(),
            features_analyzed={'mahalanobis_distance': float(mahalanobis_dist)}
        )


class RealTimeAnomalyMonitor:
    """실시간 이상 탐지 모니터"""

    def __init__(self, detector: IsolationForestDetector):
        """
        Args:
            detector: 학습된 이상 탐지 모델
        """
        self.detector = detector
        self.alert_history = []
        self.consecutive_anomalies = 0

    def check_measurement(
        self,
        measurement_value: float,
        features: np.ndarray
    ) -> Dict:
        """
        측정값 실시간 체크

        Args:
            measurement_value: 측정값
            features: 관련 특징들

        Returns:
            {
                'is_anomaly': bool,
                'alert_level': 'none' | 'warning' | 'critical',
                'result': AnomalyDetectionResult,
                'recommendation': str
            }
        """
        result = self.detector.detect(features)

        # 연속 이상 카운트
        if result.is_anomaly:
            self.consecutive_anomalies += 1
        else:
            self.consecutive_anomalies = 0

        # 경고 수준 결정
        if self.consecutive_anomalies >= 3:
            alert_level = 'critical'
            recommendation = "3회 연속 이상 감지. 즉시 공정 점검 필요."
        elif result.is_anomaly:
            alert_level = 'warning'
            recommendation = "이상 패턴 감지. 모니터링 강화."
        else:
            alert_level = 'none'
            recommendation = "정상 범위 내."

        # 이력 저장
        self.alert_history.append({
            'timestamp': result.detected_at,
            'measurement': measurement_value,
            'is_anomaly': result.is_anomaly,
            'score': result.anomaly_score
        })

        # 최근 100개만 유지
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]

        return {
            'is_anomaly': result.is_anomaly,
            'alert_level': alert_level,
            'result': result,
            'recommendation': recommendation,
            'consecutive_anomalies': self.consecutive_anomalies
        }

    def get_statistics(self) -> Dict:
        """모니터링 통계"""
        if not self.alert_history:
            return {'total': 0, 'anomalies': 0, 'anomaly_rate': 0}

        total = len(self.alert_history)
        anomalies = sum(1 for h in self.alert_history if h['is_anomaly'])

        return {
            'total_measurements': total,
            'anomaly_count': anomalies,
            'anomaly_rate': anomalies / total,
            'consecutive_anomalies': self.consecutive_anomalies
        }


# 사용 예시
if __name__ == '__main__':
    if SKLEARN_AVAILABLE:
        # 정상 데이터 생성
        np.random.seed(42)
        X_normal = np.random.randn(200, 5) * 0.5

        # 이상 데이터 생성
        X_anomaly = np.random.randn(20, 5) * 3.0

        # 모델 학습
        detector = IsolationForestDetector(contamination=0.1)
        metrics = detector.fit(X_normal)

        print("학습 완료:")
        print(f"- 학습 샘플: {metrics['training_samples']}")
        print(f"- 탐지된 이상: {metrics['detected_anomalies']}")

        # 정상 데이터 테스트
        result_normal = detector.detect(X_normal[0])
        print(f"\n정상 데이터 테스트:")
        print(f"- 이상 여부: {result_normal.is_anomaly}")
        print(f"- 점수: {result_normal.anomaly_score:.3f}")
        print(f"- 설명: {result_normal.explanation}")

        # 이상 데이터 테스트
        result_anomaly = detector.detect(X_anomaly[0])
        print(f"\n이상 데이터 테스트:")
        print(f"- 이상 여부: {result_anomaly.is_anomaly}")
        print(f"- 점수: {result_anomaly.anomaly_score:.3f}")
        print(f"- 심각도: {result_anomaly.severity}")
        print(f"- 설명: {result_anomaly.explanation}")

        # 실시간 모니터
        monitor = RealTimeAnomalyMonitor(detector)
        check = monitor.check_measurement(10.5, X_anomaly[0])
        print(f"\n실시간 체크:")
        print(f"- 경고 수준: {check['alert_level']}")
        print(f"- 권장 조치: {check['recommendation']}")
    else:
        print("scikit-learn이 설치되지 않아 예시를 실행할 수 없습니다.")
