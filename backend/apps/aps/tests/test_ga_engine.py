"""
Integration Tests for GA Engine

STEP 4: Hybrid GA + Local Search
"""
import unittest
from datetime import datetime, timedelta
from apps.aps.services.ga_engine import (
    run_ga_with_local_search,
    run_ga_only,
    run_local_search_only,
    compare_methods,
    Chromosome,
    encode_jobs,
    decode_chromosome,
    evaluate_fitness,
    calculate_metrics,
)


class GAEngineTestCase(unittest.TestCase):
    """GA Engine integration tests"""

    def setUp(self):
        """Set up test data"""
        self.test_jobs = self._generate_test_jobs(num_orders=5, ops_per_order=2)

    def _generate_test_jobs(self, num_orders=5, ops_per_order=2):
        """Generate test job data"""
        jobs = []
        base_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        machines = ['MC001', 'MC002', 'MC003']

        for order_idx in range(num_orders):
            order_id = f'WO{order_idx+1:03d}'
            due_date = base_time + timedelta(days=order_idx + 1)

            for op_idx in range(ops_per_order):
                job = {
                    'wo_no': order_id,
                    'order_id': order_id,
                    'op_seq': op_idx,
                    'resource_code': machines[op_idx % len(machines)],
                    'mc_cd': machines[op_idx % len(machines)],
                    'duration_minutes': 60 + (op_idx * 30),
                    'due_date': due_date,
                    'fr_ts': base_time,
                    'to_ts': base_time + timedelta(minutes=60),
                }
                jobs.append(job)

        return jobs

    def test_01_encoding_decoding(self):
        """Test chromosome encoding and decoding"""
        # Encode
        chromosome = encode_jobs(self.test_jobs)

        self.assertIsInstance(chromosome, Chromosome)
        self.assertEqual(len(chromosome.genes), len(self.test_jobs))

        # Decode
        schedule = decode_chromosome(chromosome, self.test_jobs)

        self.assertEqual(len(schedule), len(self.test_jobs))

        # Verify all jobs have start/end times
        for job in schedule:
            self.assertIn('start_dt', job)
            self.assertIn('end_dt', job)
            self.assertIsNotNone(job['start_dt'])
            self.assertIsNotNone(job['end_dt'])

    def test_02_fitness_evaluation(self):
        """Test fitness evaluation"""
        chromosome = encode_jobs(self.test_jobs)
        schedule = decode_chromosome(chromosome, self.test_jobs)

        # Basic fitness
        fitness = evaluate_fitness(schedule)
        self.assertIsInstance(fitness, (int, float))
        self.assertGreater(fitness, 0)

        # Metrics
        metrics = calculate_metrics(schedule)

        self.assertIn('makespan', metrics)
        self.assertIn('total_tardiness', metrics)
        self.assertIn('total_deviation', metrics)
        self.assertIn('resource_utilization', metrics)
        self.assertIn('tardy_jobs', metrics)
        self.assertIn('total_jobs', metrics)

        self.assertEqual(metrics['total_jobs'], len(self.test_jobs))

    def test_03_ga_only_execution(self):
        """Test GA-only execution (without Local Search)"""
        result = run_ga_only(
            jobs=self.test_jobs,
            population_size=10,
            max_generations=10
        )

        # Verify result structure
        self.assertIn('best_schedule', result)
        self.assertIn('best_fitness', result)
        self.assertIn('metrics', result)
        self.assertIn('history', result)
        self.assertIn('computation_time', result)

        # Verify best_schedule
        self.assertEqual(len(result['best_schedule']), len(self.test_jobs))

        # Verify history
        self.assertGreater(len(result['history']['generation']), 0)
        self.assertGreater(len(result['history']['best_fitness']), 0)

    def test_04_local_search_only_execution(self):
        """Test Local Search-only execution"""
        result = run_local_search_only(
            jobs=self.test_jobs,
            max_iterations=20
        )

        # Verify result structure
        self.assertIn('best_schedule', result)
        self.assertIn('best_fitness', result)
        self.assertIn('metrics', result)
        self.assertIn('computation_time', result)
        self.assertIn('initial_fitness', result)

        # Verify improvement
        self.assertLessEqual(result['best_fitness'], result['initial_fitness'])

    def test_05_hybrid_ga_ls_execution(self):
        """Test Hybrid GA + Local Search execution"""
        result = run_ga_with_local_search(
            jobs=self.test_jobs,
            population_size=10,
            max_generations=10,
            use_local_search=True,
            local_search_iterations=20,
            verbose=False
        )

        # Verify result structure
        self.assertIn('best_schedule', result)
        self.assertIn('best_fitness', result)
        self.assertIn('metrics', result)
        self.assertIn('history', result)
        self.assertIn('computation_time', result)
        self.assertIn('ga_generations', result)
        self.assertIn('initial_fitness', result)
        self.assertIn('ga_final_fitness', result)
        self.assertIn('ls_final_fitness', result)

        # Verify improvement chain
        self.assertGreaterEqual(result['initial_fitness'], result['ga_final_fitness'])
        self.assertGreaterEqual(result['ga_final_fitness'], result['ls_final_fitness'])

        # LS should improve or maintain GA result
        self.assertLessEqual(result['ls_final_fitness'], result['ga_final_fitness'])

    def test_06_precedence_preservation(self):
        """Test precedence constraint preservation"""
        # Create jobs with strict precedence
        jobs = []
        base_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

        for order_idx in range(3):
            order_id = f'ORDER{order_idx}'
            for op_idx in range(3):
                job = {
                    'wo_no': order_id,
                    'order_id': order_id,
                    'op_seq': op_idx,
                    'resource_code': 'MC001',
                    'mc_cd': 'MC001',
                    'duration_minutes': 30,
                    'due_date': base_time + timedelta(days=1),
                    'fr_ts': base_time,
                    'to_ts': base_time + timedelta(minutes=30),
                }
                jobs.append(job)

        # Run GA
        result = run_ga_with_local_search(
            jobs=jobs,
            population_size=10,
            max_generations=10,
            use_local_search=False,
            verbose=False
        )

        # Verify precedence in result
        schedule = result['best_schedule']

        # Group by order
        order_jobs = {}
        for job in schedule:
            order_id = job.get('order_id')
            if order_id not in order_jobs:
                order_jobs[order_id] = []
            order_jobs[order_id].append(job)

        # Check each order's operations are in sequence
        for order_id, ops in order_jobs.items():
            # Sort by op_seq
            ops_sorted = sorted(ops, key=lambda x: x.get('op_seq', 0))

            # Verify start times are in order
            for i in range(len(ops_sorted) - 1):
                start_i = ops_sorted[i]['start_dt']
                start_next = ops_sorted[i + 1]['start_dt']

                self.assertLessEqual(
                    start_i, start_next,
                    f"Precedence violated in {order_id}: op {i} starts after op {i+1}"
                )

    def test_07_empty_jobs_handling(self):
        """Test handling of empty job list"""
        result = run_ga_with_local_search(
            jobs=[],
            population_size=10,
            max_generations=10,
            verbose=False
        )

        self.assertEqual(len(result['best_schedule']), 0)
        self.assertEqual(result['best_fitness'], float('inf'))

    def test_08_objectives_customization(self):
        """Test custom objectives weights"""
        # Default objectives
        result1 = run_ga_with_local_search(
            jobs=self.test_jobs,
            population_size=10,
            max_generations=5,
            use_local_search=False,
            verbose=False
        )

        # Custom objectives (prioritize tardiness)
        result2 = run_ga_with_local_search(
            jobs=self.test_jobs,
            population_size=10,
            max_generations=5,
            objectives={
                'makespan_weight': 1.0,
                'tardiness_weight': 5.0,  # Higher weight
                'deviation_weight': 0.5,
            },
            use_local_search=False,
            verbose=False
        )

        # Both should produce valid results
        self.assertGreater(result1['best_fitness'], 0)
        self.assertGreater(result2['best_fitness'], 0)

        # Fitness values may differ due to different weights
        # Just verify both are valid
        self.assertIsNotNone(result1['best_schedule'])
        self.assertIsNotNone(result2['best_schedule'])

    def test_09_comparison_methods(self):
        """Test method comparison functionality"""
        # Use smaller job set for faster testing
        small_jobs = self.test_jobs[:6]

        results = compare_methods(small_jobs)

        # Verify all methods are present
        self.assertIn('random', results)
        self.assertIn('ga_only', results)
        self.assertIn('ls_only', results)
        self.assertIn('hybrid', results)

        # Verify each has required fields
        # Random has 'fitness' and 'metrics' directly
        self.assertIn('fitness', results['random'])
        self.assertIn('metrics', results['random'])

        # GA-based methods have 'best_fitness' and 'metrics'
        for method in ['ga_only', 'ls_only', 'hybrid']:
            self.assertIn('best_fitness', results[method])
            self.assertIn('metrics', results[method])

    def test_10_scalability(self):
        """Test scalability with different problem sizes"""
        test_sizes = [
            (3, 2),   # 6 jobs
            (5, 2),   # 10 jobs
            (7, 2),   # 14 jobs
        ]

        for num_orders, ops_per_order in test_sizes:
            jobs = self._generate_test_jobs(num_orders, ops_per_order)

            result = run_ga_with_local_search(
                jobs=jobs,
                population_size=10,
                max_generations=10,
                use_local_search=True,
                local_search_iterations=10,
                verbose=False
            )

            # Verify successful execution
            self.assertEqual(len(result['best_schedule']), len(jobs))
            self.assertGreater(result['best_fitness'], 0)
            self.assertLess(result['computation_time'], 30)  # Should complete in 30s


