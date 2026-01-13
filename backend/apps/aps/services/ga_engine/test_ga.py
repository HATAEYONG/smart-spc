"""
Test/Demo Script for Hybrid GA + Local Search

Usage:
    python manage.py shell < apps/aps/services/ga_engine/test_ga.py

Or in Django shell:
    from apps.aps.services.ga_engine.test_ga import run_demo
    run_demo()
"""
import random
from datetime import datetime, timedelta
from apps.aps.services.ga_engine import (
    run_ga_with_local_search,
    run_ga_only,
    run_local_search_only,
    compare_methods
)


def generate_test_jobs(num_orders=10, ops_per_order=3):
    """
    테스트용 작업 데이터 생성

    Args:
        num_orders: Order 수
        ops_per_order: Order당 Operation 수

    Returns:
        List of job dicts
    """
    jobs = []
    base_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

    machines = ['MC001', 'MC002', 'MC003', 'MC004', 'MC005']

    for order_idx in range(num_orders):
        order_id = f'WO{order_idx+1:03d}'

        # Order 납기일 (1-7일 후)
        due_date = base_time + timedelta(days=random.randint(1, 7))

        for op_idx in range(ops_per_order):
            # Operation별 처리시간 (30-180분)
            duration = random.randint(30, 180)

            # 자원 할당 (순차적 또는 랜덤)
            resource_code = machines[op_idx % len(machines)]

            job = {
                'wo_no': order_id,
                'order_id': order_id,
                'op_seq': op_idx,
                'resource_code': resource_code,
                'mc_cd': resource_code,
                'duration_minutes': duration,
                'due_date': due_date,
                'fr_ts': base_time,  # Planned start (will be optimized)
                'to_ts': base_time + timedelta(minutes=duration),
            }

            jobs.append(job)

    print(f"Generated {len(jobs)} jobs from {num_orders} orders")
    return jobs


def run_simple_demo():
    """
    간단한 GA+LS 데모
    """
    print("=" * 80)
    print("DEMO: Hybrid GA + Local Search")
    print("=" * 80)

    # 1. 테스트 데이터 생성
    print("\n[Step 1] Generating test jobs...")
    jobs = generate_test_jobs(num_orders=10, ops_per_order=3)

    # 2. GA + LS 실행
    print("\n[Step 2] Running Hybrid GA + Local Search...")
    result = run_ga_with_local_search(
        jobs=jobs,
        population_size=20,
        max_generations=30,
        crossover_rate=0.8,
        mutation_rate=0.1,
        use_local_search=True,
        local_search_iterations=30,
        verbose=True
    )

    # 3. 결과 출력
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"Algorithm: Hybrid GA + Local Search")
    print(f"Total Jobs: {result['metrics']['total_jobs']}")
    print(f"Makespan: {result['metrics']['makespan']:.0f} minutes")
    print(f"Total Tardiness: {result['metrics']['total_tardiness']:.0f} minutes")
    print(f"Tardy Jobs: {result['metrics']['tardy_jobs']}/{result['metrics']['total_jobs']}")
    print(f"Avg Utilization: {result['metrics']['avg_utilization']:.1f}%")
    print(f"Computation Time: {result['computation_time']:.2f} seconds")
    print(f"\nFitness Evolution:")
    print(f"  Initial: {result['initial_fitness']:.2f}")
    print(f"  GA Final: {result['ga_final_fitness']:.2f}")
    print(f"  LS Final: {result['ls_final_fitness']:.2f}")
    print(f"  Total Improvement: {(result['initial_fitness'] - result['best_fitness']) / result['initial_fitness'] * 100:.1f}%")

    # 4. Resource utilization
    print(f"\nResource Utilization:")
    for resource, util in sorted(result['metrics']['resource_utilization'].items()):
        print(f"  {resource}: {util:.1f}%")

    return result


def run_comparison_demo():
    """
    여러 방법 비교 데모
    """
    print("=" * 80)
    print("DEMO: Comparing Optimization Methods")
    print("=" * 80)

    # 테스트 데이터 생성
    print("\nGenerating test jobs...")
    jobs = generate_test_jobs(num_orders=8, ops_per_order=4)

    # 방법 비교
    print("\nComparing methods...")
    results = compare_methods(jobs)

    print("\nComparison completed! See results above.")
    return results


