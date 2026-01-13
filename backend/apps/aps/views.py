from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import models
from django.db.models import Count, Avg, Sum, F, Q, Max
from apps.core.models import StageFactPlanOut
from .models import AlgorithmComparison, BottleneckAnalysis, MachineLoadHistory
from .serializers import (
    StageFactPlanOutSerializer,
    AlgorithmComparisonSerializer,
    ComparisonRequestSerializer,
    BottleneckAnalysisSerializer,
    MachineLoadHistorySerializer,
    BottleneckAnalysisRequestSerializer,
)
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import time


class PlansViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for APS plans (Gantt view)
    Supports filtering by date and mc_cd
    """
    queryset = StageFactPlanOut.objects.all().order_by("mc_cd", "fr_ts")
    serializer_class = StageFactPlanOutSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        # Filter by date
        date = self.request.query_params.get("date")
        if date:
            qs = qs.filter(fr_ts__date=date)

        # Filter by date range
        fr_date = self.request.query_params.get("fr_date")
        to_date = self.request.query_params.get("to_date")
        if fr_date:
            qs = qs.filter(fr_ts__gte=fr_date)
        if to_date:
            qs = qs.filter(to_ts__lte=to_date)

        # Filter by machine
        mc_cd = self.request.query_params.get("mc_cd")
        if mc_cd:
            qs = qs.filter(mc_cd=mc_cd)

        return qs


class AlgorithmComparisonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for algorithm comparison
    """
    queryset = AlgorithmComparison.objects.all()
    serializer_class = AlgorithmComparisonSerializer

    @action(detail=False, methods=["post"])
    def run_comparison(self, request):
        """
        POST /api/aps/comparison/run_comparison/
        Run algorithm comparison
        """
        serializer = ComparisonRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job_count = serializer.validated_data["job_count"]
        machine_count = serializer.validated_data["machine_count"]

        # Generate test data
        jobs = self._generate_test_jobs(job_count, machine_count)

        # Run Genetic Algorithm (simulated)
        ga_start = time.time()
        ga_result = self._run_genetic_algorithm(jobs)
        ga_runtime = time.time() - ga_start

        # Run Dispatch Rules
        dispatch_results = self._run_dispatch_rules(jobs)

        # Find best rule
        best_rule = min(dispatch_results.items(), key=lambda x: x[1]["makespan"])[0]

        # Save comparison
        comparison = AlgorithmComparison.objects.create(
            job_count=job_count,
            machine_count=machine_count,
            ga_makespan=ga_result["makespan"],
            ga_tardiness=ga_result["tardiness"],
            ga_cost=ga_result["cost"],
            ga_runtime=ga_runtime,
            dispatch_results=dispatch_results,
            best_rule=best_rule,
        )

        return Response(AlgorithmComparisonSerializer(comparison).data, status=status.HTTP_201_CREATED)

    def _generate_test_jobs(self, job_count: int, machine_count: int):
        """Generate random test jobs"""
        jobs = []
        machines = [f"MC{i:03d}" for i in range(1, machine_count + 1)]
        current_time = datetime.now()

        for i in range(job_count):
            job = {
                "wo_no": f"WO{i+1:04d}",
                "itm_id": f"ITM{random.randint(1, 20):03d}",
                "mc_cd": random.choice(machines),
                "process_time": random.randint(30, 240),  # 30 min to 4 hours
                "due_date": current_time + timedelta(hours=random.randint(4, 48)),
                "priority": random.randint(1, 5),
                "arrival_time": current_time - timedelta(minutes=random.randint(0, 60)),
            }
            jobs.append(job)

        return jobs

    def _run_genetic_algorithm(self, jobs):
        """Simulate genetic algorithm (replace with actual implementation)"""
        # Simulated GA results
        total_process_time = sum(j["process_time"] for j in jobs)
        machine_count = len(set(j["mc_cd"] for j in jobs))

        makespan = total_process_time / machine_count * random.uniform(0.85, 0.95)
        tardiness = sum(random.uniform(0, 30) for _ in range(int(len(jobs) * 0.2)))
        cost = makespan * random.uniform(10, 15)

        return {
            "makespan": makespan,
            "tardiness": tardiness,
            "cost": cost,
        }

    def _run_dispatch_rules(self, jobs):
        """Run all dispatch rules"""
        rules = ["FIFO", "SPT", "LPT", "EDD", "MS", "CR", "PRIORITY"]
        results = {}

        total_process_time = sum(j["process_time"] for j in jobs)
        machine_count = len(set(j["mc_cd"] for j in jobs))

        for rule in rules:
            # Simulated dispatch rule results
            # Different rules have different makespan multipliers
            multipliers = {
                "FIFO": 1.0,
                "SPT": 0.92,
                "LPT": 1.08,
                "EDD": 0.95,
                "MS": 0.93,
                "CR": 0.94,
                "PRIORITY": 0.96,
            }

            makespan = total_process_time / machine_count * multipliers[rule]
            tardiness = sum(random.uniform(0, 50) for _ in range(int(len(jobs) * random.uniform(0.15, 0.35))))

            results[rule] = {
                "makespan": makespan,
                "total_tardiness": tardiness,
                "max_tardiness": tardiness / 2 if tardiness > 0 else 0,
                "num_tardy_jobs": int(len(jobs) * random.uniform(0.15, 0.35)),
                "total_jobs": len(jobs),
                "avg_flow_time": makespan * random.uniform(0.6, 0.9),
            }

        return results


class BottleneckAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for bottleneck analysis
    """
    queryset = BottleneckAnalysis.objects.all()
    serializer_class = BottleneckAnalysisSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        # Filter by machine
        mc_cd = self.request.query_params.get("mc_cd")
        if mc_cd:
            qs = qs.filter(mc_cd=mc_cd)

        # Filter bottlenecks only
        bottlenecks_only = self.request.query_params.get("bottlenecks_only")
        if bottlenecks_only == "true":
            qs = qs.filter(is_bottleneck=True)

        return qs

    @action(detail=False, methods=["post"])
    def run_analysis(self, request):
        """
        POST /api/aps/bottleneck/run_analysis/
        Run bottleneck analysis on current plan
        """
        serializer = BottleneckAnalysisRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        threshold = serializer.validated_data["threshold"]
        start_date = serializer.validated_data.get("start_date") or timezone.now()
        end_date = serializer.validated_data.get("end_date") or (start_date + timedelta(days=7))

        # Analyze bottlenecks
        results = self._analyze_bottlenecks(start_date, end_date, threshold)

        return Response(
            {
                "analysis_count": len(results),
                "bottleneck_count": sum(1 for r in results if r["is_bottleneck"]),
                "results": results,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def heatmap(self, request):
        """
        GET /api/aps/bottleneck/heatmap/
        Get machine utilization heatmap data
        """
        days = int(request.query_params.get("days", 7))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Get load history
        history = MachineLoadHistory.objects.filter(
            timestamp__gte=start_date, timestamp__lte=end_date
        ).order_by("mc_cd", "timestamp")

        # Group by machine and time bucket
        heatmap_data = []
        machines = history.values_list("mc_cd", flat=True).distinct()

        for mc_cd in machines:
            mc_history = history.filter(mc_cd=mc_cd)
            utilization_series = list(
                mc_history.values("timestamp", "utilization_rate").order_by("timestamp")
            )

            heatmap_data.append(
                {
                    "mc_cd": mc_cd,
                    "avg_utilization": mc_history.aggregate(Avg("utilization_rate"))["utilization_rate__avg"] or 0,
                    "max_utilization": mc_history.aggregate(max_util=Max("utilization_rate"))["max_util"] or 0,
                    "data_points": utilization_series,
                }
            )

        return Response({"heatmap": heatmap_data})

    @action(detail=False, methods=["get"])
    def trends(self, request):
        """
        GET /api/aps/bottleneck/trends/
        Get bottleneck trends over time
        """
        days = int(request.query_params.get("days", 30))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Get historical bottleneck data
        analyses = BottleneckAnalysis.objects.filter(
            created_at__gte=start_date, created_at__lte=end_date, is_bottleneck=True
        ).order_by("created_at")

        # Group by date and machine
        trend_data = {}
        for analysis in analyses:
            date_key = analysis.created_at.date().isoformat()
            if date_key not in trend_data:
                trend_data[date_key] = {"date": date_key, "bottleneck_count": 0, "machines": []}

            trend_data[date_key]["bottleneck_count"] += 1
            if analysis.mc_cd not in trend_data[date_key]["machines"]:
                trend_data[date_key]["machines"].append(analysis.mc_cd)

        return Response({"trends": list(trend_data.values())})

    def _analyze_bottlenecks(
        self, start_date: datetime, end_date: datetime, threshold: float
    ) -> List[Dict]:
        """Analyze bottlenecks in the given time window"""
        results = []

        # Get all plans in the time window
        plans = StageFactPlanOut.objects.filter(
            Q(fr_ts__gte=start_date, fr_ts__lte=end_date) | Q(to_ts__gte=start_date, to_ts__lte=end_date)
        )

        # Group by machine
        machines = plans.values_list("mc_cd", flat=True).distinct()

        for mc_cd in machines:
            mc_plans = plans.filter(mc_cd=mc_cd).order_by("fr_ts")

            # Calculate metrics
            metrics = self._calculate_machine_metrics(mc_cd, mc_plans, start_date, end_date)

            # Generate recommendations
            recommendations = self._generate_recommendations(mc_cd, metrics)

            # Determine if bottleneck
            is_bottleneck = metrics["utilization_rate"] >= threshold or metrics["bottleneck_score"] >= 70

            # Save analysis
            analysis = BottleneckAnalysis.objects.create(
                mc_cd=mc_cd,
                utilization_rate=metrics["utilization_rate"],
                queue_length=metrics["queue_length"],
                avg_waiting_time=metrics["avg_waiting_time"],
                bottleneck_score=metrics["bottleneck_score"],
                is_bottleneck=is_bottleneck,
                affected_jobs=metrics["affected_jobs"],
                total_delay=metrics["total_delay"],
                recommendations=recommendations,
                analysis_start=start_date,
                analysis_end=end_date,
            )

            # Save load history
            MachineLoadHistory.objects.create(
                mc_cd=mc_cd,
                timestamp=timezone.now(),
                active_jobs=metrics["active_jobs"],
                queued_jobs=metrics["queue_length"],
                utilization_rate=metrics["utilization_rate"],
                total_capacity=metrics["total_capacity"],
                used_capacity=metrics["used_capacity"],
                available_capacity=metrics["available_capacity"],
            )

            results.append(BottleneckAnalysisSerializer(analysis).data)

        return results

    def _calculate_machine_metrics(
        self, mc_cd: str, plans, start_date: datetime, end_date: datetime
    ) -> Dict:
        """Calculate utilization and bottleneck metrics for a machine"""
        total_time_window = (end_date - start_date).total_seconds() / 60  # minutes

        # Calculate total processing time
        total_process_time = 0
        overlaps = 0
        waiting_times = []

        plan_list = list(plans)
        for i, plan in enumerate(plan_list):
            duration = (plan.to_ts - plan.fr_ts).total_seconds() / 60
            total_process_time += duration

            # Check for overlaps (indicates queueing)
            if i > 0:
                prev_plan = plan_list[i - 1]
                if plan.fr_ts < prev_plan.to_ts:
                    overlaps += 1
                    waiting_time = (prev_plan.to_ts - plan.fr_ts).total_seconds() / 60
                    waiting_times.append(max(0, waiting_time))

        # Utilization rate
        utilization_rate = min(100, (total_process_time / total_time_window * 100)) if total_time_window > 0 else 0

        # Queue metrics
        queue_length = overlaps
        avg_waiting_time = sum(waiting_times) / len(waiting_times) if waiting_times else 0

        # Bottleneck score (0-100)
        # Higher utilization + longer queues + more waiting = higher score
        bottleneck_score = (
            utilization_rate * 0.5 + min(queue_length * 10, 30) + min(avg_waiting_time / 10, 20)
        )

        # Affected jobs and delays
        affected_jobs = len(plan_list)
        total_delay = sum(waiting_times)

        return {
            "utilization_rate": round(utilization_rate, 2),
            "queue_length": queue_length,
            "avg_waiting_time": round(avg_waiting_time, 2),
            "bottleneck_score": round(min(100, bottleneck_score), 2),
            "affected_jobs": affected_jobs,
            "total_delay": round(total_delay, 2),
            "active_jobs": len([p for p in plan_list if p.fr_ts <= timezone.now() <= p.to_ts]),
            "total_capacity": round(total_time_window, 2),
            "used_capacity": round(total_process_time, 2),
            "available_capacity": round(max(0, total_time_window - total_process_time), 2),
        }

    def _generate_recommendations(self, mc_cd: str, metrics: Dict) -> List[Dict]:
        """Generate recommendations based on bottleneck analysis"""
        recommendations = []

        utilization = metrics["utilization_rate"]
        queue_length = metrics["queue_length"]
        avg_waiting = metrics["avg_waiting_time"]

        # High utilization
        if utilization >= 90:
            recommendations.append(
                {
                    "type": "capacity",
                    "priority": "high",
                    "title": "기계 용량 증설 필요",
                    "description": f"{mc_cd}의 가동률이 {utilization:.1f}%로 매우 높습니다. 추가 기계 배치를 고려하세요.",
                    "actions": ["추가 기계 투입", "작업 재배치", "교대 근무 확대"],
                }
            )
        elif utilization >= 80:
            recommendations.append(
                {
                    "type": "capacity",
                    "priority": "medium",
                    "title": "작업 부하 분산 권장",
                    "description": f"{mc_cd}의 가동률이 {utilization:.1f}%입니다. 다른 기계로 일부 작업을 분산할 수 있습니다.",
                    "actions": ["대체 기계 활용", "작업 우선순위 조정"],
                }
            )

        # Long queues
        if queue_length >= 5:
            recommendations.append(
                {
                    "type": "scheduling",
                    "priority": "high",
                    "title": "작업 대기열 최적화",
                    "description": f"{queue_length}개의 작업이 대기 중입니다. 스케줄링 규칙을 재검토하세요.",
                    "actions": ["SPT/EDD 룰 적용", "긴급 작업 우선 처리", "배치 크기 조정"],
                }
            )
        elif queue_length >= 3:
            recommendations.append(
                {
                    "type": "scheduling",
                    "priority": "medium",
                    "title": "대기 시간 감소 필요",
                    "description": f"평균 대기 시간이 {avg_waiting:.1f}분입니다. 작업 순서를 최적화하세요.",
                    "actions": ["작업 순서 재배치", "병렬 처리 검토"],
                }
            )

        # Load leveling
        if utilization >= 75 and metrics["available_capacity"] > 100:
            recommendations.append(
                {
                    "type": "load_leveling",
                    "priority": "low",
                    "title": "부하 평준화 기회",
                    "description": f"여유 용량 {metrics['available_capacity']:.0f}분을 활용하여 부하를 평준화할 수 있습니다.",
                    "actions": ["작업 시간 분산", "비긴급 작업 조정"],
                }
            )

        # No issues
        if not recommendations:
            recommendations.append(
                {
                    "type": "ok",
                    "priority": "info",
                    "title": "정상 가동 중",
                    "description": f"{mc_cd}는 현재 최적의 상태로 가동 중입니다.",
                    "actions": [],
                }
            )

        return recommendations
