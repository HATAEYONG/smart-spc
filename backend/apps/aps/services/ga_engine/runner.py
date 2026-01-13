"""
GA Runner Module

Hybrid GA + Local Search 실행 엔진
"""
import random
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from .encoding import (
    Chromosome,
    encode_jobs,
    decode_chromosome,
    create_random_chromosome,
    validate_chromosome,
    repair_chromosome
)
from .fitness import evaluate_fitness, calculate_metrics
from .operators import (
    create_offspring,
    tournament_selection,
    elitism_selection
)
from .local_search import local_search

logger = logging.getLogger(__name__)


def run_ga_with_local_search(
    jobs: List[Dict[str, Any]],
    population_size: int = 50,
    max_generations: int = 100,
    crossover_rate: float = 0.8,
    mutation_rate: float = 0.1,
    elite_size: int = 2,
    tournament_size: int = 3,
    objectives: Dict[str, float] = None,
    use_local_search: bool = True,
    local_search_iterations: int = 50,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Hybrid GA + Local Search 메인 함수

    Args:
        jobs: 작업 리스트
            - order_id, op_seq, resource_code, duration_minutes, due_date, fr_ts 포함
        population_size: 개체군 크기
        max_generations: 최대 세대 수
        crossover_rate: 교차 확률 (0-1)
        mutation_rate: 돌연변이 확률 (0-1)
        elite_size: 엘리트 개체 수
        tournament_size: 토너먼트 크기
        objectives: 목적함수 가중치
            - makespan_weight (기본 1.0)
            - tardiness_weight (기본 2.0)
            - deviation_weight (기본 0.5)
        use_local_search: Local Search 사용 여부
        local_search_iterations: Local Search 반복 횟수
        verbose: 로그 출력 여부

    Returns:
        dict:
            - best_schedule: 최적 스케줄
            - best_fitness: 최적 fitness
            - metrics: KPI 메트릭
            - history: 세대별 fitness 이력
            - computation_time: 실행 시간
    """
    start_time = datetime.now()

    if not jobs:
        logger.warning("Empty jobs list, returning empty result")
        return {
            'best_schedule': [],
            'best_fitness': float('inf'),
            'metrics': {},
            'history': [],
            'computation_time': 0
        }

    logger.info(
        f"Starting Hybrid GA+LS: {len(jobs)} jobs, "
        f"pop={population_size}, gen={max_generations}, "
        f"LS={use_local_search}"
    )

    # 기본 가중치
    if objectives is None:
        objectives = {
            'makespan_weight': 1.0,
            'tardiness_weight': 2.0,
            'deviation_weight': 0.5,
        }

    # ========================================================================
    # Step 1: 초기 개체군 생성
    # ========================================================================
    logger.info("Step 1: Initializing population...")
    population = _initialize_population(jobs, population_size)

    # Fitness 평가
    for chromosome in population:
        schedule = decode_chromosome(chromosome, jobs)
        chromosome.fitness = evaluate_fitness(schedule, objectives)

    # 초기 best 찾기
    population.sort(key=lambda c: c.fitness)
    best_chromosome = population[0].copy()

    history = {
        'generation': [],
        'best_fitness': [],
        'avg_fitness': [],
        'worst_fitness': []
    }

    _record_generation(history, 0, population)

    if verbose:
        logger.info(f"Generation 0: Best fitness = {best_chromosome.fitness:.2f}")

    # ========================================================================
    # Step 2: GA 진화 루프
    # ========================================================================
    logger.info("Step 2: Running GA evolution...")

    no_improvement_streak = 0
    last_best_fitness = best_chromosome.fitness

    for generation in range(1, max_generations + 1):
        # 새로운 세대 생성
        new_population = []

        # 1) Elitism: 최고 개체 보존
        elites = elitism_selection(population, elite_size)
        new_population.extend(elites)

        # 2) 교차 + 돌연변이로 나머지 채우기
        while len(new_population) < population_size:
            # 부모 선택 (tournament)
            parent1 = tournament_selection(population, tournament_size)
            parent2 = tournament_selection(population, tournament_size)

            # 자식 생성
            child1, child2 = create_offspring(
                parent1, parent2, jobs,
                crossover_rate, mutation_rate
            )

            # 유효성 검증 및 복구
            if not validate_chromosome(child1, jobs):
                child1 = repair_chromosome(child1, jobs)

            if not validate_chromosome(child2, jobs):
                child2 = repair_chromosome(child2, jobs)

            # Fitness 평가
            schedule1 = decode_chromosome(child1, jobs)
            child1.fitness = evaluate_fitness(schedule1, objectives)

            schedule2 = decode_chromosome(child2, jobs)
            child2.fitness = evaluate_fitness(schedule2, objectives)

            new_population.append(child1)
            if len(new_population) < population_size:
                new_population.append(child2)

        # 개체군 업데이트
        population = new_population

        # Best 업데이트
        population.sort(key=lambda c: c.fitness)
        if population[0].fitness < best_chromosome.fitness:
            best_chromosome = population[0].copy()
            no_improvement_streak = 0
        else:
            no_improvement_streak += 1

        # History 기록
        _record_generation(history, generation, population)

        # 로그 출력
        if verbose and generation % 10 == 0:
            logger.info(
                f"Generation {generation}: "
                f"Best = {population[0].fitness:.2f}, "
                f"Avg = {sum(c.fitness for c in population) / len(population):.2f}"
            )

        # Early stopping
        if no_improvement_streak >= 30:
            logger.info(f"Early stopping at generation {generation} (no improvement for 30 generations)")
            break

    logger.info(f"GA evolution completed after {generation} generations")

    # ========================================================================
    # Step 3: Local Search (최종 개선)
    # ========================================================================
    best_schedule = decode_chromosome(best_chromosome, jobs)
    ga_fitness = best_chromosome.fitness

    if use_local_search:
        logger.info("Step 3: Applying Local Search to best solution...")

        improved_schedule = local_search(
            best_schedule,
            max_iterations=local_search_iterations,
            acceptance='greedy',
            objectives=objectives
        )

        improved_fitness = evaluate_fitness(improved_schedule, objectives)

        if improved_fitness < ga_fitness:
            logger.info(
                f"Local Search improved fitness: {ga_fitness:.2f} → {improved_fitness:.2f} "
                f"({(ga_fitness - improved_fitness) / ga_fitness * 100:.1f}% improvement)"
            )
            best_schedule = improved_schedule
            best_fitness = improved_fitness
        else:
            logger.info(f"Local Search did not improve fitness (kept GA solution)")
            best_fitness = ga_fitness
    else:
        best_fitness = ga_fitness

    # ========================================================================
    # Step 4: 결과 정리
    # ========================================================================
    end_time = datetime.now()
    computation_time = (end_time - start_time).total_seconds()

    metrics = calculate_metrics(best_schedule)

    result = {
        'best_schedule': best_schedule,
        'best_fitness': best_fitness,
        'metrics': metrics,
        'history': history,
        'computation_time': computation_time,
        'ga_generations': generation,
        'initial_fitness': history['best_fitness'][0] if history['best_fitness'] else None,
        'ga_final_fitness': ga_fitness,
        'ls_final_fitness': best_fitness if use_local_search else None,
    }

    logger.info(
        f"✓ Hybrid GA+LS completed in {computation_time:.2f}s\n"
        f"  Initial fitness: {result['initial_fitness']:.2f}\n"
        f"  GA final: {ga_fitness:.2f}\n"
        f"  LS final: {best_fitness:.2f}\n"
        f"  Total improvement: {(result['initial_fitness'] - best_fitness) / result['initial_fitness'] * 100:.1f}%\n"
        f"  Makespan: {metrics['makespan']:.0f} min\n"
        f"  Tardiness: {metrics['total_tardiness']:.0f} min\n"
        f"  Tardy jobs: {metrics['tardy_jobs']}/{metrics['total_jobs']}"
    )

    return result


def _initialize_population(jobs: List[Dict[str, Any]], population_size: int) -> List[Chromosome]:
    """
    초기 개체군 생성

    여러 휴리스틱을 조합하여 다양성 확보:
    1. Random (50%)
    2. EDD (Earliest Due Date) (25%)
    3. SPT (Shortest Processing Time) (25%)
    """
    population = []

    # 1) Random 염색체
    for _ in range(population_size // 2):
        chromosome = create_random_chromosome(jobs)
        population.append(chromosome)

    # 2) EDD 기반 염색체
    for _ in range(population_size // 4):
        chromosome = _create_edd_chromosome(jobs)
        population.append(chromosome)

    # 3) SPT 기반 염색체
    for _ in range(population_size - len(population)):
        chromosome = _create_spt_chromosome(jobs)
        population.append(chromosome)

    logger.info(
        f"Initialized population: {len(population)} individuals "
        f"(Random: {population_size // 2}, EDD: {population_size // 4}, SPT: {population_size - len(population)})"
    )

    return population


def _create_edd_chromosome(jobs: List[Dict[str, Any]]) -> Chromosome:
    """
    EDD (Earliest Due Date) 휴리스틱 기반 염색체 생성

    Order를 due_date 순서로 정렬하여 염색체 구성
    """
    # Order별 due_date 계산
    order_due_dates = {}
    order_jobs = {}

    for idx, job in enumerate(jobs):
        order_id = job.get('order_id', job.get('wo_no', f'ORDER_{idx}'))
        due_date = job.get('due_date') or job.get('to_ts') or datetime.max

        if order_id not in order_due_dates:
            order_due_dates[order_id] = due_date
            order_jobs[order_id] = []

        order_jobs[order_id].append((idx, job.get('op_seq', 0)))

    # Order를 due_date 순서로 정렬
    sorted_orders = sorted(order_due_dates.items(), key=lambda x: x[1])

    # 염색체 구성
    genes = []
    for order_id, _ in sorted_orders:
        # operation을 op_seq 순서로 추가
        ops = sorted(order_jobs[order_id], key=lambda x: x[1])
        genes.extend([idx for idx, _ in ops])

    return Chromosome(genes)


def _create_spt_chromosome(jobs: List[Dict[str, Any]]) -> Chromosome:
    """
    SPT (Shortest Processing Time) 휴리스틱 기반 염색체 생성

    짧은 작업을 우선 배치 (precedence 유지)
    """
    # Order별 그룹화
    orders = {}
    for idx, job in enumerate(jobs):
        order_id = job.get('order_id', job.get('wo_no', f'ORDER_{idx}'))
        if order_id not in orders:
            orders[order_id] = []
        orders[order_id].append((idx, job.get('op_seq', 0), job.get('duration_minutes', 60)))

    # 각 order의 operation을 op_seq 순서로 정렬
    for order_id in orders:
        orders[order_id].sort(key=lambda x: x[1])

    # Order를 총 처리시간 순서로 정렬
    order_durations = {
        order_id: sum(duration for _, _, duration in ops)
        for order_id, ops in orders.items()
    }

    sorted_orders = sorted(order_durations.items(), key=lambda x: x[1])

    # 염색체 구성
    genes = []
    for order_id, _ in sorted_orders:
        genes.extend([idx for idx, _, _ in orders[order_id]])

    return Chromosome(genes)


def _record_generation(history: Dict[str, List], generation: int, population: List[Chromosome]):
    """
    세대별 통계 기록
    """
    fitnesses = [c.fitness for c in population]

    history['generation'].append(generation)
    history['best_fitness'].append(min(fitnesses))
    history['avg_fitness'].append(sum(fitnesses) / len(fitnesses))
    history['worst_fitness'].append(max(fitnesses))


def run_ga_only(
    jobs: List[Dict[str, Any]],
    population_size: int = 50,
    max_generations: int = 100,
    objectives: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    GA만 실행 (Local Search 없이)

    테스트 및 비교용
    """
    return run_ga_with_local_search(
        jobs=jobs,
        population_size=population_size,
        max_generations=max_generations,
        objectives=objectives,
        use_local_search=False,
        verbose=True
    )


def run_local_search_only(
    jobs: List[Dict[str, Any]],
    initial_solution: Optional[List[Dict[str, Any]]] = None,
    max_iterations: int = 100,
    objectives: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Local Search만 실행 (GA 없이)

    Args:
        jobs: 작업 리스트
        initial_solution: 초기 솔루션 (None이면 랜덤 생성)
        max_iterations: 최대 반복 횟수
        objectives: 목적함수 가중치

    Returns:
        dict: 결과 (best_schedule, best_fitness, metrics 포함)
    """
    start_time = datetime.now()

    # 초기 솔루션 생성
    if initial_solution is None:
        chromosome = create_random_chromosome(jobs)
        initial_solution = decode_chromosome(chromosome, jobs)

    initial_fitness = evaluate_fitness(initial_solution, objectives)

    # Local Search 적용
    best_schedule = local_search(
        initial_solution,
        max_iterations=max_iterations,
        acceptance='greedy',
        objectives=objectives
    )

    best_fitness = evaluate_fitness(best_schedule, objectives)
    metrics = calculate_metrics(best_schedule)

    end_time = datetime.now()
    computation_time = (end_time - start_time).total_seconds()

    result = {
        'best_schedule': best_schedule,
        'best_fitness': best_fitness,
        'metrics': metrics,
        'computation_time': computation_time,
        'initial_fitness': initial_fitness,
    }

    logger.info(
        f"✓ Local Search completed in {computation_time:.2f}s\n"
        f"  Initial fitness: {initial_fitness:.2f}\n"
        f"  Final fitness: {best_fitness:.2f}\n"
        f"  Improvement: {(initial_fitness - best_fitness) / initial_fitness * 100:.1f}%"
    )

    return result


def compare_methods(
    jobs: List[Dict[str, Any]],
    objectives: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    여러 최적화 방법 비교

    1. Random 솔루션
    2. GA only
    3. Local Search only
    4. Hybrid GA + LS

    Returns:
        dict: 각 방법별 결과 비교
    """
    logger.info("=" * 80)
    logger.info("Comparing optimization methods...")
    logger.info("=" * 80)

    results = {}

    # 1) Random solution (baseline)
    logger.info("\n[1/4] Random solution...")
    chromosome = create_random_chromosome(jobs)
    random_schedule = decode_chromosome(chromosome, jobs)
    random_fitness = evaluate_fitness(random_schedule, objectives)
    results['random'] = {
        'fitness': random_fitness,
        'metrics': calculate_metrics(random_schedule)
    }

    # 2) GA only
    logger.info("\n[2/4] GA only...")
    ga_result = run_ga_only(jobs, population_size=30, max_generations=50, objectives=objectives)
    results['ga_only'] = ga_result

    # 3) Local Search only
    logger.info("\n[3/4] Local Search only...")
    ls_result = run_local_search_only(jobs, initial_solution=random_schedule, max_iterations=50, objectives=objectives)
    results['ls_only'] = ls_result

    # 4) Hybrid GA + LS
    logger.info("\n[4/4] Hybrid GA + Local Search...")
    hybrid_result = run_ga_with_local_search(
        jobs,
        population_size=30,
        max_generations=50,
        use_local_search=True,
        local_search_iterations=50,
        objectives=objectives
    )
    results['hybrid'] = hybrid_result

    # 비교 출력
    logger.info("\n" + "=" * 80)
    logger.info("COMPARISON RESULTS")
    logger.info("=" * 80)
    logger.info(f"{'Method':<20} {'Fitness':>12} {'Makespan':>12} {'Tardiness':>12} {'Time (s)':>10}")
    logger.info("-" * 80)

    logger.info(
        f"{'Random':<20} {results['random']['fitness']:>12.2f} "
        f"{results['random']['metrics']['makespan']:>12.0f} "
        f"{results['random']['metrics']['total_tardiness']:>12.0f} "
        f"{'-':>10}"
    )

    logger.info(
        f"{'GA only':<20} {results['ga_only']['best_fitness']:>12.2f} "
        f"{results['ga_only']['metrics']['makespan']:>12.0f} "
        f"{results['ga_only']['metrics']['total_tardiness']:>12.0f} "
        f"{results['ga_only']['computation_time']:>10.2f}"
    )

    logger.info(
        f"{'LS only':<20} {results['ls_only']['best_fitness']:>12.2f} "
        f"{results['ls_only']['metrics']['makespan']:>12.0f} "
        f"{results['ls_only']['metrics']['total_tardiness']:>12.0f} "
        f"{results['ls_only']['computation_time']:>10.2f}"
    )

    logger.info(
        f"{'Hybrid GA+LS':<20} {results['hybrid']['best_fitness']:>12.2f} "
        f"{results['hybrid']['metrics']['makespan']:>12.0f} "
        f"{results['hybrid']['metrics']['total_tardiness']:>12.0f} "
        f"{results['hybrid']['computation_time']:>10.2f}"
    )

    logger.info("=" * 80)

    return results
