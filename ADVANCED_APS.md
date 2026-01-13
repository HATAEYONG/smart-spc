# 고급 APS 기능 가이드

이 문서는 Online APS-CPS Scheduler의 고급 스케줄링 기능을 설명합니다.

## 📋 목차

- [다중 목표 최적화](#다중-목표-최적화)
- [유전 알고리즘 스케줄러](#유전-알고리즘-스케줄러)
- [실시간 리스케줄링](#실시간-리스케줄링)
- [Setup Time 관리](#setup-time-관리)
- [Cleaning Time 관리](#cleaning-time-관리)
- [사용 예제](#사용-예제)

## 🎯 다중 목표 최적화

### 개요

`MultiObjectiveSolver`는 여러 목표를 동시에 최적화합니다:
- **Makespan**: 전체 작업 완료 시간 최소화
- **Cost**: 기계 사용 비용 최소화
- **Tardiness**: 납기 지연 최소화

### 특징

```python
from aps_solver_advanced import MultiObjectiveSolver

# 가중치 설정 (각 목표의 중요도)
weights = {
    'makespan': 1.0,    # 완료 시간
    'cost': 0.5,        # 비용
    'tardiness': 2.0    # 납기 준수 (가장 중요)
}

solver = MultiObjectiveSolver(weights=weights)
```

### 기능

1. **기계 할당 최적화**
   - Freeze level에 따라 기계 변경 가능 여부 결정
   - Level 0: 자유롭게 기계 선택 가능
   - Level 1+: 기계 고정

2. **Setup Time 고려**
   - 품목 간 전환 시 setup time 자동 추가
   - Setup time matrix 기반 최적화

3. **Cleaning Time 통합**
   - 기계별 cleaning 주기 자동 고려
   - 스케줄에 cleaning 시간 포함

4. **우선순위 기반 스케줄링**
   - Job priority (1-10)에 따른 가중치 적용
   - 높은 우선순위 작업의 지연 페널티 증가

### 사용 방법

```python
# Setup time matrix
setup_times = {
    ('ITEM_A', 'ITEM_B'): 15,  # A에서 B로 전환 시 15분
    ('ITEM_B', 'ITEM_A'): 20,  # B에서 A로 전환 시 20분
}

# Cleaning requirements
cleaning_times = {
    'MC001': 30,  # MC001은 30분 cleaning 필요
    'MC002': 20,
}

# Machine costs (per hour)
machine_costs = {
    'MC001': 100.0,  # $100/hour
    'MC002': 150.0,  # $150/hour (더 비쌈)
}

# Solve
result = solver.solve(
    scope_items=jobs,
    machines=['MC001', 'MC002'],
    setup_times=setup_times,
    cleaning_times=cleaning_times,
    machine_costs=machine_costs
)
```

## 🧬 유전 알고리즘 스케줄러

### 개요

`GeneticScheduler`는 진화론적 접근방식을 사용하여 대규모 스케줄링 문제를 빠르게 해결합니다.

### 장점

- **대규모 문제 처리**: 수백~수천 개의 작업 처리 가능
- **빠른 실행 시간**: CP-SAT보다 빠른 근사해 도출
- **유연성**: 다양한 제약 조건 쉽게 추가 가능

### 파라미터

```python
from genetic_scheduler import GeneticScheduler

scheduler = GeneticScheduler(
    population_size=100,    # 세대당 개체 수
    generations=500,        # 진화 세대 수
    crossover_rate=0.8,     # 교차 확률
    mutation_rate=0.2,      # 돌연변이 확률
    elite_size=10           # 엘리트 보존 개체 수
)
```

### 알고리즘 흐름

1. **초기 개체군 생성**: 랜덤 스케줄 생성
2. **적합도 평가**: Makespan, Cost, Tardiness 계산
3. **선택**: Tournament selection으로 부모 선택
4. **교차**: Order crossover (OX)로 자식 생성
5. **돌연변이**: 작업 순서 변경 또는 기계 재할당
6. **엘리트 보존**: 최고 개체 다음 세대로 전달
7. **반복**: 지정된 세대 수만큼 반복

### 사용 방법

```python
# 간단한 사용
result = scheduler.solve(
    scope_items=jobs,
    machines=['MC001', 'MC002', 'MC003'],
    objective='makespan'  # 'makespan', 'cost', or 'tardiness'
)

# 진행 상황 로그
# Generation 0: Best fitness = 2450.00
# Generation 100: Best fitness = 1850.00
# Generation 200: Best fitness = 1620.00
# ...
```

### 하이브리드 스케줄러

문제 크기에 따라 자동으로 알고리즘 선택:

```python
from genetic_scheduler import HybridScheduler

hybrid = HybridScheduler(threshold=50)

# 작업 수 <= 50: CP-SAT 사용 (최적해)
# 작업 수 > 50: GA 사용 (빠른 근사해)
result = hybrid.solve(scope_items, machines)
```

## 🔄 실시간 리스케줄링

### 개요

`RealtimeRescheduler`는 다양한 이벤트에 대응하여 스케줄을 동적으로 조정합니다.

### 지원 이벤트

#### 1. 기계 고장 (Machine Breakdown)

```python
from realtime_rescheduler import RealtimeRescheduler

rescheduler = RealtimeRescheduler(strategy='minimal_disruption')

updated_schedule = rescheduler.reschedule_on_breakdown(
    current_schedule=current_schedule,
    broken_machine='MC001',
    repair_time_minutes=120,  # 2시간 수리 예상
    current_time=datetime.now()
)
```

**전략 옵션**:
- `minimal_disruption`: 영향받은 작업만 지연
- `complete_reopt`: 대체 기계로 재배치
- `rolling_horizon`: 시간 창 기반 재최적화

#### 2. 긴급 주문 (Emergency Order)

```python
emergency_job = {
    'wo_no': 'URGENT001',
    'mc_cd': 'MC002',
    'duration': 60,
    'priority': 10  # 최고 우선순위
}

updated_schedule = rescheduler.reschedule_on_emergency_order(
    current_schedule=current_schedule,
    emergency_job=emergency_job,
    current_time=datetime.now(),
    priority=10
)
```

특징:
- 최적 삽입 위치 자동 탐색
- 후속 작업 자동 shift
- 최소 disruption 보장

#### 3. 작업 지연 (Job Delay)

```python
updated_schedule = rescheduler.reschedule_on_delay(
    current_schedule=current_schedule,
    delayed_job_id='WO12345',
    delay_minutes=30,
    current_time=datetime.now()
)
```

특징:
- 지연 전파 자동 계산
- 의존 작업 자동 조정

### 적응형 스케줄러

과거 이벤트로부터 학습하여 버퍼 시간을 자동 조정:

```python
from realtime_rescheduler import AdaptiveScheduler

adaptive = AdaptiveScheduler()

# 이벤트 기록
adaptive.add_reschedule_event(
    event_type='breakdown',
    machine='MC001',
    impact_minutes=120
)

# 권장 버퍼 시간 조회
buffer = adaptive.get_recommended_buffer('MC001')
print(f"Recommended buffer for MC001: {buffer} minutes")
```

## ⚙️ Setup Time 관리

### 개요

`SetupTimeManager`는 품목 간 전환 시간을 관리합니다.

### Setup Time Matrix

```python
from setup_manager import SetupTimeManager

setup_mgr = SetupTimeManager()

# Setup time 설정
setup_mgr.add_setup_time('ITEM_A', 'ITEM_B', 15)  # A->B: 15분
setup_mgr.add_setup_time('ITEM_B', 'ITEM_A', 20)  # B->A: 20분
setup_mgr.add_setup_time('ITEM_A', 'ITEM_A', 5)   # A->A: 5분 (동일 품목)
```

### 패밀리 기반 Setup Time

```python
# 품목 패밀리별 setup time
setup_mgr.setup_matrix = {
    ('FAMILY_A', 'FAMILY_A'): 5,   # 같은 패밀리 내
    ('FAMILY_A', 'FAMILY_B'): 15,  # 다른 패밀리 간
    ('FAMILY_B', 'FAMILY_C'): 10,
}

# 자동 패밀리 매핑 (품목 코드 첫 3자리)
setup_time = setup_mgr.get_setup_time('ABC-001', 'ABC-002')  # FAMILY_A 내부
# Returns: 5 minutes
```

### 시퀀스 최적화

Setup time을 최소화하는 작업 순서 계산:

```python
items = ['ITEM_A', 'ITEM_B', 'ITEM_C', 'ITEM_D']

optimized_sequence = setup_mgr.optimize_sequence(items)
# Returns: ['ITEM_A', 'ITEM_C', 'ITEM_B', 'ITEM_D']
# (nearest neighbor heuristic)
```

### JSON 파일에서 로드

```json
{
  "ITEM_A,ITEM_B": 15,
  "ITEM_B,ITEM_A": 20,
  "FAMILY_A,FAMILY_B": 15
}
```

```python
setup_mgr = SetupTimeManager(setup_matrix_file='setup_times.json')
```

## 🧹 Cleaning Time 관리

### 개요

`CleaningTimeManager`는 기계별 청소 요구사항을 관리합니다.

### 청소 요구사항 설정

```python
from setup_manager import CleaningTimeManager

cleaning_mgr = CleaningTimeManager()

# 기계별 청소 설정
cleaning_mgr.set_cleaning_requirement(
    machine='MC001',
    frequency_hours=8,     # 8시간마다 청소
    duration_minutes=30    # 청소 시간 30분
)

cleaning_mgr.set_cleaning_requirement(
    machine='MC002',
    frequency_hours=12,
    duration_minutes=20
)
```

### 청소 필요 여부 확인

```python
hours_running = 9.5  # 9.5시간 연속 가동

needs_clean = cleaning_mgr.needs_cleaning('MC001', hours_running)
# Returns: True (8시간 기준 초과)

if needs_clean:
    duration = cleaning_mgr.get_cleaning_duration('MC001')
    print(f"Cleaning needed: {duration} minutes")
```

### 청소 스케줄 자동 생성

```python
# 24시간 planning horizon에 대한 청소 스케줄
cleaning_schedule = cleaning_mgr.schedule_cleanings(
    machine='MC001',
    schedule_horizon_hours=24,
    start_hour=0
)

# Returns: [8, 16] (8시간, 16시간에 청소)
```

## 🔧 사용 예제

### 예제 1: 다중 목표 최적화

```python
from aps_solver_advanced import MultiObjectiveSolver
from setup_manager import SetupTimeManager, CleaningTimeManager

# 1. Setup 및 Cleaning 관리자 초기화
setup_mgr = SetupTimeManager()
cleaning_mgr = CleaningTimeManager()

# 2. Setup times 설정
setup_times = setup_mgr.get_all_setup_times()

# 3. Cleaning requirements
cleaning_times = {
    'MC001': cleaning_mgr.get_cleaning_duration('MC001'),
    'MC002': cleaning_mgr.get_cleaning_duration('MC002'),
}

# 4. Solver 설정
weights = {'makespan': 1.0, 'cost': 0.8, 'tardiness': 2.0}
solver = MultiObjectiveSolver(weights=weights)

# 5. 최적화 실행
jobs = [
    {'wo_no': 'WO001', 'mc_cd': 'MC001', 'priority': 8, 'itm_id': 'ITEM_A', ...},
    {'wo_no': 'WO002', 'mc_cd': 'MC002', 'priority': 5, 'itm_id': 'ITEM_B', ...},
    # ...
]

result = solver.solve(
    scope_items=jobs,
    machines=['MC001', 'MC002'],
    setup_times=setup_times,
    cleaning_times=cleaning_times,
    machine_costs={'MC001': 100, 'MC002': 150}
)

print(f"Scheduled {len(result)} jobs")
```

### 예제 2: 대규모 스케줄링 (유전 알고리즘)

```python
from genetic_scheduler import HybridScheduler

# 자동으로 문제 크기에 따라 알고리즘 선택
scheduler = HybridScheduler(threshold=50)

# 500개 작업 -> GA 사용
large_jobs = [...]  # 500 jobs
result = scheduler.solve(large_jobs, machines)
```

### 예제 3: 실시간 긴급 주문 처리

```python
from realtime_rescheduler import RealtimeRescheduler

rescheduler = RealtimeRescheduler(strategy='minimal_disruption')

# 현재 스케줄
current_schedule = [...]  # 현재 진행 중인 스케줄

# 긴급 주문 발생
emergency = {
    'wo_no': 'URGENT_999',
    'mc_cd': 'MC001',
    'fr_ts': datetime.now().isoformat(),
    'to_ts': (datetime.now() + timedelta(hours=1)).isoformat(),
    'priority': 10
}

# 리스케줄링
new_schedule = rescheduler.reschedule_on_emergency_order(
    current_schedule=current_schedule,
    emergency_job=emergency,
    current_time=datetime.now(),
    priority=10
)

print(f"Rescheduled with emergency order")
```

### 예제 4: 기계 고장 대응

```python
# 기계 고장 발생
new_schedule = rescheduler.reschedule_on_breakdown(
    current_schedule=current_schedule,
    broken_machine='MC001',
    repair_time_minutes=180,  # 3시간 수리
    current_time=datetime.now()
)

# 영향받은 작업 확인
affected_jobs = [
    job for job in new_schedule
    if job['mc_cd'] == 'MC001'
]

print(f"{len(affected_jobs)} jobs affected by breakdown")
```

## 📊 성능 비교

| 알고리즘 | 작업 수 | 실행 시간 | 품질 |
|---------|--------|----------|------|
| CP-SAT | 10-50 | 1-10초 | 최적해 |
| GA | 50-500 | 5-30초 | 95-98% |
| Hybrid | 자동 | 최적화됨 | 최상 |

## 🔍 디버깅 팁

### 로깅 활성화

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 상세 로그
logging.getLogger('aps_solver_advanced').setLevel(logging.DEBUG)
logging.getLogger('genetic_scheduler').setLevel(logging.INFO)
```

### 솔루션 검증

```python
def validate_schedule(schedule, machines):
    """스케줄 유효성 검증"""
    # 1. 기계별 작업 overlap 체크
    for machine in machines:
        jobs = [j for j in schedule if j['mc_cd'] == machine]
        jobs.sort(key=lambda x: x['fr_ts'])

        for i in range(len(jobs) - 1):
            end1 = datetime.fromisoformat(jobs[i]['to_ts'])
            start2 = datetime.fromisoformat(jobs[i + 1]['fr_ts'])
            assert end1 <= start2, f"Overlap detected on {machine}"

    # 2. Freeze level 제약 체크
    # ...

    print("✅ Schedule validation passed")
```

## 📚 추가 리소스

- [OR-Tools Documentation](https://developers.google.com/optimization)
- [Genetic Algorithms Tutorial](https://en.wikipedia.org/wiki/Genetic_algorithm)
- [Job Shop Scheduling Problem](https://en.wikipedia.org/wiki/Job-shop_scheduling)

---

**버전**: 1.1.0
**최종 업데이트**: 2025-12-29
