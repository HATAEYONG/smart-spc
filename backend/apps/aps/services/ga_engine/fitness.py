"""
Fitness Evaluation Module

스케줄 품질 평가
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def evaluate_fitness(schedule: List[Dict[str, Any]], objectives: Dict[str, float] = None) -> float:
    """
    스케줄의 fitness 평가

    Fitness = W1 * makespan + W2 * total_tardiness + W3 * total_deviation

    Args:
        schedule: 스케줄 (start_dt, end_dt 포함)
        objectives: 목적함수 가중치
            - makespan_weight (기본 1.0)
            - tardiness_weight (기본 2.0)
            - deviation_weight (기본 0.5)

    Returns:
        float: fitness 값 (낮을수록 좋음)
    """
    if not schedule:
        return float('inf')

    # 기본 가중치
    if objectives is None:
        objectives = {
            'makespan_weight': 1.0,
            'tardiness_weight': 2.0,
            'deviation_weight': 0.5,
        }

    # 1. Makespan 계산
    makespan_minutes = calculate_makespan(schedule)

    # 2. Tardiness 계산
    total_tardiness = calculate_tardiness(schedule)

    # 3. Deviation 계산 (계획 대비 편차)
    total_deviation = calculate_deviation(schedule)

    # 4. Weighted sum
    fitness = (
        objectives['makespan_weight'] * makespan_minutes +
        objectives['tardiness_weight'] * total_tardiness +
        objectives['deviation_weight'] * total_deviation
    )

    return fitness


def calculate_makespan(schedule: List[Dict[str, Any]]) -> float:
    """
    Makespan 계산 (분 단위)

    Makespan = max(end_dt) - min(start_dt)
    """
    if not schedule:
        return 0.0

    start_times = [job['start_dt'] for job in schedule if 'start_dt' in job]
    end_times = [job['end_dt'] for job in schedule if 'end_dt' in job]

    if not start_times or not end_times:
        return 0.0

    makespan = max(end_times) - min(start_times)
    return makespan.total_seconds() / 60  # 분 단위


def calculate_tardiness(schedule: List[Dict[str, Any]]) -> float:
    """
    Total tardiness 계산 (분 단위)

    Tardiness = max(0, completion_time - due_date)
    """
    total_tardiness = 0.0

    for job in schedule:
        end_dt = job.get('end_dt')
        due_date = job.get('due_date') or job.get('to_ts')

        if end_dt and due_date:
            if end_dt > due_date:
                tardiness = (end_dt - due_date).total_seconds() / 60
                total_tardiness += tardiness

    return total_tardiness


def calculate_deviation(schedule: List[Dict[str, Any]]) -> float:
    """
    Total deviation 계산 (분 단위)

    Deviation = |actual_start - planned_start|
    """
    total_deviation = 0.0

    for job in schedule:
        start_dt = job.get('start_dt')
        planned_start = job.get('fr_ts')  # 원래 계획 시작 시간

        if start_dt and planned_start:
            deviation = abs((start_dt - planned_start).total_seconds() / 60)
            total_deviation += deviation

    return total_deviation


def calculate_resource_utilization(schedule: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    자원별 가동률 계산

    Returns:
        dict: {resource_code: utilization_rate (0-100%)}
    """
    if not schedule:
        return {}

    # 자원별 작업 시간 집계
    resource_times = {}  # {resource: [(start, end), ...]}

    for job in schedule:
        resource = job.get('resource_code', job.get('mc_cd', 'UNKNOWN'))
        start_dt = job.get('start_dt')
        end_dt = job.get('end_dt')

        if start_dt and end_dt:
            if resource not in resource_times:
                resource_times[resource] = []
            resource_times[resource].append((start_dt, end_dt))

    # 가동률 계산
    utilization = {}

    for resource, times in resource_times.items():
        if not times:
            utilization[resource] = 0.0
            continue

        # 총 가동 시간
        total_work_time = sum(
            (end - start).total_seconds() / 60 for start, end in times
        )

        # 총 가용 시간 (makespan 기준)
        overall_start = min(start for start, _ in times)
        overall_end = max(end for _, end in times)
        total_available = (overall_end - overall_start).total_seconds() / 60

        if total_available > 0:
            utilization[resource] = (total_work_time / total_available) * 100
        else:
            utilization[resource] = 0.0

    return utilization


def calculate_metrics(schedule: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    스케줄의 모든 메트릭 계산

    Returns:
        dict: 모든 KPI 포함
    """
    metrics = {
        'makespan': calculate_makespan(schedule),
        'total_tardiness': calculate_tardiness(schedule),
        'total_deviation': calculate_deviation(schedule),
        'resource_utilization': calculate_resource_utilization(schedule),
    }

    # 평균 가동률
    if metrics['resource_utilization']:
        metrics['avg_utilization'] = sum(metrics['resource_utilization'].values()) / len(metrics['resource_utilization'])
    else:
        metrics['avg_utilization'] = 0.0

    # Tardy jobs 수
    tardy_jobs = sum(1 for job in schedule
                     if job.get('end_dt') and job.get('due_date')
                     and job['end_dt'] > job['due_date'])
    metrics['tardy_jobs'] = tardy_jobs
    metrics['total_jobs'] = len(schedule)

    return metrics


def compare_schedules(schedule_a: List[Dict[str, Any]],
                      schedule_b: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    두 스케줄 비교

    Returns:
        dict: 비교 결과
            - makespan_diff
            - tardiness_diff
            - better: 'A' or 'B'
    """
    metrics_a = calculate_metrics(schedule_a)
    metrics_b = calculate_metrics(schedule_b)

    comparison = {
        'makespan_diff': metrics_b['makespan'] - metrics_a['makespan'],
        'tardiness_diff': metrics_b['total_tardiness'] - metrics_a['total_tardiness'],
        'deviation_diff': metrics_b['total_deviation'] - metrics_a['total_deviation'],
    }

    # Fitness 비교
    fitness_a = evaluate_fitness(schedule_a)
    fitness_b = evaluate_fitness(schedule_b)

    comparison['fitness_a'] = fitness_a
    comparison['fitness_b'] = fitness_b
    comparison['fitness_diff'] = fitness_b - fitness_a
    comparison['better'] = 'A' if fitness_a < fitness_b else 'B'

    return comparison
