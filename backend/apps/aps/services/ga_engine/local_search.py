"""
Local Search Module

GA 솔루션을 개선하기 위한 Local Search 알고리즘
"""
import random
import copy
from typing import List, Dict, Any, Tuple, Optional
import logging

from .fitness import evaluate_fitness

logger = logging.getLogger(__name__)


def local_search(
    schedule: List[Dict[str, Any]],
    max_iterations: int = 100,
    acceptance: str = 'greedy',
    objectives: Dict[str, float] = None
) -> List[Dict[str, Any]]:
    """
    Local Search를 통한 스케줄 개선

    Neighborhood exploration:
    - Swap: 같은 자원의 두 작업을 교환
    - Insertion: 작업을 다른 위치로 이동

    Args:
        schedule: 초기 스케줄
        max_iterations: 최대 반복 횟수
        acceptance: 'greedy' (개선만 수락) or 'first_improvement'
        objectives: fitness 가중치

    Returns:
        improved_schedule: 개선된 스케줄
    """
    if not schedule:
        return schedule

    logger.info(f"Starting Local Search (max_iterations={max_iterations}, acceptance={acceptance})")

    # 현재 best solution
    current_schedule = copy.deepcopy(schedule)
    current_fitness = evaluate_fitness(current_schedule, objectives)

    best_schedule = copy.deepcopy(current_schedule)
    best_fitness = current_fitness

    improvement_count = 0
    no_improvement_streak = 0

    for iteration in range(max_iterations):
        # Neighborhood 탐색
        neighbors = _generate_neighbors(current_schedule)

        if not neighbors:
            logger.debug(f"Iteration {iteration}: No valid neighbors found")
            break

        # 이웃 솔루션 평가
        best_neighbor = None
        best_neighbor_fitness = float('inf')

        for neighbor in neighbors:
            neighbor_fitness = evaluate_fitness(neighbor, objectives)

            if neighbor_fitness < best_neighbor_fitness:
                best_neighbor_fitness = neighbor_fitness
                best_neighbor = neighbor

            # First improvement: 첫 개선 발견 시 즉시 수락
            if acceptance == 'first_improvement' and neighbor_fitness < current_fitness:
                best_neighbor = neighbor
                best_neighbor_fitness = neighbor_fitness
                break

        # 개선이 있으면 수락
        if best_neighbor_fitness < current_fitness:
            current_schedule = copy.deepcopy(best_neighbor)
            current_fitness = best_neighbor_fitness
            improvement_count += 1
            no_improvement_streak = 0

            # Global best 업데이트
            if current_fitness < best_fitness:
                best_schedule = copy.deepcopy(current_schedule)
                best_fitness = current_fitness
                logger.debug(f"Iteration {iteration}: New best fitness = {best_fitness:.2f}")
        else:
            no_improvement_streak += 1

        # Early stopping: 연속 개선 없으면 종료
        if no_improvement_streak >= 20:
            logger.info(f"Early stopping at iteration {iteration} (no improvement for 20 iterations)")
            break

    logger.info(
        f"Local Search completed: {improvement_count} improvements, "
        f"fitness {evaluate_fitness(schedule, objectives):.2f} → {best_fitness:.2f}"
    )

    return best_schedule


