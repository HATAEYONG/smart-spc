"""
품질 예측 모델
Random Forest 기반 불량 예측 및 품질 점수 예측
"""
import numpy as np
import pickle
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

try:
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import classification_report, confusion_matrix, mean_squared_error, r2_score
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not installed. Install with: pip install scikit-learn")


@dataclass
class PredictionResult:
    """예측 결과"""
    predicted_value: float
    confidence_score: float
    prediction_type: str  # 'defect_probability' or 'quality_score'
    features_used: Dict
    explanation: str
    timestamp: datetime


class DefectPredictor:
    """불량 예측 모델 (분류)"""

    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        """
        Args:
            n_estimators: Random Forest의 트리 개수
            random_state: 랜덤 시드
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required. Install with: pip install scikit-learn")

        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight='balanced'
        )
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False

    def prepare_features(self, data: List[Dict]) -> Tuple[np.ndarray, List[str]]:
        """
        특징 추출

        Args:
            data: [{'measurement': float, 'machine': str, 'operator': str, ...}, ...]

        Returns:
            (features_array, feature_names)
        """
        feature_list = []
        feature_names = []

        for record in data:
            features = []

            # 측정값 통계
            features.append(record.get('measurement_value', 0))
            features.append(record.get('measurement_std', 0))  # 부분군 표준편차
            features.append(record.get('measurement_range', 0))  # 부분군 범위

            # 시간 특징
            hour = record.get('hour_of_day', 0)
            features.append(hour)
            features.append(1 if 6 <= hour < 14 else 0)  # 주간 교대
            features.append(1 if 14 <= hour < 22 else 0)  # 야간 교대

            # 기계 특징
            features.append(record.get('machine_age_days', 0))
            features.append(record.get('machine_usage_hours', 0))
            features.append(record.get('days_since_maintenance', 0))

            # 공정 조건
            features.append(record.get('temperature', 20))
            features.append(record.get('humidity', 50))
            features.append(record.get('pressure', 1))

            # 이전 측정값과의 차이
            features.append(record.get('diff_from_prev', 0))
            features.append(record.get('diff_from_mean', 0))

            # 누적 통계
            features.append(record.get('recent_defect_rate', 0))  # 최근 불량률
            features.append(record.get('consecutive_within_spec', 0))  # 연속 규격 내 개수

            feature_list.append(features)

        if not feature_names:
            feature_names = [
                'measurement_value', 'measurement_std', 'measurement_range',
                'hour_of_day', 'is_day_shift', 'is_night_shift',
                'machine_age_days', 'machine_usage_hours', 'days_since_maintenance',
                'temperature', 'humidity', 'pressure',
                'diff_from_prev', 'diff_from_mean',
                'recent_defect_rate', 'consecutive_within_spec'
            ]

        return np.array(feature_list), feature_names

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        feature_names: Optional[List[str]] = None
    ) -> Dict:
        """
        모델 학습

        Args:
            X_train: 학습 특징 (n_samples, n_features)
            y_train: 학습 레이블 (0: 정상, 1: 불량)
            feature_names: 특징 이름 리스트

        Returns:
            학습 결과 메트릭
        """
        if X_train.shape[0] < 10:
            raise ValueError("최소 10개의 학습 샘플이 필요합니다")

        # 특징 스케일링
        X_train_scaled = self.scaler.fit_transform(X_train)

        # 모델 학습
        self.model.fit(X_train_scaled, y_train)
        self.feature_names = feature_names or [f'feature_{i}' for i in range(X_train.shape[1])]
        self.is_trained = True

        # 교차 검증
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5, scoring='f1')

        # 특징 중요도
        feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
        sorted_importance = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)

        return {
            'training_samples': X_train.shape[0],
            'cv_f1_mean': cv_scores.mean(),
            'cv_f1_std': cv_scores.std(),
            'feature_importance': sorted_importance[:10]  # 상위 10개
        }

    def predict_defect_probability(self, features: np.ndarray) -> PredictionResult:
        """
        불량 발생 확률 예측

        Args:
            features: 특징 배열 (1, n_features)

        Returns:
            PredictionResult
        """
        if not self.is_trained:
            raise ValueError("모델이 학습되지 않았습니다")

        # 스케일링
        features_scaled = self.scaler.transform(features.reshape(1, -1))

        # 예측
        prob = self.model.predict_proba(features_scaled)[0][1]  # 불량 확률
        confidence = max(self.model.predict_proba(features_scaled)[0])

        # 설명 생성
        explanation = self._generate_explanation(features, prob)

        return PredictionResult(
            predicted_value=prob,
            confidence_score=confidence,
            prediction_type='defect_probability',
            features_used={'features': features.tolist()},
            explanation=explanation,
            timestamp=datetime.now()
        )

    def _generate_explanation(self, features: np.ndarray, prob: float) -> str:
        """예측 설명 생성"""
        if prob > 0.7:
            return f"높은 불량 위험 ({prob*100:.1f}%). 즉각적인 공정 점검 필요."
        elif prob > 0.4:
            return f"중간 불량 위험 ({prob*100:.1f}%). 공정 모니터링 강화 권장."
        else:
            return f"낮은 불량 위험 ({prob*100:.1f}%). 정상 범위 내."

    def save_model(self, filepath: str):
        """모델 저장"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'is_trained': self.is_trained
            }, f)

    def load_model(self, filepath: str):
        """모델 로드"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_names = data['feature_names']
            self.is_trained = data['is_trained']


class QualityScorePredictor:
    """품질 점수 예측 모델 (회귀)"""

    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        """
        Args:
            n_estimators: Random Forest의 트리 개수
            random_state: 랜덤 시드
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required")

        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            random_state=random_state,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2
        )
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        feature_names: Optional[List[str]] = None
    ) -> Dict:
        """
        모델 학습

        Args:
            X_train: 학습 특징
            y_train: 품질 점수 (0-100)

        Returns:
            학습 결과 메트릭
        """
        # 특징 스케일링
        X_train_scaled = self.scaler.fit_transform(X_train)

        # 모델 학습
        self.model.fit(X_train_scaled, y_train)
        self.feature_names = feature_names or [f'feature_{i}' for i in range(X_train.shape[1])]
        self.is_trained = True

        # 평가
        y_pred = self.model.predict(X_train_scaled)
        mse = mean_squared_error(y_train, y_pred)
        r2 = r2_score(y_train, y_pred)

        return {
            'training_samples': X_train.shape[0],
            'mse': mse,
            'rmse': np.sqrt(mse),
            'r2_score': r2
        }

    def predict_quality_score(self, features: np.ndarray) -> PredictionResult:
        """
        품질 점수 예측 (0-100)

        Args:
            features: 특징 배열

        Returns:
            PredictionResult
        """
        if not self.is_trained:
            raise ValueError("모델이 학습되지 않았습니다")

        # 스케일링
        features_scaled = self.scaler.transform(features.reshape(1, -1))

        # 예측
        score = self.model.predict(features_scaled)[0]
        score = np.clip(score, 0, 100)  # 0-100 범위로 제한

        # 신뢰도 (예측값의 표준편차 기반)
        tree_predictions = [tree.predict(features_scaled)[0] for tree in self.model.estimators_]
        confidence = 1 - (np.std(tree_predictions) / 100)  # 표준화

        explanation = self._generate_explanation(score)

        return PredictionResult(
            predicted_value=score,
            confidence_score=confidence,
            prediction_type='quality_score',
            features_used={'features': features.tolist()},
            explanation=explanation,
            timestamp=datetime.now()
        )

    def _generate_explanation(self, score: float) -> str:
        """품질 점수 설명 생성"""
        if score >= 90:
            return f"우수한 품질 (점수: {score:.1f}/100)"
        elif score >= 70:
            return f"양호한 품질 (점수: {score:.1f}/100)"
        elif score >= 50:
            return f"보통 품질 (점수: {score:.1f}/100). 개선 검토 필요."
        else:
            return f"낮은 품질 (점수: {score:.1f}/100). 즉각적인 조치 필요."


