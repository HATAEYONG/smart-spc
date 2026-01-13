"""
PPO 에이전트 학습 스크립트
APS 스케줄링 최적화를 위한 강화학습 에이전트 훈련
"""
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
import numpy as np
from pathlib import Path
import os

from aps_rl_env import APSSchedulingEnv

def train_ppo_agent(
    n_jobs=20,
    n_machines=5,
    total_timesteps=500000,
    save_dir='saved_models',
    use_parallel_envs=True,
    n_envs=4
):
    """
    PPO 에이전트 학습

    Args:
        n_jobs: 작업 수
        n_machines: 설비 수
        total_timesteps: 총 학습 스텝 수
        save_dir: 모델 저장 디렉토리
        use_parallel_envs: 병렬 환경 사용 여부
        n_envs: 병렬 환경 수
    """
    print("=" * 80)
    print("🚀 PPO 에이전트 학습 시작")
    print("=" * 80)

    # 저장 디렉토리 생성
    save_path = Path(__file__).parent / save_dir
    save_path.mkdir(parents=True, exist_ok=True)

    # 환경 설정
    env_config = {
        'n_machines': n_machines,
        'n_jobs': n_jobs,
        'max_process_time': 100,
        'max_due_date': 500,
        'max_priority': 10,
        'tardiness_penalty': 2.0,
        'makespan_penalty': 0.5,
        'balance_reward': 10.0
    }

    # 환경 생성
    if use_parallel_envs:
        print(f"\n🔧 병렬 환경 생성 ({n_envs}개)...")
        env = make_vec_env(
            lambda: APSSchedulingEnv(config=env_config),
            n_envs=n_envs,
            vec_env_cls=SubprocVecEnv
        )
    else:
        print(f"\n🔧 단일 환경 생성...")
        env = APSSchedulingEnv(config=env_config)
        env = DummyVecEnv([lambda: env])

    # 평가 환경 (별도)
    eval_env = APSSchedulingEnv(config=env_config)
    eval_env = DummyVecEnv([lambda: eval_env])

    # PPO 하이퍼파라미터
    ppo_config = {
        'policy': 'MlpPolicy',
        'env': env,
        'learning_rate': 3e-4,
        'n_steps': 2048,
        'batch_size': 64,
        'n_epochs': 10,
        'gamma': 0.99,
        'gae_lambda': 0.95,
        'clip_range': 0.2,
        'ent_coef': 0.01,
        'vf_coef': 0.5,
        'max_grad_norm': 0.5,
        'verbose': 1,
        'tensorboard_log': str(save_path / 'tensorboard')
    }

    print(f"\n⚙️ PPO 하이퍼파라미터:")
    for key, value in ppo_config.items():
        if key not in ['policy', 'env']:
            print(f"   {key}: {value}")

    # PPO 에이전트 생성
    print(f"\n🤖 PPO 에이전트 생성 중...")
    model = PPO(**ppo_config)

    # 콜백 설정
    # 1. 평가 콜백 (10,000 스텝마다 평가)
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=str(save_path / 'best_model'),
        log_path=str(save_path / 'eval_logs'),
        eval_freq=10000,
        n_eval_episodes=10,
        deterministic=True,
        render=False,
        verbose=1
    )

    # 2. 체크포인트 콜백 (50,000 스텝마다 저장)
    checkpoint_callback = CheckpointCallback(
        save_freq=50000,
        save_path=str(save_path / 'checkpoints'),
        name_prefix='ppo_aps_scheduling'
    )

    # 학습 시작
    print(f"\n🎓 학습 시작 (Total timesteps: {total_timesteps:,})...")
    print(f"   TensorBoard 로그: {save_path / 'tensorboard'}")
    print(f"   Best 모델 저장: {save_path / 'best_model'}")
    print(f"   체크포인트: {save_path / 'checkpoints'}")

    model.learn(
        total_timesteps=total_timesteps,
        callback=[eval_callback, checkpoint_callback],
        progress_bar=True
    )

    # 최종 모델 저장
    final_model_path = save_path / 'final_model' / 'ppo_aps_scheduling'
    model.save(str(final_model_path))
    print(f"\n✅ 최종 모델 저장 완료: {final_model_path}")

    # 환경 종료
    env.close()
    eval_env.close()

    print("\n" + "=" * 80)
    print("✅ 학습 완료!")
    print("=" * 80)

    return model, save_path

