from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import models
from datetime import timedelta
from apps.core.models import StageFactPlanOut
from .models import AlgorithmComparison, BottleneckAnalysis


class PerformanceMetricsViewSet(viewsets.ViewSet):
    """
    API endpoint for performance metrics and KPIs
    """

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """
        GET /api/aps/performance/summary/
        Get overall performance summary
        """
        days = int(request.query_params.get("days", 7))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Get plans in time range
        plans = StageFactPlanOut.objects.filter(fr_ts__gte=start_date, fr_ts__lte=end_date)

        if not plans.exists():
            return Response(
                {
                    "summary": {
                        "total_jobs": 0,
                        "total_machines": 0,
                        "avg_makespan": 0,
                        "total_tardiness": 0,
                        "avg_utilization": 0,
                        "throughput": 0,
                    }
                }
            )

        # Calculate metrics
        total_jobs = plans.count()
        machines = plans.values_list("mc_cd", flat=True).distinct()
        total_machines = len(machines)

        # Makespan (max completion time - min start time)
        all_times = plans.aggregate(min_start=models.Min("fr_ts"), max_end=models.Max("to_ts"))
        if all_times["min_start"] and all_times["max_end"]:
            makespan = (all_times["max_end"] - all_times["min_start"]).total_seconds() / 60
        else:
            makespan = 0

        # Utilization per machine
        utilizations = []
        for mc_cd in machines:
            mc_plans = plans.filter(mc_cd=mc_cd)
            total_process_time = sum([(p.to_ts - p.fr_ts).total_seconds() / 60 for p in mc_plans])
            if makespan > 0:
                utilizations.append(total_process_time / makespan * 100)

        avg_utilization = sum(utilizations) / len(utilizations) if utilizations else 0

        # Throughput (jobs per day)
        time_window_days = (end_date - start_date).total_seconds() / (24 * 3600)
        throughput = total_jobs / time_window_days if time_window_days > 0 else 0

        return Response(
            {
                "summary": {
                    "total_jobs": total_jobs,
                    "total_machines": total_machines,
                    "avg_makespan": round(makespan, 2),
                    "total_tardiness": 0,  # Placeholder
                    "avg_utilization": round(avg_utilization, 2),
                    "throughput": round(throughput, 2),
                }
            }
        )

    @action(detail=False, methods=["get"])
    def machine_comparison(self, request):
        """
        GET /api/aps/performance/machine_comparison/
        Compare performance across machines
        """
        days = int(request.query_params.get("days", 7))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        plans = StageFactPlanOut.objects.filter(fr_ts__gte=start_date, fr_ts__lte=end_date)
        machines = plans.values_list("mc_cd", flat=True).distinct()

        comparison_data = []
        for mc_cd in machines:
            mc_plans = plans.filter(mc_cd=mc_cd)
            job_count = mc_plans.count()

            if job_count == 0:
                continue

            # Calculate total process time
            total_process_time = sum([(p.to_ts - p.fr_ts).total_seconds() / 60 for p in mc_plans])

            # Time window
            mc_times = mc_plans.aggregate(min_start=models.Min("fr_ts"), max_end=models.Max("to_ts"))
            if mc_times["min_start"] and mc_times["max_end"]:
                time_window = (mc_times["max_end"] - mc_times["min_start"]).total_seconds() / 60
                utilization = (total_process_time / time_window * 100) if time_window > 0 else 0
            else:
                utilization = 0

            comparison_data.append(
                {
                    "mc_cd": mc_cd,
                    "job_count": job_count,
                    "total_process_time": round(total_process_time, 2),
                    "utilization": round(utilization, 2),
                    "avg_job_duration": round(total_process_time / job_count, 2),
                }
            )

        # Sort by utilization descending
        comparison_data.sort(key=lambda x: x["utilization"], reverse=True)

        return Response({"machines": comparison_data})

    @action(detail=False, methods=["get"])
    def trends(self, request):
        """
        GET /api/aps/performance/trends/
        Get performance trends over time
        """
        days = int(request.query_params.get("days", 30))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Group by day
        trends = []
        current_date = start_date.date()
        end_date_only = end_date.date()

        while current_date <= end_date_only:
            next_date = current_date + timedelta(days=1)

            # Get plans for this day
            day_plans = StageFactPlanOut.objects.filter(fr_ts__date=current_date)

            job_count = day_plans.count()

            if job_count > 0:
                # Calculate utilization
                machines = day_plans.values_list("mc_cd", flat=True).distinct()
                total_process_time = sum([(p.to_ts - p.fr_ts).total_seconds() / 60 for p in day_plans])
                # Assume 24 hours available per machine
                total_available = len(machines) * 24 * 60
                utilization = (total_process_time / total_available * 100) if total_available > 0 else 0

                trends.append(
                    {
                        "date": current_date.isoformat(),
                        "job_count": job_count,
                        "utilization": round(utilization, 2),
                        "machine_count": len(machines),
                    }
                )

            current_date = next_date

        return Response({"trends": trends})

    @action(detail=False, methods=["get"])
    def algorithm_history(self, request):
        """
        GET /api/aps/performance/algorithm_history/
        Get algorithm comparison history
        """
        limit = int(request.query_params.get("limit", 10))

        comparisons = AlgorithmComparison.objects.all()[:limit]

        history = []
        for comp in comparisons:
            best_dispatch_makespan = (
                comp.dispatch_results.get(comp.best_rule, {}).get("makespan", 0)
                if comp.dispatch_results and comp.best_rule
                else 0
            )

            improvement = 0
            if best_dispatch_makespan > 0:
                improvement = (best_dispatch_makespan - comp.ga_makespan) / best_dispatch_makespan * 100

            history.append(
                {
                    "comparison_id": comp.comparison_id,
                    "created_at": comp.created_at.isoformat(),
                    "job_count": comp.job_count,
                    "machine_count": comp.machine_count,
                    "ga_makespan": comp.ga_makespan,
                    "best_rule": comp.best_rule,
                    "best_rule_makespan": best_dispatch_makespan,
                    "improvement": round(improvement, 2),
                }
            )

        return Response({"history": history})

    @action(detail=False, methods=["get"])
    def bottleneck_summary(self, request):
        """
        GET /api/aps/performance/bottleneck_summary/
        Get bottleneck summary
        """
        days = int(request.query_params.get("days", 7))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Get recent bottlenecks
        bottlenecks = BottleneckAnalysis.objects.filter(
            created_at__gte=start_date, created_at__lte=end_date, is_bottleneck=True
        ).order_by("-bottleneck_score")

        summary = {
            "total_bottlenecks": bottlenecks.count(),
            "top_bottlenecks": [],
            "avg_bottleneck_score": 0,
            "total_affected_jobs": 0,
        }

        if bottlenecks.exists():
            summary["avg_bottleneck_score"] = round(
                bottlenecks.aggregate(avg_score=models.Avg("bottleneck_score"))["avg_score"] or 0, 2
            )
            summary["total_affected_jobs"] = bottlenecks.aggregate(
                total_jobs=models.Sum("affected_jobs")
            )["total_jobs"] or 0

            # Get top 5 bottlenecks
            top_5 = bottlenecks[:5]
            for bn in top_5:
                summary["top_bottlenecks"].append(
                    {
                        "mc_cd": bn.mc_cd,
                        "bottleneck_score": bn.bottleneck_score,
                        "utilization_rate": bn.utilization_rate,
                        "queue_length": bn.queue_length,
                        "affected_jobs": bn.affected_jobs,
                    }
                )

        return Response(summary)
