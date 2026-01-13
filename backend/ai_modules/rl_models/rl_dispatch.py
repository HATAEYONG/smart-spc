"""
RL 기반 최적 스케줄링 실행 스크립트
학습된 PPO 에이전트를 사용하여 실제 작업 스케줄링
"""
from stable_baselines3 import PPO
from aps_rl_env import APSSchedulingEnv
import numpy as np
import pandas as pd
from pathlib import Path
import json
from typing import List, Dict

class RLScheduler:
    """
    RL 기반 스케줄러
    """

    def __init__(self, model_path: str):
        """
        초기화

        Args:
            model_path: 학습된 PPO 모델 경로
        """
        print(f"🔄 RL 모델 로드 중: {model_path}")
        self.model = PPO.load(model_path)
        print(f"✅ 모델 로드 완료")

    def schedule_jobs(
        self,
        jobs: List[Dict],
        machines: List[Dict],
        deterministic: bool = True
    ) -> Dict:
        """
        작업 스케줄링 실행

        Args:
            jobs: 작업 리스트
                각 작업: {
                    'job_id': str,
                    'process_time': int,
                    'due_date': int,
                    'priority': int,
                    'machine_eligibility': List[bool]  # 설비별 적합성
                }
            machines: 설비 리스트
                각 설비: {
                    'machine_id': str
                }
            deterministic: 결정적 예측 여부 (True 권장)

        Returns:
            스케줄 결과: {
                'schedule': [{'job_id', 'machine_id', 'start_time', 'end_time'}, ...],
                'metrics': {'total_tardiness', 'makespan', 'utilization'},
                'gantt_data': DataFrame
            }
        """
        print(f"\n📅 스케줄링 시작 (작업: {len(jobs)}, 설비: {len(machines)})")

        # 환경 생성 및 초기화
        env_config = {
            'n_machines': len(machines),
            'n_jobs': len(jobs),
            'max_process_time': max(job['process_time'] for job in jobs),
            'max_due_date': max(job['due_date'] for job in jobs)
        }

        env = APSSchedulingEnv(config=env_config)

        # 작업 데이터 설정
        env.jobs = jobs
        env.n_jobs = len(jobs)
        env.n_machines = len(machines)
        env.machine_available_times = np.zeros(len(machines), dtype=np.float32)
        env.scheduled_jobs = np.zeros(len(jobs), dtype=bool)
        env.total_tardiness = 0.0
        env.total_makespan = 0.0

        # 초기 관찰
        observation = env._get_observation()

        # 스케줄링 실행
        schedule = []
        step = 0

        while not env.scheduled_jobs.all():
            step += 1

            # RL 에이전트가 액션 선택
            action, _states = self.model.predict(observation, deterministic=deterministic)

            # 액션 실행
            observation, reward, terminated, truncated, info = env.step(action)

            # 액션 디코딩
            job_idx = action // env.n_machines
            machine_idx = action % env.n_machines

            # 스케줄 기록 (유효한 액션인 경우)
            if reward > -100:  # Invalid action 아닌 경우
                job = env.jobs[job_idx]
                machine = machines[machine_idx]

                start_time = env.machine_available_times[machine_idx] - job['process_time']
                end_time = env.machine_available_times[machine_idx]

                schedule_entry = {
                    'job_id': job.get('job_id', f'JOB{job_idx:03d}'),
                    'machine_id': machine['machine_id'],
                    'start_time': start_time,
                    'end_time': end_time,
                    'process_time': job['process_time'],
                    'due_date': job['due_date'],
                    'tardiness': max(0, end_time - job['due_date'])
                }
                schedule.append(schedule_entry)

            if terminated or truncated:
                break

        # 최종 메트릭
        metrics = {
            'total_tardiness': info['total_tardiness'],
            'makespan': info['makespan'],
            'utilization': info['utilization'],
            'scheduled_jobs': info['scheduled_jobs']
        }

        # Gantt 차트용 데이터
        gantt_df = pd.DataFrame(schedule)

        print(f"\n✅ 스케줄링 완료")
        print(f"   스케줄된 작업: {len(schedule)} / {len(jobs)}")
        print(f"   총 Tardiness: {metrics['total_tardiness']:.2f}")
        print(f"   Makespan: {metrics['makespan']:.2f}")
        print(f"   평균 가동률: {metrics['utilization']:.2f}")

        return {
            'schedule': schedule,
            'metrics': metrics,
            'gantt_data': gantt_df
        }

    def export_schedule(self, result: Dict, output_path: str):
        """
        스케줄 결과 내보내기 (JSON + CSV)
        """
        output_path = Path(output_path)

        # JSON 저장
        json_path = output_path.with_suffix('.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            # DataFrame은 직렬화 불가능하므로 제외
            export_data = {
                'schedule': result['schedule'],
                'metrics': result['metrics']
            }
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        print(f"   JSON 저장: {json_path}")

        # CSV 저장
        csv_path = output_path.with_suffix('.csv')
        result['gantt_data'].to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"   CSV 저장: {csv_path}")

def example_usage():
    """
    사용 예시
    """
    print("=" * 80)
    print("🚀 RL 기반 스케줄링 실행 예시")
    print("=" * 80)

    # 1. 모델 로드
    model_path = Path(__file__).parent / 'saved_models' / 'best_model' / 'best_model.zip'

    if not model_path.exists():
        print(f"\n⚠️  모델이 존재하지 않습니다: {model_path}")
        print("   먼저 'python train_rl_agent.py train'을 실행하여 모델을 학습하세요.")
        return

    scheduler = RLScheduler(str(model_path))

    # 2. 샘플 작업 및 설비 생성
    print("\n📋 샘플 데이터 생성 중...")

    machines = [
        {'machine_id': f'MC{i+1:03d}'}
        for i in range(5)
    ]

    np.random.seed(42)
    jobs = []
    for i in range(20):
        job = {
            'job_id': f'JOB{i+1:03d}',
            'process_time': int(np.random.randint(10, 100)),
            'due_date': int(np.random.randint(50, 500)),
            'priority': int(np.random.randint(1, 11)),
            'machine_eligibility': [True] * 5  # 모든 설비에서 가능
        }
        jobs.append(job)

    # 3. 스케줄링 실행
    result = scheduler.schedule_jobs(jobs, machines)

    # 4. 결과 출력
    print("\n📊 스케줄 결과 (처음 10개):")
    for entry in result['schedule'][:10]:
        print(f"   {entry['job_id']} → {entry['machine_id']}: "
              f"[{entry['start_time']:.1f} - {entry['end_time']:.1f}] "
              f"(Tardiness: {entry['tardiness']:.1f})")

    # 5. 내보내기
    output_path = Path(__file__).parent / 'schedule_result'
    scheduler.export_schedule(result, str(output_path))

    print("\n" + "=" * 80)
    print("✅ 예시 완료!")
    print("=" * 80)

if __name__ == '__main__':
    example_usage()
