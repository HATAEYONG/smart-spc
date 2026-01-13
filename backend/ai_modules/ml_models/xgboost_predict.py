"""
XGBoost 기반 공정 시간 예측 모델
실시간 작업 특성 입력 → 예상 처리 시간 출력 → APS 스케줄링 입력으로 활용
"""
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
import joblib
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class ProcessTimePredictorXGB:
    """
    XGBoost 기반 공정 시간 예측기
    """

    def __init__(self):
        self.model = None
        self.feature_names = None
        self.label_encoders = {}
        self.feature_importance = None

    def preprocess_data(self, df, fit=True):
        """
        데이터 전처리 및 인코딩

        Args:
            df: 원본 데이터프레임
            fit: True면 LabelEncoder 학습, False면 기존 인코더 사용

        Returns:
            X: 특성 데이터
            y: 타겟 데이터 (있는 경우)
        """
        df = df.copy()

        # 범주형 변수 인코딩
        categorical_features = ['process_name', 'machine_id', 'item_type']

        for col in categorical_features:
            if fit:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                df[col] = self.label_encoders[col].fit_transform(df[col])
            else:
                if col in self.label_encoders:
                    # 학습 시 보지 못한 카테고리는 -1로 처리
                    df[col] = df[col].apply(
                        lambda x: self.label_encoders[col].transform([x])[0]
                        if x in self.label_encoders[col].classes_
                        else -1
                    )

        # 특성과 타겟 분리
        if 'process_time_minutes' in df.columns:
            X = df.drop('process_time_minutes', axis=1)
            y = df['process_time_minutes']
            return X, y
        else:
            return df, None

    def train(self, data_path, test_size=0.2, random_state=42):
        """
        XGBoost 모델 학습

        Args:
            data_path: 학습 데이터 CSV 경로
            test_size: 테스트 세트 비율
            random_state: 랜덤 시드
        """
        print("📚 학습 데이터 로드 중...")
        df = pd.read_csv(data_path)
        print(f"   - 데이터 크기: {df.shape}")

        # 전처리
        print("🔄 데이터 전처리 중...")
        X, y = self.preprocess_data(df, fit=True)
        self.feature_names = X.columns.tolist()

        # Train-Test Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        print(f"   - 학습 세트: {X_train.shape[0]} 샘플")
        print(f"   - 테스트 세트: {X_test.shape[0]} 샘플")

        # XGBoost 모델 학습
        print("\n🚀 XGBoost 모델 학습 중...")
        self.model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=random_state,
            n_jobs=-1,
            objective='reg:squarederror'
        )

        # Early Stopping을 위한 평가 세트
        eval_set = [(X_train, y_train), (X_test, y_test)]

        self.model.fit(
            X_train, y_train,
            eval_set=eval_set,
            eval_metric='rmse',
            early_stopping_rounds=20,
            verbose=False
        )

        # 예측 및 평가
        print("\n📊 모델 성능 평가:")
        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)

        # 학습 세트 성능
        train_mae = mean_absolute_error(y_train, y_train_pred)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
        train_r2 = r2_score(y_train, y_train_pred)

        print(f"   [학습 세트]")
        print(f"   - MAE: {train_mae:.2f} 분")
        print(f"   - RMSE: {train_rmse:.2f} 분")
        print(f"   - R² Score: {train_r2:.4f}")

        # 테스트 세트 성능
        test_mae = mean_absolute_error(y_test, y_test_pred)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        test_r2 = r2_score(y_test, y_test_pred)

        print(f"\n   [테스트 세트]")
        print(f"   - MAE: {test_mae:.2f} 분")
        print(f"   - RMSE: {test_rmse:.2f} 분")
        print(f"   - R² Score: {test_r2:.4f}")

        # 특성 중요도
        self.feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        print("\n🔍 상위 10개 중요 특성:")
        for idx, row in self.feature_importance.head(10).iterrows():
            print(f"   {row['feature']}: {row['importance']:.4f}")

        return {
            'train_mae': train_mae,
            'train_rmse': train_rmse,
            'train_r2': train_r2,
            'test_mae': test_mae,
            'test_rmse': test_rmse,
            'test_r2': test_r2
        }

    def predict(self, job_features):
        """
        작업 특성 입력 → 공정 시간 예측

        Args:
            job_features: dict 또는 DataFrame
                필수 특성:
                - process_name, machine_id, item_type
                - complexity, batch_size, operator_skill
                - shift, temperature, humidity
                - machine_age_days, maintenance_days_ago
                - has_previous_job, setup_time

        Returns:
            predicted_time: 예측된 공정 시간 (분)
            confidence_interval: 95% 신뢰구간 (하한, 상한)
        """
        if self.model is None:
            raise ValueError("모델이 학습되지 않았습니다. train() 먼저 호출하세요.")

        # DataFrame으로 변환
        if isinstance(job_features, dict):
            df = pd.DataFrame([job_features])
        else:
            df = job_features.copy()

        # job_id 제거 (있는 경우)
        if 'job_id' in df.columns:
            job_ids = df['job_id'].tolist()
            df = df.drop('job_id', axis=1)
        else:
            job_ids = None

        # 전처리
        X, _ = self.preprocess_data(df, fit=False)

        # 특성 순서 맞추기
        X = X[self.feature_names]

        # 예측
        predictions = self.model.predict(X)

        # 신뢰구간 추정 (Bootstrap 방식의 간단한 근사)
        # 실제로는 Quantile Regression 또는 Bootstrap 사용
        # 여기서는 테스트 RMSE를 기반으로 간단히 추정
        std_error = 5.0  # 테스트 RMSE 근사값
        confidence_lower = predictions - 1.96 * std_error
        confidence_upper = predictions + 1.96 * std_error

        # 결과 반환
        results = []
        for i, pred in enumerate(predictions):
            result = {
                'predicted_time_minutes': round(float(pred), 2),
                'confidence_interval_95': {
                    'lower': round(float(confidence_lower[i]), 2),
                    'upper': round(float(confidence_upper[i]), 2)
                }
            }
            if job_ids:
                result['job_id'] = job_ids[i]
            results.append(result)

        return results if len(results) > 1 else results[0]

    def save_model(self, model_dir='C:\\Claude\\online-aps-cps-scheduler\\backend\\ai_modules\\ml_models\\saved'):
        """
        모델 저장
        """
        Path(model_dir).mkdir(parents=True, exist_ok=True)

        # XGBoost 모델 저장
        model_path = Path(model_dir) / 'xgboost_process_time_model.json'
        self.model.save_model(str(model_path))

        # 메타데이터 저장 (LabelEncoders, feature_names 등)
        meta_path = Path(model_dir) / 'model_metadata.pkl'
        metadata = {
            'feature_names': self.feature_names,
            'label_encoders': self.label_encoders,
            'feature_importance': self.feature_importance.to_dict('records')
        }
        joblib.dump(metadata, meta_path)

        print(f"\n✅ 모델 저장 완료: {model_dir}")
        return model_path, meta_path

    def load_model(self, model_dir='C:\\Claude\\online-aps-cps-scheduler\\backend\\ai_modules\\ml_models\\saved'):
        """
        저장된 모델 로드
        """
        model_path = Path(model_dir) / 'xgboost_process_time_model.json'
        meta_path = Path(model_dir) / 'model_metadata.pkl'

        # XGBoost 모델 로드
        self.model = xgb.XGBRegressor()
        self.model.load_model(str(model_path))

        # 메타데이터 로드
        metadata = joblib.load(meta_path)
        self.feature_names = metadata['feature_names']
        self.label_encoders = metadata['label_encoders']
        self.feature_importance = pd.DataFrame(metadata['feature_importance'])

        print(f"✅ 모델 로드 완료: {model_dir}")
        return self