def run_scalability_test():
    """
    확장성 테스트 (다양한 크기의 문제)
    """
    print("=" * 80)
    print("SCALABILITY TEST")
    print("=" * 80)

    test_sizes = [
        (5, 2),   # 10 jobs
        (10, 3),  # 30 jobs
        (15, 3),  # 45 jobs
        (20, 3),  # 60 jobs
    ]

    results = []

    for num_orders, ops_per_order in test_sizes:
        total_jobs = num_orders * ops_per_order
        print(f"\n{'=' * 80}")
        print(f"Testing with {num_orders} orders × {ops_per_order} ops = {total_jobs} jobs")
        print(f"{'=' * 80}")

        jobs = generate_test_jobs(num_orders, ops_per_order)

        result = run_ga_with_local_search(
            jobs=jobs,
            population_size=30,
            max_generations=40,
            use_local_search=True,
            local_search_iterations=30,
            verbose=False
        )

        results.append({
            'total_jobs': total_jobs,
            'makespan': result['metrics']['makespan'],
            'tardiness': result['metrics']['total_tardiness'],
            'fitness': result['best_fitness'],
            'time': result['computation_time'],
        })

        print(f"  Makespan: {result['metrics']['makespan']:.0f} min")
        print(f"  Tardiness: {result['metrics']['total_tardiness']:.0f} min")
        print(f"  Time: {result['computation_time']:.2f} s")

    # Summary
    print(f"\n{'=' * 80}")
    print("SCALABILITY SUMMARY")
    print(f"{'=' * 80}")
    print(f"{'Jobs':>8} {'Makespan':>12} {'Tardiness':>12} {'Fitness':>12} {'Time (s)':>10}")
    print("-" * 80)

    for r in results:
        print(
            f"{r['total_jobs']:>8} "
            f"{r['makespan']:>12.0f} "
            f"{r['tardiness']:>12.0f} "
            f"{r['fitness']:>12.2f} "
            f"{r['time']:>10.2f}"
        )

    return results


def run_parameter_tuning():
    """
    파라미터 튜닝 테스트
    """
    print("=" * 80)
    print("PARAMETER TUNING TEST")
    print("=" * 80)

    jobs = generate_test_jobs(num_orders=10, ops_per_order=3)

    # Test different mutation rates
    print("\n[1] Testing Mutation Rates")
    print("-" * 80)

    mutation_rates = [0.05, 0.1, 0.2, 0.3]

    for mut_rate in mutation_rates:
        result = run_ga_with_local_search(
            jobs=jobs,
            population_size=30,
            max_generations=30,
            mutation_rate=mut_rate,
            use_local_search=False,
            verbose=False
        )

        print(f"Mutation Rate: {mut_rate:.2f} → Fitness: {result['best_fitness']:.2f}")

    # Test different population sizes
    print("\n[2] Testing Population Sizes")
    print("-" * 80)

    pop_sizes = [10, 20, 30, 50]

    for pop_size in pop_sizes:
        result = run_ga_with_local_search(
            jobs=jobs,
            population_size=pop_size,
            max_generations=30,
            use_local_search=False,
            verbose=False
        )

        print(f"Population Size: {pop_size:>3} → Fitness: {result['best_fitness']:.2f}, Time: {result['computation_time']:.2f}s")

    # Test Local Search impact
    print("\n[3] Testing Local Search Impact")
    print("-" * 80)

    # Without LS
    result_no_ls = run_ga_only(jobs, population_size=30, max_generations=30)

    # With LS
    result_with_ls = run_ga_with_local_search(
        jobs=jobs,
        population_size=30,
        max_generations=30,
        use_local_search=True,
        local_search_iterations=50,
        verbose=False
    )

    print(f"GA only:    Fitness = {result_no_ls['best_fitness']:.2f}, Time = {result_no_ls['computation_time']:.2f}s")
    print(f"GA + LS:    Fitness = {result_with_ls['best_fitness']:.2f}, Time = {result_with_ls['computation_time']:.2f}s")
    print(f"Improvement: {(result_no_ls['best_fitness'] - result_with_ls['best_fitness']) / result_no_ls['best_fitness'] * 100:.1f}%")


def run_demo():
    """
    전체 데모 실행

    Usage:
        from apps.aps.services.ga_engine.test_ga import run_demo
        run_demo()
    """
    print("\n" + "=" * 80)
    print(" " * 20 + "GA ENGINE DEMO")
    print("=" * 80)

    print("\nSelect demo:")
    print("1. Simple Demo (Hybrid GA + LS)")
    print("2. Comparison Demo (All Methods)")
    print("3. Scalability Test")
    print("4. Parameter Tuning")
    print("5. Run All")

    try:
        choice = input("\nEnter choice (1-5): ").strip()
    except:
        # Default to simple demo if running non-interactively
        choice = "1"

    if choice == "1":
        return run_simple_demo()
    elif choice == "2":
        return run_comparison_demo()
    elif choice == "3":
        return run_scalability_test()
    elif choice == "4":
        return run_parameter_tuning()
    elif choice == "5":
        run_simple_demo()
        print("\n\n")
        run_comparison_demo()
        print("\n\n")
        run_scalability_test()
        print("\n\n")
        run_parameter_tuning()
    else:
        print("Invalid choice, running simple demo...")
        return run_simple_demo()


if __name__ == "__main__":
    # Auto-run when executed
    run_demo()
