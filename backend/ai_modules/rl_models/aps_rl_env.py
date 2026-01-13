"""
APS 작업 스케줄링을 위한 강화학습 환경 (OpenAI Gym)
순차 공정 + 설비 제약 하에 지연 시간 최소화
"""
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Dict, List, Tuple, Optional
import json

class APSSchedulingEnv(gym.Env):
    """
    APS 작업 스케줄링 강화학습 환경

    State:
    - 각 설비의 현재 가용 시간
    - 각 작업의 처리 시간, 납기, 우선순위
    - 현재까지 스케줄된 작업 수

    Action:
    - 다음에 스케줄할 (작업, 설비) 쌍 선택

    Reward:
    - 납기 준수: +100
    - 납기 지연: -지연시간
    - 설비 가동률 균형: +10
    - 에피소드 완료 시 전체 Makespan에 따른 보너스
    """

    metadata = {'render_modes': ['human']}

    def __init__(self, config: Optional[Dict] = None):
        super().__init__()

        # 환경 설정
        self.config = config or self._default_config()
        self.n_machines = self.config['n_machines']
        self.n_jobs = self.config['n_jobs']
        self.max_process_time = self.config['max_process_time']

        # Observation Space
        # [machine_available_times (n_machines),
        #  job_process_times (n_jobs),
        #  job_due_dates (n_jobs),
        #  job_priorities (n_jobs),
        #  job_scheduled_flags (n_jobs)]
        obs_dim = self.n_machines + self.n_jobs * 4
        self.observation_space = spaces.Box(
            low=0,
            high=np.inf,
            shape=(obs_dim,),
            dtype=np.float32
        )

        # Action Space
        # Discrete action: job_index * n_machines + machine_index
        # 예: job 3를 machine 2에 할당 = 3 * n_machines + 2
        self.action_space = spaces.Discrete(self.n_jobs * self.n_machines)

        # 환경 변수 초기화
        self.machine_available_times = None
        self.jobs = None
        self.scheduled_jobs = None
        self.current_time = None
        self.total_tardiness = None
        self.total_makespan = None

    def _default_config(self) -> Dict:
        """
        기본 환경 설정
        """
        return {
            'n_machines': 5,
            'n_jobs': 20,
            'max_process_time': 100,
            'max_due_date': 500,
            'max_priority': 10,
            'tardiness_penalty': 2.0,
            'makespan_penalty': 0.5,
            'balance_reward': 10.0
        }

    def reset(self, seed=None, options=None):
        """
        환경 초기화

        Returns:
            observation: 초기 상태
            info: 추가 정보
        """
        super().reset(seed=seed)

        # 설비 가용 시간 초기화 (모두 0에서 시작)
        self.machine_available_times = np.zeros(self.n_machines, dtype=np.float32)

        # 작업 생성
        self.jobs = self._generate_jobs()

        # 스케줄된 작업 플래그
        self.scheduled_jobs = np.zeros(self.n_jobs, dtype=bool)

        # 현재 시간
        self.current_time = 0.0

        # 성능 지표 초기화
        self.total_tardiness = 0.0
        self.total_makespan = 0.0

        # 초기 관찰 반환
        observation = self._get_observation()
        info = self._get_info()

        return observation, info

    def _generate_jobs(self) -> List[Dict]:
        """
        랜덤 작업 생성
        """
        jobs = []
        for i in range(self.n_jobs):
            job = {
                'job_id': i,
                'process_time': self.np_random.integers(10, self.max_process_time + 1),
                'due_date': self.np_random.integers(50, self.config['max_due_date'] + 1),
                'priority': self.np_random.integers(1, self.config['max_priority'] + 1),
                'machine_eligibility': self._generate_machine_eligibility()
            }
            jobs.append(job)
        return jobs

    def _generate_machine_eligibility(self) -> np.ndarray:
        """
        작업별 설비 적합성 생성 (일부 작업은 특정 설비에서만 가능)
        """
        # 80% 확률로 모든 설비 가능, 20% 확률로 일부 설비만 가능
        if self.np_random.random() < 0.8:
            return np.ones(self.n_machines, dtype=bool)
        else:
            eligibility = self.np_random.random(self.n_machines) > 0.5
            # 최소 1개 설비는 가능하도록
            if not eligibility.any():
                eligibility[self.np_random.integers(0, self.n_machines)] = True
            return eligibility

    def _get_observation(self) -> np.ndarray:
        """
        현재 상태 관찰 생성
        """
        # Machine available times
        machine_times = self.machine_available_times.copy()

        # Job process times
        job_process_times = np.array([job['process_time'] for job in self.jobs], dtype=np.float32)

        # Job due dates
        job_due_dates = np.array([job['due_date'] for job in self.jobs], dtype=np.float32)

        # Job priorities
        job_priorities = np.array([job['priority'] for job in self.jobs], dtype=np.float32)

        # Job scheduled flags
        job_scheduled = self.scheduled_jobs.astype(np.float32)

        # 모든 관찰 결합
        observation = np.concatenate([
            machine_times,
            job_process_times,
            job_due_dates,
            job_priorities,
            job_scheduled
        ])

        return observation

    def _get_info(self) -> Dict:
        """
        추가 정보 반환
        """
        return {
            'total_tardiness': self.total_tardiness,
            'makespan': self.total_makespan,
            'scheduled_jobs': self.scheduled_jobs.sum(),
            'utilization': self.machine_available_times.mean()
        }

    def step(self, action: int):
        """
        행동 실행

        Args:
            action: job_index * n_machines + machine_index

        Returns:
            observation: 다음 상태
            reward: 보상
            terminated: 에피소드 종료 여부
            truncated: 에피소드 중단 여부
            info: 추가 정보
        """
        # Action 디코딩
        job_idx = action // self.n_machines
        machine_idx = action % self.n_machines

        # Invalid action 체크
        reward = 0.0
        terminated = False
        truncated = False

        # 1. 이미 스케줄된 작업인지 체크
        if self.scheduled_jobs[job_idx]:
            reward = -100  # 큰 패널티
            observation = self._get_observation()
            info = self._get_info()
            return observation, reward, terminated, truncated, info

        # 2. 설비 적합성 체크
        if not self.jobs[job_idx]['machine_eligibility'][machine_idx]:
            reward = -100  # 큰 패널티
            observation = self._get_observation()
            info = self._get_info()
            return observation, reward, terminated, truncated, info

        # 3. 작업 스케줄링
        job = self.jobs[job_idx]
        process_time = job['process_time']
        due_date = job['due_date']

        # 작업 시작 시간 = 설비 가용 시간
        start_time = self.machine_available_times[machine_idx]
        completion_time = start_time + process_time

        # 설비 가용 시간 업데이트
        self.machine_available_times[machine_idx] = completion_time

        # 스케줄 플래그 업데이트
        self.scheduled_jobs[job_idx] = True

        # 4. 보상 계산
        # 4-1. 납기 준수/지연
        tardiness = max(0, completion_time - due_date)
        if tardiness == 0:
            reward += 100  # 납기 준수 보너스
        else:
            reward -= tardiness * self.config['tardiness_penalty']  # 지연 패널티

        self.total_tardiness += tardiness

        # 4-2. 우선순위 고려
        priority_bonus = job['priority'] * 5
        reward += priority_bonus

        # 5. 에피소드 종료 체크
        if self.scheduled_jobs.all():
            terminated = True

            # 5-1. Makespan 계산
            self.total_makespan = self.machine_available_times.max()
            makespan_penalty = self.total_makespan * self.config['makespan_penalty']
            reward -= makespan_penalty

            # 5-2. 설비 가동률 균형 보너스
            utilization_std = self.machine_available_times.std()
            balance_reward = self.config['balance_reward'] / (1 + utilization_std)
            reward += balance_reward

        # 6. 관찰 및 정보 반환
        observation = self._get_observation()
        info = self._get_info()

        return observation, reward, terminated, truncated, info

    def render(self):
        """
        환경 시각화 (간단한 텍스트 출력)
        """
        if not hasattr(self, 'machine_available_times'):
            return

        print(f"\n현재 스케줄링 상태:")
        print(f"  스케줄된 작업: {self.scheduled_jobs.sum()} / {self.n_jobs}")
        print(f"  총 Tardiness: {self.total_tardiness:.2f}")
        print(f"  현재 Makespan: {self.machine_available_times.max():.2f}")

        print(f"\n설비별 가용 시간:")
        for i, time in enumerate(self.machine_available_times):
            print(f"  MC{i+1:03d}: {time:.2f}")

    def close(self):
        """
        환경 종료
        """
        pass