# 사용 예시
if __name__ == '__main__':
    if SKLEARN_AVAILABLE:
        # 예제 데이터 생성
        np.random.seed(42)
        n_samples = 200

        # 특징 생성
        X = np.random.randn(n_samples, 16)
        # 레이블 생성 (불량 확률이 특징에 의존)
        y = (X[:, 0] + X[:, 1] * 0.5 + np.random.randn(n_samples) * 0.3 > 0.5).astype(int)

        # 학습/테스트 분할
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # 모델 학습
        predictor = DefectPredictor()
        metrics = predictor.train(X_train, y_train)

        print("학습 완료:")
        print(f"- 샘플 수: {metrics['training_samples']}")
        print(f"- CV F1 Score: {metrics['cv_f1_mean']:.3f} ± {metrics['cv_f1_std']:.3f}")
        print(f"\n상위 특징 중요도:")
        for feature, importance in metrics['feature_importance']:
            print(f"  {feature}: {importance:.3f}")

        # 예측
        result = predictor.predict_defect_probability(X_test[0])
        print(f"\n예측 결과:")
        print(f"- 불량 확률: {result.predicted_value*100:.1f}%")
        print(f"- 신뢰도: {result.confidence_score:.3f}")
        print(f"- 설명: {result.explanation}")
    else:
        print("scikit-learn이 설치되지 않아 예시를 실행할 수 없습니다.")