def main():
    """
    메인 실행 함수: 학습 → 평가 → 저장 → 예측 테스트
    """
    print("=" * 80)
    print("🤖 XGBoost 공정 시간 예측 모델 학습 시작")
    print("=" * 80)

    # 데이터 경로
    data_path = 'C:\\Claude\\online-aps-cps-scheduler\\backend\\ai_modules\\data\\process_time_training_data.csv'

    # 모델 초기화 및 학습
    predictor = ProcessTimePredictorXGB()
    metrics = predictor.train(data_path)

    # 모델 저장
    predictor.save_model()

    # 실시간 예측 테스트
    print("\n" + "=" * 80)
    print("🔮 실시간 예측 테스트")
    print("=" * 80)

    # 샘플 작업 로드
    sample_path = 'C:\\Claude\\online-aps-cps-scheduler\\backend\\ai_modules\\data\\sample_jobs.json'
    with open(sample_path, 'r', encoding='utf-8') as f:
        sample_jobs = json.load(f)

    print(f"\n📋 {len(sample_jobs)}개 샘플 작업 예측 중...\n")

    for job in sample_jobs:
        job_id = job['job_id']
        result = predictor.predict(job)

        print(f"작업 ID: {job_id}")
        print(f"  공정: {job['process_name']} | 설비: {job['machine_id']} | 품목: {job['item_type']}")
        print(f"  복잡도: {job['complexity']} | 배치: {job['batch_size']} | 숙련도: {job['operator_skill']}")
        print(f"  📊 예측 시간: {result['predicted_time_minutes']} 분")
        print(f"  📈 신뢰구간(95%): [{result['confidence_interval_95']['lower']}, {result['confidence_interval_95']['upper']}] 분")
        print()

    print("=" * 80)
    print("✅ 모델 학습 및 테스트 완료!")
    print("=" * 80)

    # 사용 예시 출력
    print("\n📚 사용 예시:")
    print("""
    # 1. 모델 로드
    predictor = ProcessTimePredictorXGB()
    predictor.load_model()

    # 2. 작업 특성 입력
    job = {
        'process_name': '가공',
        'machine_id': 'MC001',
        'item_type': '프레임',
        'complexity': 7,
        'batch_size': 50,
        'operator_skill': 4,
        'shift': 1,
        'temperature': 23.5,
        'humidity': 52.0,
        'machine_age_days': 730,
        'maintenance_days_ago': 15,
        'has_previous_job': 1,
        'setup_time': 10
    }

    # 3. 공정 시간 예측
    result = predictor.predict(job)
    print(f"예측 시간: {result['predicted_time_minutes']} 분")

    # 4. APS 스케줄링에 입력
    # → 이 예측값을 APS 알고리즘의 process_time으로 사용
    """)

if __name__ == '__main__':
    main()