def evaluate_agent(model_path, n_episodes=100, render=False):
    """
    학습된 에이전트 평가

    Args:
        model_path: 모델 경로
        n_episodes: 평가 에피소드 수
        render: 렌더링 여부

    Returns:
        평가 결과 딕셔너리
    """
    print("\n" + "=" * 80)
    print(f"📊 에이전트 평가 ({n_episodes} 에피소드)")
    print("=" * 80)

    # 모델 로드
    print(f"\n🔄 모델 로드 중: {model_path}")
    model = PPO.load(model_path)

    # 평가 환경 생성
    env_config = {
        'n_machines': 5,
        'n_jobs': 20,
        'max_process_time': 100,
        'max_due_date': 500
    }
    env = APSSchedulingEnv(config=env_config)

    # 평가 실행
    episode_rewards = []
    episode_tardiness = []
    episode_makespans = []

    for ep in range(n_episodes):
        observation, info = env.reset()
        episode_reward = 0
        terminated = False
        truncated = False

        while not (terminated or truncated):
            action, _states = model.predict(observation, deterministic=True)
            observation, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward

        episode_rewards.append(episode_reward)
        episode_tardiness.append(info['total_tardiness'])
        episode_makespans.append(info['makespan'])

        if render and ep < 3:  # 처음 3개 에피소드만 렌더링
            env.render()

    # 결과 통계
    results = {
        'mean_reward': np.mean(episode_rewards),
        'std_reward': np.std(episode_rewards),
        'mean_tardiness': np.mean(episode_tardiness),
        'std_tardiness': np.std(episode_tardiness),
        'mean_makespan': np.mean(episode_makespans),
        'std_makespan': np.std(episode_makespans),
        'min_tardiness': np.min(episode_tardiness),
        'max_tardiness': np.max(episode_tardiness)
    }

    print(f"\n📈 평가 결과:")
    print(f"   평균 보상: {results['mean_reward']:.2f} ± {results['std_reward']:.2f}")
    print(f"   평균 Tardiness: {results['mean_tardiness']:.2f} ± {results['std_tardiness']:.2f}")
    print(f"   평균 Makespan: {results['mean_makespan']:.2f} ± {results['std_makespan']:.2f}")
    print(f"   최소 Tardiness: {results['min_tardiness']:.2f}")
    print(f"   최대 Tardiness: {results['max_tardiness']:.2f}")

    env.close()

    return results

def compare_with_baseline():
    """
    RL 에이전트 vs 베이스라인 알고리즘 비교
    """
    print("\n" + "=" * 80)
    print("⚔️  RL vs 베이스라인 비교")
    print("=" * 80)

    # 환경 설정
    env_config = {
        'n_machines': 5,
        'n_jobs': 20,
        'max_process_time': 100,
        'max_due_date': 500
    }

    # 1. RL 에이전트
    print("\n1️⃣ RL 에이전트 (PPO)")
    model_path = Path(__file__).parent / 'saved_models' / 'best_model' / 'best_model.zip'
    if model_path.exists():
        rl_results = evaluate_agent(str(model_path), n_episodes=50)
    else:
        print("   ⚠️  학습된 모델이 없습니다. 먼저 train_ppo_agent()를 실행하세요.")
        return

    # 2. 베이스라인: FIFO (First In First Out)
    print("\n2️⃣ 베이스라인: FIFO")
    fifo_results = evaluate_baseline('FIFO', env_config, n_episodes=50)

    # 3. 베이스라인: SPT (Shortest Processing Time)
    print("\n3️⃣ 베이스라인: SPT")
    spt_results = evaluate_baseline('SPT', env_config, n_episodes=50)

    # 4. 베이스라인: EDD (Earliest Due Date)
    print("\n4️⃣ 베이스라인: EDD")
    edd_results = evaluate_baseline('EDD', env_config, n_episodes=50)

    # 비교 결과
    print("\n" + "=" * 80)
    print("📊 비교 결과 요약")
    print("=" * 80)

    comparison = {
        'RL (PPO)': rl_results,
        'FIFO': fifo_results,
        'SPT': spt_results,
        'EDD': edd_results
    }

    print(f"\n{'알고리즘':<15} {'평균 Tardiness':>20} {'평균 Makespan':>20}")
    print("-" * 60)
    for name, result in comparison.items():
        print(f"{name:<15} {result['mean_tardiness']:>15.2f} ± {result['std_tardiness']:<7.2f} {result['mean_makespan']:>15.2f} ± {result['std_makespan']:<7.2f}")

    # 개선율 계산
    best_baseline_tardiness = min(fifo_results['mean_tardiness'], spt_results['mean_tardiness'], edd_results['mean_tardiness'])
    improvement = ((best_baseline_tardiness - rl_results['mean_tardiness']) / best_baseline_tardiness) * 100

    print(f"\n🎯 RL 에이전트 개선율: {improvement:.2f}% (Best Baseline 대비)")