def test_environment():
    """
    환경 테스트
    """
    print("=" * 80)
    print("🧪 APS 스케줄링 RL 환경 테스트")
    print("=" * 80)

    # 환경 생성
    env = APSSchedulingEnv(config={
        'n_machines': 5,
        'n_jobs': 10,
        'max_process_time': 50,
        'max_due_date': 300
    })

    # 환경 초기화
    observation, info = env.reset(seed=42)
    print(f"\n✅ 환경 초기화 완료")
    print(f"   Observation shape: {observation.shape}")
    print(f"   Action space: {env.action_space}")

    # 랜덤 에피소드 실행
    print(f"\n🎮 랜덤 에이전트 테스트 (10 스텝)")
    total_reward = 0
    for step in range(10):
        # 유효한 액션만 선택 (미스케줄 작업 + 적합한 설비)
        valid_actions = []
        for job_idx in range(env.n_jobs):
            if not env.scheduled_jobs[job_idx]:
                for machine_idx in range(env.n_machines):
                    if env.jobs[job_idx]['machine_eligibility'][machine_idx]:
                        action = job_idx * env.n_machines + machine_idx
                        valid_actions.append(action)

        if not valid_actions:
            break

        # 랜덤 액션 선택
        action = np.random.choice(valid_actions)
        observation, reward, terminated, truncated, info = env.step(action)

        job_idx = action // env.n_machines
        machine_idx = action % env.n_machines

        print(f"   Step {step+1}: Job {job_idx} → MC{machine_idx+1} | Reward: {reward:.2f}")

        total_reward += reward

        if terminated or truncated:
            print(f"\n✅ 에피소드 종료")
            break

    # 최종 결과
    print(f"\n📊 최종 결과:")
    print(f"   Total Reward: {total_reward:.2f}")
    print(f"   Total Tardiness: {info['total_tardiness']:.2f}")
    print(f"   Makespan: {info['makespan']:.2f}")
    print(f"   Scheduled Jobs: {info['scheduled_jobs']} / {env.n_jobs}")

    env.render()

    print("\n" + "=" * 80)
    print("✅ 환경 테스트 완료!")
    print("=" * 80)

if __name__ == '__main__':
    test_environment()
