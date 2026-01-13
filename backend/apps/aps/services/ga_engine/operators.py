"""
GA Operators Module

교차(Crossover), 돌연변이(Mutation), 선택(Selection)
"""
import random
from typing import List, Tuple
import logging

from .encoding import Chromosome

logger = logging.getLogger(__name__)


# ============================================================================
# Crossover Operators
# ============================================================================

def precedence_preserving_crossover(parent1: Chromosome, parent2: Chromosome,
                                   jobs: List[dict]) -> Tuple[Chromosome, Chromosome]:
    """
    Precedence-preserving crossover (PPX)

    Order의 precedence를 유지하면서 두 부모를 교차

    Args:
        parent1, parent2: 부모 염색체
        jobs: 작업 정보

    Returns:
        (child1, child2): 자식 염색체
    """
    n = len(parent1.genes)

    # 교차점 2개 선택
    point1 = random.randint(0, n - 1)
    point2 = random.randint(point1, n)

    # 부분 복사
    child1_genes = [None] * n
    child2_genes = [None] * n

    # 교차 구간 복사
    child1_genes[point1:point2] = parent1.genes[point1:point2]
    child2_genes[point1:point2] = parent2.genes[point1:point2]

    # 나머지 유전자 채우기 (다른 부모로부터)
    _fill_remaining(child1_genes, parent2.genes)
    _fill_remaining(child2_genes, parent1.genes)

    return Chromosome(child1_genes), Chromosome(child2_genes)


def _fill_remaining(child_genes: List[int], parent_genes: List[int]):
    """
    교차 후 빈 위치를 다른 부모의 유전자로 채우기

    순서는 다른 부모의 순서 유지
    """
    # 이미 채워진 유전자
    filled = set(g for g in child_genes if g is not None)

    # 다른 부모로부터 순서대로 채우기
    parent_iter = iter(g for g in parent_genes if g not in filled)

    for i in range(len(child_genes)):
        if child_genes[i] is None:
            child_genes[i] = next(parent_iter)