def evaluate_baseline(rule, env_config, n_episodes=50):
    """
    베이스라인 dispatch rule 평가
    """
    env = APSSchedulingEnv(config=env_config)

    episode_tardiness = []
    episode_makespans = []

    for ep in range(n_episodes):
        observation, info = env.reset()
        terminated = False
        truncated = False

        while not (terminated or truncated):
            # 규칙 기반 액션 선택
            action = select_action_by_rule(env, rule)
            observation, reward, terminated, truncated, info = env.step(action)

        episode_tardiness.append(info['total_tardiness'])
        episode_makespans.append(info['makespan'])

    results = {
        'mean_tardiness': np.mean(episode_tardiness),
        'std_tardiness': np.std(episode_tardiness),
        'mean_makespan': np.mean(episode_makespans),
        'std_makespan': np.std(episode_makespans)
    }

    print(f"   평균 Tardiness: {results['mean_tardiness']:.2f} ± {results['std_tardiness']:.2f}")
    print(f"   평균 Makespan: {results['mean_makespan']:.2f} ± {results['std_makespan']:.2f}")

    env.close()
    return results

def select_action_by_rule(env, rule):
    """
    규칙 기반 액션 선택
    """
    # 미스케줄 작업 찾기
    unscheduled_jobs = [i for i in range(env.n_jobs) if not env.scheduled_jobs[i]]

    if not unscheduled_jobs:
        return 0  # 더 이상 작업 없음

    # 규칙에 따라 작업 선택
    if rule == 'FIFO':
        selected_job = unscheduled_jobs[0]
    elif rule == 'SPT':
        selected_job = min(unscheduled_jobs, key=lambda j: env.jobs[j]['process_time'])
    elif rule == 'EDD':
        selected_job = min(unscheduled_jobs, key=lambda j: env.jobs[j]['due_date'])
    else:
        selected_job = unscheduled_jobs[0]

    # 가용한 설비 선택 (가장 빨리 끝나는 설비)
    eligible_machines = [m for m in range(env.n_machines) if env.jobs[selected_job]['machine_eligibility'][m]]
    selected_machine = min(eligible_machines, key=lambda m: env.machine_available_times[m])

    # 액션 인코딩
    action = selected_job * env.n_machines + selected_machine

    return action

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'train':
            # 학습 실행
            train_ppo_agent(
                n_jobs=20,
                n_machines=5,
                total_timesteps=500000,
                use_parallel_envs=True,
                n_envs=4
            )

        elif command == 'eval':
            # 평가 실행
            model_path = Path(__file__).parent / 'saved_models' / 'best_model' / 'best_model.zip'
            evaluate_agent(str(model_path), n_episodes=100, render=True)

        elif command == 'compare':
            # 비교 실행
            compare_with_baseline()

        else:
            print(f"Unknown command: {command}")
            print("Usage: python train_rl_agent.py [train|eval|compare]")

    else:
        print("Usage: python train_rl_agent.py [train|eval|compare]")
        print("\n예시:")
        print("  python train_rl_agent.py train      # 에이전트 학습")
        print("  python train_rl_agent.py eval       # 에이전트 평가")
        print("  python train_rl_agent.py compare    # 베이스라인과 비교")
