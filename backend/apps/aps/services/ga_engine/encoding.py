"""
Encoding/Decoding Module

GA 염색체 표현 및 스케줄 변환
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class Chromosome:
    """
    염색체 표현: Operation-based encoding

    chromosome = [job_idx1, job_idx2, ..., job_idxN]
    - 각 job이 순서대로 나타남
    - 같은 job의 operation들은 순서 유지 (precedence)
    """

    def __init__(self, genes: List[int]):
        """
        Args:
            genes: job index 리스트
        """
        self.genes = genes
        self.fitness = None

    def __len__(self):
        return len(self.genes)

    def __repr__(self):
        return f"Chromosome(genes={self.genes[:10]}..., fitness={self.fitness})"

    def copy(self):
        """염색체 복사"""
        new_chr = Chromosome(self.genes.copy())
        new_chr.fitness = self.fitness
        return new_chr


def encode_jobs(jobs: List[Dict[str, Any]]) -> Chromosome:
    """
    작업 리스트를 염색체로 인코딩

    Args:
        jobs: 작업 리스트
            - order_id, op_seq, resource_code, duration_minutes 포함

    Returns:
        Chromosome: 인코딩된 염색체
    """
    # Order별로 그룹화
    orders = {}
    for idx, job in enumerate(jobs):
        order_id = job.get('order_id', job.get('wo_no', f'ORDER_{idx}'))
        if order_id not in orders:
            orders[order_id] = []
        orders[order_id].append(idx)

    # 각 order의 operation들을 순서대로 추가 (precedence 유지)
    genes = []
    for order_id in orders:
        # op_seq로 정렬
        ops = sorted(orders[order_id], key=lambda i: jobs[i].get('op_seq', 0))
        genes.extend(ops)

    return Chromosome(genes)


def decode_chromosome(chromosome: Chromosome, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    염색체를 스케줄로 디코딩

    Args:
        chromosome: 염색체
        jobs: 원본 작업 리스트

    Returns:
        schedule: 디코딩된 스케줄
            - start_dt, end_dt 추가됨
    """
    schedule = []

    # Resource별 마지막 종료 시간 추적
    resource_end_times: Dict[str, datetime] = {}

    # Order별 마지막 종료 시간 추적 (precedence)
    order_end_times: Dict[str, datetime] = {}

    # 기준 시작 시간
    base_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

    for gene in chromosome.genes:
        job = jobs[gene].copy()

        order_id = job.get('order_id', job.get('wo_no', f'ORDER_{gene}'))
        resource_code = job.get('resource_code', job.get('mc_cd', 'UNKNOWN'))
        duration_minutes = job.get('duration_minutes', 60)

        # 최소 시작 시간 계산
        min_start = base_time

        # 1. Order precedence: 이전 operation 완료 후
        if order_id in order_end_times:
            min_start = max(min_start, order_end_times[order_id])

        # 2. Resource conflict: 자원 사용 가능 시간
        if resource_code in resource_end_times:
            min_start = max(min_start, resource_end_times[resource_code])

        # 시작/종료 시간 설정
        start_dt = min_start
        end_dt = start_dt + timedelta(minutes=duration_minutes)

        # 작업 정보 업데이트
        job['start_dt'] = start_dt
        job['end_dt'] = end_dt
        job['job_idx'] = gene

        schedule.append(job)

        # 추적 업데이트
        resource_end_times[resource_code] = end_dt
        order_end_times[order_id] = end_dt

    return schedule


def create_random_chromosome(jobs: List[Dict[str, Any]]) -> Chromosome:
    """
    랜덤 염색체 생성 (초기 population용)

    Precedence를 유지하면서 랜덤 순서 생성
    """
    # Order별 그룹화
    orders = {}
    for idx, job in enumerate(jobs):
        order_id = job.get('order_id', job.get('wo_no', f'ORDER_{idx}'))
        if order_id not in orders:
            orders[order_id] = []
        orders[order_id].append((idx, job.get('op_seq', 0)))

    # 각 order의 operation 정렬 (op_seq 순서 유지)
    for order_id in orders:
        orders[order_id].sort(key=lambda x: x[1])
        orders[order_id] = [idx for idx, _ in orders[order_id]]

    # Order 순서 섞기 (랜덤)
    order_ids = list(orders.keys())
    random.shuffle(order_ids)

    # 염색체 구성
    genes = []
    while order_ids:
        # 랜덤하게 order 선택
        order_id = random.choice(order_ids)

        # 해당 order의 다음 operation 추가
        if orders[order_id]:
            genes.append(orders[order_id].pop(0))

            # operation이 모두 추가되면 제거
            if not orders[order_id]:
                order_ids.remove(order_id)

    return Chromosome(genes)


def validate_chromosome(chromosome: Chromosome, jobs: List[Dict[str, Any]]) -> bool:
    """
    염색체 유효성 검증

    1. 모든 job이 정확히 한 번씩 나타나는가?
    2. Precedence 제약을 만족하는가?

    Returns:
        bool: True if valid
    """
    # 1. 모든 job 존재 확인
    if len(chromosome.genes) != len(jobs):
        logger.error(f"Invalid chromosome: length mismatch ({len(chromosome.genes)} != {len(jobs)})")
        return False

    if set(chromosome.genes) != set(range(len(jobs))):
        logger.error(f"Invalid chromosome: missing or duplicate jobs")
        return False

    # 2. Precedence 확인
    order_positions = {}  # {order_id: [positions of operations]}

    for pos, gene in enumerate(chromosome.genes):
        job = jobs[gene]
        order_id = job.get('order_id', job.get('wo_no', f'ORDER_{gene}'))
        op_seq = job.get('op_seq', 0)

        if order_id not in order_positions:
            order_positions[order_id] = []

        order_positions[order_id].append((pos, op_seq))

    # 각 order의 operation들이 op_seq 순서대로 나타나는지 확인
    for order_id, ops in order_positions.items():
        ops.sort(key=lambda x: x[0])  # position으로 정렬
        op_seqs = [op_seq for _, op_seq in ops]

        if op_seqs != sorted(op_seqs):
            logger.error(f"Invalid chromosome: precedence violation in order {order_id}")
            return False

    return True


def repair_chromosome(chromosome: Chromosome, jobs: List[Dict[str, Any]]) -> Chromosome:
    """
    유효하지 않은 염색체 복구

    Precedence 제약을 만족하도록 재정렬
    """
    # Order별 그룹화
    orders = {}
    for gene in chromosome.genes:
        job = jobs[gene]
        order_id = job.get('order_id', job.get('wo_no', f'ORDER_{gene}'))
        op_seq = job.get('op_seq', 0)

        if order_id not in orders:
            orders[order_id] = []
        orders[order_id].append((gene, op_seq))

    # 각 order의 operation 정렬
    for order_id in orders:
        orders[order_id].sort(key=lambda x: x[1])  # op_seq로 정렬

    # 원래 순서 유지하면서 precedence만 수정
    repaired_genes = []
    order_queues = {order_id: list(ops) for order_id, ops in orders.items()}

    for gene in chromosome.genes:
        job = jobs[gene]
        order_id = job.get('order_id', job.get('wo_no', f'ORDER_{gene}'))

        # 해당 order의 다음 operation 추가
        if order_queues[order_id]:
            next_gene, _ = order_queues[order_id].pop(0)
            repaired_genes.append(next_gene)

    return Chromosome(repaired_genes)