def _generate_neighbors(schedule: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """
    Neighborhood 생성

    두 가지 operator 적용:
    1. Swap: 같은 자원의 두 작업 교환
    2. Insertion: 작업을 다른 위치로 이동

    Returns:
        List of neighbor schedules
    """
    neighbors = []

    # 자원별 작업 그룹화
    resource_jobs = _group_by_resource(schedule)

    # 1. Swap operator: 같은 자원의 작업들끼리만 swap
    for resource_code, job_indices in resource_jobs.items():
        if len(job_indices) < 2:
            continue

        # 모든 swap 조합 생성 (최대 10개까지만)
        swap_pairs = []
        for i in range(len(job_indices)):
            for j in range(i + 1, len(job_indices)):
                swap_pairs.append((job_indices[i], job_indices[j]))

        # 최대 10개 swap 시도
        for idx1, idx2 in random.sample(swap_pairs, min(10, len(swap_pairs))):
            neighbor = _apply_swap(schedule, idx1, idx2)
            if neighbor and _is_precedence_safe(neighbor):
                neighbors.append(neighbor)

    # 2. Insertion operator: 같은 자원 내에서 위치 변경
    for resource_code, job_indices in resource_jobs.items():
        if len(job_indices) < 2:
            continue

        # 랜덤하게 몇 개 insertion 시도
        for _ in range(min(5, len(job_indices))):
            source_idx = random.choice(job_indices)
            target_idx = random.choice(job_indices)

            if source_idx != target_idx:
                neighbor = _apply_insertion(schedule, source_idx, target_idx)
                if neighbor and _is_precedence_safe(neighbor):
                    neighbors.append(neighbor)

    return neighbors


def _group_by_resource(schedule: List[Dict[str, Any]]) -> Dict[str, List[int]]:
    """
    자원별 작업 인덱스 그룹화

    Returns:
        {resource_code: [job_idx1, job_idx2, ...]}
    """
    resource_jobs = {}

    for idx, job in enumerate(schedule):
        resource_code = job.get('resource_code', job.get('mc_cd', 'UNKNOWN'))

        if resource_code not in resource_jobs:
            resource_jobs[resource_code] = []

        resource_jobs[resource_code].append(idx)

    return resource_jobs


def _apply_swap(schedule: List[Dict[str, Any]], idx1: int, idx2: int) -> Optional[List[Dict[str, Any]]]:
    """
    Swap operator: 두 작업의 시작 시간을 교환

    Args:
        schedule: 스케줄
        idx1, idx2: 교환할 작업 인덱스

    Returns:
        새로운 스케줄 (None if invalid)
    """
    if idx1 == idx2:
        return None

    # 같은 order의 작업은 swap 불가 (precedence 위반)
    order1 = schedule[idx1].get('order_id', schedule[idx1].get('wo_no'))
    order2 = schedule[idx2].get('order_id', schedule[idx2].get('wo_no'))

    if order1 == order2:
        return None

    # Deep copy and swap start/end times
    new_schedule = copy.deepcopy(schedule)

    start1 = new_schedule[idx1]['start_dt']
    end1 = new_schedule[idx1]['end_dt']
    start2 = new_schedule[idx2]['start_dt']
    end2 = new_schedule[idx2]['end_dt']

    duration1 = (end1 - start1).total_seconds() / 60
    duration2 = (end2 - start2).total_seconds() / 60

    # Swap positions
    new_schedule[idx1]['start_dt'] = start2
    new_schedule[idx1]['end_dt'] = start2 + (end1 - start1)

    new_schedule[idx2]['start_dt'] = start1
    new_schedule[idx2]['end_dt'] = start1 + (end2 - start2)

    return new_schedule


def _apply_insertion(schedule: List[Dict[str, Any]], source_idx: int, target_idx: int) -> Optional[List[Dict[str, Any]]]:
    """
    Insertion operator: source 작업을 target 위치로 이동

    Args:
        schedule: 스케줄
        source_idx: 이동할 작업
        target_idx: 목표 위치

    Returns:
        새로운 스케줄 (None if invalid)
    """
    if source_idx == target_idx:
        return None

    # 같은 order의 작업은 insertion 불가
    order_source = schedule[source_idx].get('order_id', schedule[source_idx].get('wo_no'))
    order_target = schedule[target_idx].get('order_id', schedule[target_idx].get('wo_no'))

    if order_source == order_target:
        return None

    new_schedule = copy.deepcopy(schedule)

    # source 작업을 target 시작 시간으로 이동
    source_job = new_schedule[source_idx]
    target_start = new_schedule[target_idx]['start_dt']

    duration = (source_job['end_dt'] - source_job['start_dt']).total_seconds() / 60

    source_job['start_dt'] = target_start
    source_job['end_dt'] = target_start + (source_job['end_dt'] - source_job['start_dt'])

    return new_schedule


def _is_precedence_safe(schedule: List[Dict[str, Any]]) -> bool:
    """
    Precedence 제약 검증

    같은 order의 작업들이 op_seq 순서대로 실행되는지 확인

    Returns:
        bool: True if precedence is satisfied
    """
    # Order별 작업 그룹화
    order_ops = {}

    for job in schedule:
        order_id = job.get('order_id', job.get('wo_no', ''))
        op_seq = job.get('op_seq', 0)
        start_dt = job.get('start_dt')

        if order_id not in order_ops:
            order_ops[order_id] = []

        order_ops[order_id].append((op_seq, start_dt))

    # 각 order의 작업들이 순서대로 실행되는지 확인
    for order_id, ops in order_ops.items():
        ops.sort(key=lambda x: x[0])  # op_seq로 정렬

        for i in range(len(ops) - 1):
            op_seq1, start1 = ops[i]
            op_seq2, start2 = ops[i + 1]

            # 다음 operation은 이전 operation 이후에 시작해야 함
            if start2 < start1:
                return False

    return True


def simulated_annealing_search(
    schedule: List[Dict[str, Any]],
    max_iterations: int = 200,
    initial_temp: float = 100.0,
    cooling_rate: float = 0.95,
    objectives: Dict[str, float] = None
) -> List[Dict[str, Any]]:
    """
    Simulated Annealing을 사용한 Local Search (advanced)

    Args:
        schedule: 초기 스케줄
        max_iterations: 최대 반복 횟수
        initial_temp: 초기 온도
        cooling_rate: 냉각 비율
        objectives: fitness 가중치

    Returns:
        improved_schedule: 개선된 스케줄
    """
    import math

    logger.info(f"Starting Simulated Annealing (T0={initial_temp}, cooling={cooling_rate})")

    current_schedule = copy.deepcopy(schedule)
    current_fitness = evaluate_fitness(current_schedule, objectives)

    best_schedule = copy.deepcopy(current_schedule)
    best_fitness = current_fitness

    temperature = initial_temp

    for iteration in range(max_iterations):
        # 이웃 솔루션 생성
        neighbors = _generate_neighbors(current_schedule)

        if not neighbors:
            break

        # 랜덤하게 하나 선택
        neighbor = random.choice(neighbors)
        neighbor_fitness = evaluate_fitness(neighbor, objectives)

        # Delta fitness
        delta = neighbor_fitness - current_fitness

        # Acceptance probability
        if delta < 0:
            # 개선: 무조건 수락
            accept = True
        else:
            # 나빠짐: 확률적 수락
            prob = math.exp(-delta / temperature)
            accept = random.random() < prob

        if accept:
            current_schedule = copy.deepcopy(neighbor)
            current_fitness = neighbor_fitness

            # Global best 업데이트
            if current_fitness < best_fitness:
                best_schedule = copy.deepcopy(current_schedule)
                best_fitness = current_fitness
                logger.debug(f"Iteration {iteration}: New best fitness = {best_fitness:.2f}")

        # 온도 감소
        temperature *= cooling_rate

    logger.info(
        f"Simulated Annealing completed: "
        f"fitness {evaluate_fitness(schedule, objectives):.2f} → {best_fitness:.2f}"
    )

    return best_schedule


def variable_neighborhood_search(
    schedule: List[Dict[str, Any]],
    max_iterations: int = 50,
    objectives: Dict[str, float] = None
) -> List[Dict[str, Any]]:
    """
    Variable Neighborhood Search (VNS) - advanced Local Search

    여러 neighborhood 구조를 번갈아 탐색

    Args:
        schedule: 초기 스케줄
        max_iterations: 최대 반복 횟수
        objectives: fitness 가중치

    Returns:
        improved_schedule: 개선된 스케줄
    """
    logger.info(f"Starting Variable Neighborhood Search (max_iterations={max_iterations})")

    current_schedule = copy.deepcopy(schedule)
    current_fitness = evaluate_fitness(current_schedule, objectives)

    best_schedule = copy.deepcopy(current_schedule)
    best_fitness = current_fitness

    # Neighborhood 구조들
    neighborhoods = ['swap', 'insertion', 'both']

    for iteration in range(max_iterations):
        improved = False

        for neighborhood in neighborhoods:
            # Neighborhood별 탐색
            if neighborhood == 'swap':
                neighbors = _generate_swap_neighbors(current_schedule)
            elif neighborhood == 'insertion':
                neighbors = _generate_insertion_neighbors(current_schedule)
            else:  # both
                neighbors = _generate_neighbors(current_schedule)

            if not neighbors:
                continue

            # Best neighbor 찾기
            for neighbor in neighbors:
                neighbor_fitness = evaluate_fitness(neighbor, objectives)

                if neighbor_fitness < current_fitness:
                    current_schedule = copy.deepcopy(neighbor)
                    current_fitness = neighbor_fitness
                    improved = True

                    if current_fitness < best_fitness:
                        best_schedule = copy.deepcopy(current_schedule)
                        best_fitness = current_fitness
                        logger.debug(f"Iteration {iteration} ({neighborhood}): New best = {best_fitness:.2f}")

                    break  # 개선 발견 시 다음 neighborhood로

            if improved:
                break  # 개선 발견 시 처음 neighborhood부터 재시작

        if not improved:
            logger.debug(f"Iteration {iteration}: No improvement found")

    logger.info(
        f"VNS completed: "
        f"fitness {evaluate_fitness(schedule, objectives):.2f} → {best_fitness:.2f}"
    )

    return best_schedule


def _generate_swap_neighbors(schedule: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """Swap operator만 사용한 neighborhood 생성"""
    neighbors = []
    resource_jobs = _group_by_resource(schedule)

    for resource_code, job_indices in resource_jobs.items():
        if len(job_indices) < 2:
            continue

        for i in range(len(job_indices)):
            for j in range(i + 1, len(job_indices)):
                neighbor = _apply_swap(schedule, job_indices[i], job_indices[j])
                if neighbor and _is_precedence_safe(neighbor):
                    neighbors.append(neighbor)

    return neighbors


def _generate_insertion_neighbors(schedule: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """Insertion operator만 사용한 neighborhood 생성"""
    neighbors = []
    resource_jobs = _group_by_resource(schedule)

    for resource_code, job_indices in resource_jobs.items():
        if len(job_indices) < 2:
            continue

        for source_idx in job_indices:
            for target_idx in job_indices:
                if source_idx != target_idx:
                    neighbor = _apply_insertion(schedule, source_idx, target_idx)
                    if neighbor and _is_precedence_safe(neighbor):
                        neighbors.append(neighbor)

    return neighbors