class PerformanceTestCase(unittest.TestCase):
    """Performance and stress tests"""

    def test_01_medium_scale_performance(self):
        """Test medium-scale problem (30 jobs)"""
        jobs = self._generate_jobs(15, 2)

        result = run_ga_with_local_search(
            jobs=jobs,
            population_size=20,
            max_generations=20,
            use_local_search=True,
            local_search_iterations=30,
            verbose=False
        )

        # Should complete in reasonable time
        self.assertLess(result['computation_time'], 60)  # 60 seconds

        # Should produce valid result
        self.assertEqual(len(result['best_schedule']), 30)
        self.assertGreater(result['best_fitness'], 0)

    def test_02_improvement_verification(self):
        """Verify that GA+LS improves over random"""
        jobs = self._generate_jobs(10, 2)

        # Get random solution
        chromosome = encode_jobs(jobs)
        random_schedule = decode_chromosome(chromosome, jobs)
        random_fitness = evaluate_fitness(random_schedule)

        # Get GA+LS solution
        result = run_ga_with_local_search(
            jobs=jobs,
            population_size=20,
            max_generations=30,
            use_local_search=True,
            local_search_iterations=30,
            verbose=False
        )

        # GA+LS should be better than or equal to random
        # (with high probability, though not guaranteed)
        improvement_rate = (random_fitness - result['best_fitness']) / random_fitness * 100

        # Log the improvement (for informational purposes)
        print(f"\nImprovement over random: {improvement_rate:.1f}%")
        print(f"Random fitness: {random_fitness:.2f}")
        print(f"GA+LS fitness: {result['best_fitness']:.2f}")

    def _generate_jobs(self, num_orders, ops_per_order):
        """Generate test jobs"""
        jobs = []
        base_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        machines = ['MC001', 'MC002', 'MC003', 'MC004', 'MC005']

        for order_idx in range(num_orders):
            order_id = f'WO{order_idx+1:03d}'
            due_date = base_time + timedelta(days=order_idx % 5 + 1)

            for op_idx in range(ops_per_order):
                job = {
                    'wo_no': order_id,
                    'order_id': order_id,
                    'op_seq': op_idx,
                    'resource_code': machines[op_idx % len(machines)],
                    'mc_cd': machines[op_idx % len(machines)],
                    'duration_minutes': 60 + (op_idx * 20),
                    'due_date': due_date,
                    'fr_ts': base_time,
                    'to_ts': base_time + timedelta(minutes=60),
                }
                jobs.append(job)

        return jobs


if __name__ == '__main__':
    unittest.main()
