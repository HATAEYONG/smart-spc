"""
샘플 학습 데이터 생성기
공정 시간 예측을 위한 이력 데이터 생성
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

np.random.seed(42)

def generate_process_time_data(n_samples=5000):
    """
    공정 시간 예측을 위한 학습 데이터 생성

    Features:
    - process_name: 공정명 (가공, 조립, 도장, 검사)
    - machine_id: 설비 ID (MC001-MC006)
    - previous_job: 이전 작업 ID
    - item_type: 품목 유형 (프레임, 브라켓, 하우징 등)
    - complexity: 복잡도 (1-10)
    - batch_size: 배치 크기 (1-100)
    - operator_skill: 작업자 숙련도 (1-5)
    - shift: 교대조 (1=주간, 2=야간)
    - temperature: 작업장 온도 (15-35°C)
    - humidity: 습도 (30-80%)
    - machine_age_days: 설비 사용 일수
    - maintenance_days_ago: 마지막 보수 후 경과일

    Target:
    - process_time_minutes: 실제 공정 소요 시간 (분)
    """

    # 공정 유형별 기본 시간 (분)
    process_base_times = {
        '가공': 45,
        '조립': 60,
        '도장': 35,
        '검사': 20,
        '포장': 15
    }

    # 설비별 효율 계수
    machine_efficiency = {
        'MC001': 1.0,  # 표준
        'MC002': 0.95,  # 5% 느림
        'MC003': 1.1,   # 10% 빠름
        'MC004': 0.9,   # 10% 빠름
        'MC005': 1.05,  # 5% 느림
        'MC006': 0.85   # 15% 빠름 (신규 설비)
    }

    # 품목 유형별 난이도 계수
    item_difficulty = {
        '프레임': 1.0,
        '브라켓': 0.8,
        '하우징': 1.2,
        '모터': 1.5,
        '케이블': 0.6
    }

    data = []

    for i in range(n_samples):
        # 기본 특성 생성
        process_name = np.random.choice(list(process_base_times.keys()))
        machine_id = np.random.choice(list(machine_efficiency.keys()))
        item_type = np.random.choice(list(item_difficulty.keys()))

        base_time = process_base_times[process_name]
        machine_coef = machine_efficiency[machine_id]
        item_coef = item_difficulty[item_type]

        # 추가 특성
        complexity = np.random.randint(1, 11)
        batch_size = np.random.randint(1, 101)
        operator_skill = np.random.randint(1, 6)
        shift = np.random.choice([1, 2])  # 1=주간, 2=야간
        temperature = np.random.uniform(15, 35)
        humidity = np.random.uniform(30, 80)
        machine_age_days = np.random.randint(0, 1825)  # 0-5년
        maintenance_days_ago = np.random.randint(0, 90)

        # 이전 작업 영향 (설정 시간)
        has_previous_job = np.random.choice([0, 1], p=[0.3, 0.7])
        setup_time = 0
        if has_previous_job:
            # 같은 품목이면 설정 시간 짧음, 다른 품목이면 길음
            same_item = np.random.choice([0, 1], p=[0.4, 0.6])
            setup_time = 5 if same_item else 15

        # 공정 시간 계산 (실제값)
        # 기본 시간 × 설비 계수 × 품목 계수
        estimated_time = base_time * machine_coef * item_coef

        # 복잡도 영향 (+0~50%)
        complexity_factor = 1 + (complexity - 1) * 0.05

        # 배치 크기 영향 (규모의 경제, 배치 클수록 단위당 시간 감소)
        batch_factor = 1 - (np.log(batch_size) / 10)
        batch_factor = max(0.7, batch_factor)  # 최소 30% 감소

        # 작업자 숙련도 영향 (숙련도 높을수록 빠름)
        operator_factor = 1 - (operator_skill - 1) * 0.08

        # 교대조 영향 (야간은 5% 느림)
        shift_factor = 1.05 if shift == 2 else 1.0

        # 환경 영향 (온도/습도 최적 범위에서 벗어나면 느려짐)
        temp_optimal = 23
        humid_optimal = 50
        temp_deviation = abs(temperature - temp_optimal) / 10
        humid_deviation = abs(humidity - humid_optimal) / 20
        env_factor = 1 + temp_deviation * 0.02 + humid_deviation * 0.01

        # 설비 노후화 영향 (1000일마다 5% 느려짐)
        aging_factor = 1 + (machine_age_days / 1000) * 0.05

        # 보수 후 경과일 영향 (보수 직후는 빠름, 시간 지날수록 느려짐)
        maintenance_factor = 1 + (maintenance_days_ago / 90) * 0.1

        # 최종 공정 시간 계산
        process_time = estimated_time * complexity_factor * batch_factor * \
                       operator_factor * shift_factor * env_factor * \
                       aging_factor * maintenance_factor + setup_time

        # 랜덤 노이즈 추가 (±10%)
        noise = np.random.normal(1.0, 0.1)
        process_time = process_time * noise

        # 최소 시간 제한
        process_time = max(10, process_time)

        # 데이터 저장
        data.append({
            'process_name': process_name,
            'machine_id': machine_id,
            'item_type': item_type,
            'complexity': complexity,
            'batch_size': batch_size,
            'operator_skill': operator_skill,
            'shift': shift,
            'temperature': round(temperature, 2),
            'humidity': round(humidity, 2),
            'machine_age_days': machine_age_days,
            'maintenance_days_ago': maintenance_days_ago,
            'has_previous_job': has_previous_job,
            'setup_time': setup_time,
            'process_time_minutes': round(process_time, 2)
        })

    return pd.DataFrame(data)

def generate_realtime_features():
    """
    실시간 예측용 샘플 특성 생성
    """
    sample_jobs = [
        {
            'job_id': 'JOB001',
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
        },
        {
            'job_id': 'JOB002',
            'process_name': '조립',
            'machine_id': 'MC002',
            'item_type': '하우징',
            'complexity': 8,
            'batch_size': 30,
            'operator_skill': 3,
            'shift': 1,
            'temperature': 24.0,
            'humidity': 55.0,
            'machine_age_days': 1095,
            'maintenance_days_ago': 45,
            'has_previous_job': 0,
            'setup_time': 0
        },
        {
            'job_id': 'JOB003',
            'process_name': '도장',
            'machine_id': 'MC003',
            'item_type': '브라켓',
            'complexity': 5,
            'batch_size': 80,
            'operator_skill': 5,
            'shift': 2,
            'temperature': 22.0,
            'humidity': 48.0,
            'machine_age_days': 365,
            'maintenance_days_ago': 7,
            'has_previous_job': 1,
            'setup_time': 5
        }
    ]

    return sample_jobs

if __name__ == '__main__':
    print("🔄 공정 시간 예측 학습 데이터 생성 중...")

    # 학습 데이터 생성
    df_train = generate_process_time_data(n_samples=5000)

    # 데이터 저장
    output_path = 'C:\\Claude\\online-aps-cps-scheduler\\backend\\ai_modules\\data\\process_time_training_data.csv'
    df_train.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ 학습 데이터 생성 완료: {output_path}")
    print(f"   - 샘플 수: {len(df_train)}")
    print(f"   - 특성 수: {len(df_train.columns) - 1}")

    # 기술 통계 출력
    print("\n📊 데이터 통계:")
    print(df_train['process_time_minutes'].describe())

    print("\n📋 공정별 평균 시간:")
    print(df_train.groupby('process_name')['process_time_minutes'].mean().round(2))

    print("\n🏭 설비별 평균 시간:")
    print(df_train.groupby('machine_id')['process_time_minutes'].mean().round(2))

    # 실시간 예측용 샘플 저장
    sample_jobs = generate_realtime_features()
    sample_path = 'C:\\Claude\\online-aps-cps-scheduler\\backend\\ai_modules\\data\\sample_jobs.json'
    with open(sample_path, 'w', encoding='utf-8') as f:
        json.dump(sample_jobs, f, indent=2, ensure_ascii=False)
    print(f"\n✅ 샘플 작업 데이터 생성 완료: {sample_path}")
    print(f"   - 샘플 작업 수: {len(sample_jobs)}")