def order_crossover(parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
    """
    Order Crossover (OX)

    두 부모의 순서를 유지하면서 교차

    Args:
        parent1, parent2: 부모 염색체

    Returns:
        (child1, child2): 자식 염색체
    """
    n = len(parent1.genes)

    # 교차점 2개 선택
    point1 = random.randint(0, n - 1)
    point2 = random.randint(point1, n)

    # Child 1
    child1_genes = [None] * n
    child1_genes[point1:point2] = parent1.genes[point1:point2]

    # Parent2에서 순서대로 채우기
    filled = set(child1_genes[point1:point2])
    parent2_iter = (g for g in parent2.genes if g not in filled)

    for i in range(n):
        if child1_genes[i] is None:
            child1_genes[i] = next(parent2_iter)

    # Child 2 (대칭)
    child2_genes = [None] * n
    child2_genes[point1:point2] = parent2.genes[point1:point2]

    filled = set(child2_genes[point1:point2])
    parent1_iter = (g for g in parent1.genes if g not in filled)

    for i in range(n):
        if child2_genes[i] is None:
            child2_genes[i] = next(parent1_iter)

    return Chromosome(child1_genes), Chromosome(child2_genes)


# ============================================================================
# Mutation Operators
# ============================================================================

def swap_mutation(chromosome: Chromosome, mutation_rate: float = 0.1) -> Chromosome:
    """
    Swap Mutation

    랜덤하게 두 유전자를 교환

    Args:
        chromosome: 염색체
        mutation_rate: 돌연변이 확률 (0-1)

    Returns:
        Chromosome: 돌연변이된 염색체
    """
    if random.random() > mutation_rate:
        return chromosome.copy()

    mutated = chromosome.copy()
    n = len(mutated.genes)

    if n < 2:
        return mutated

    # 랜덤하게 두 위치 선택
    i, j = random.sample(range(n), 2)

    # Swap
    mutated.genes[i], mutated.genes[j] = mutated.genes[j], mutated.genes[i]

    return mutated


def insertion_mutation(chromosome: Chromosome, mutation_rate: float = 0.1) -> Chromosome:
    """
    Insertion Mutation

    유전자 하나를 다른 위치로 이동

    Args:
        chromosome: 염색체
        mutation_rate: 돌연변이 확률

    Returns:
        Chromosome: 돌연변이된 염색체
    """
    if random.random() > mutation_rate:
        return chromosome.copy()

    mutated = chromosome.copy()
    n = len(mutated.genes)

    if n < 2:
        return mutated

    # 이동할 유전자와 목표 위치 선택
    source = random.randint(0, n - 1)
    target = random.randint(0, n - 1)

    if source == target:
        return mutated

    # 유전자 이동
    gene = mutated.genes.pop(source)
    mutated.genes.insert(target, gene)

    return mutated


def inversion_mutation(chromosome: Chromosome, mutation_rate: float = 0.1) -> Chromosome:
    """
    Inversion Mutation

    구간을 선택하여 역순으로 뒤집기

    Args:
        chromosome: 염색체
        mutation_rate: 돌연변이 확률

    Returns:
        Chromosome: 돌연변이된 염색체
    """
    if random.random() > mutation_rate:
        return chromosome.copy()

    mutated = chromosome.copy()
    n = len(mutated.genes)

    if n < 2:
        return mutated

    # 구간 선택
    point1 = random.randint(0, n - 1)
    point2 = random.randint(point1, n)

    # 역순으로 뒤집기
    mutated.genes[point1:point2] = reversed(mutated.genes[point1:point2])

    return mutated


# ============================================================================
# Selection Operators
# ============================================================================

def tournament_selection(population: List[Chromosome], tournament_size: int = 3) -> Chromosome:
    """
    Tournament Selection

    랜덤하게 tournament_size개 선택하여 가장 좋은 개체 반환

    Args:
        population: 개체군
        tournament_size: 토너먼트 크기

    Returns:
        Chromosome: 선택된 염색체
    """
    tournament = random.sample(population, min(tournament_size, len(population)))
    return min(tournament, key=lambda c: c.fitness)


def roulette_wheel_selection(population: List[Chromosome]) -> Chromosome:
    """
    Roulette Wheel Selection

    Fitness에 반비례하는 확률로 선택 (minimization)

    Args:
        population: 개체군

    Returns:
        Chromosome: 선택된 염색체
    """
    # Fitness를 확률로 변환 (minimization이므로 역수 사용)
    max_fitness = max(c.fitness for c in population) + 1  # 0 방지
    weights = [max_fitness - c.fitness for c in population]
    total_weight = sum(weights)

    if total_weight == 0:
        return random.choice(population)

    # Roulette wheel
    r = random.uniform(0, total_weight)
    cumulative = 0

    for chromosome, weight in zip(population, weights):
        cumulative += weight
        if cumulative >= r:
            return chromosome

    return population[-1]  # fallback


def elitism_selection(population: List[Chromosome], elite_size: int = 2) -> List[Chromosome]:
    """
    Elitism Selection

    가장 좋은 elite_size개 개체를 그대로 유지

    Args:
        population: 개체군
        elite_size: 엘리트 개체 수

    Returns:
        List[Chromosome]: 엘리트 개체들
    """
    sorted_pop = sorted(population, key=lambda c: c.fitness)
    return [c.copy() for c in sorted_pop[:elite_size]]


# ============================================================================
# Helper Functions
# ============================================================================

def create_offspring(parent1: Chromosome, parent2: Chromosome,
                    jobs: List[dict],
                    crossover_rate: float = 0.8,
                    mutation_rate: float = 0.1) -> Tuple[Chromosome, Chromosome]:
    """
    두 부모로부터 자식 생성 (교차 + 돌연변이)

    Args:
        parent1, parent2: 부모 염색체
        jobs: 작업 정보
        crossover_rate: 교차 확률
        mutation_rate: 돌연변이 확률

    Returns:
        (child1, child2): 자식 염색체
    """
    # 1. Crossover
    if random.random() < crossover_rate:
        child1, child2 = order_crossover(parent1, parent2)
    else:
        child1, child2 = parent1.copy(), parent2.copy()

    # 2. Mutation
    child1 = swap_mutation(child1, mutation_rate)
    child2 = insertion_mutation(child2, mutation_rate)

    return child1, child2
