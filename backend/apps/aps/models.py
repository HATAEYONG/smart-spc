from django.db import models
from django.utils import timezone


class BottleneckAnalysis(models.Model):
    """
    Store bottleneck analysis results for machines
    """
    analysis_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    mc_cd = models.CharField(max_length=20, db_index=True)

    # Utilization metrics
    utilization_rate = models.FloatField()  # 0-100%
    queue_length = models.IntegerField(default=0)
    avg_waiting_time = models.FloatField(default=0)  # minutes

    # Bottleneck severity
    bottleneck_score = models.FloatField(default=0)  # 0-100 (higher = worse bottleneck)
    is_bottleneck = models.BooleanField(default=False)

    # Impact analysis
    affected_jobs = models.IntegerField(default=0)
    total_delay = models.FloatField(default=0)  # minutes

    # Recommendations (JSON array)
    recommendations = models.JSONField(null=True, blank=True)

    # Time window for analysis
    analysis_start = models.DateTimeField()
    analysis_end = models.DateTimeField()

    class Meta:
        db_table = "bottleneck_analysis"
        ordering = ["-created_at", "-bottleneck_score"]
        indexes = [
            models.Index(fields=["mc_cd", "created_at"], name="ix_bottleneck_mc_ts"),
            models.Index(fields=["is_bottleneck"], name="ix_bottleneck_flag"),
        ]

    def __str__(self):
        return f"{self.mc_cd} - {self.bottleneck_score:.1f} at {self.created_at}"


class MachineLoadHistory(models.Model):
    """
    Track machine load over time for trend analysis
    """
    history_id = models.AutoField(primary_key=True)
    mc_cd = models.CharField(max_length=20, db_index=True)
    timestamp = models.DateTimeField(db_index=True)

    # Load metrics
    active_jobs = models.IntegerField(default=0)
    queued_jobs = models.IntegerField(default=0)
    utilization_rate = models.FloatField(default=0)  # 0-100%

    # Capacity
    total_capacity = models.FloatField(default=0)  # minutes
    used_capacity = models.FloatField(default=0)  # minutes
    available_capacity = models.FloatField(default=0)  # minutes

    class Meta:
        db_table = "machine_load_history"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["mc_cd", "timestamp"], name="ix_load_mc_ts"),
        ]

    def __str__(self):
        return f"{self.mc_cd} at {self.timestamp} - {self.utilization_rate:.1f}%"


class AlgorithmComparison(models.Model):
    """
    Store algorithm comparison results
    """
    comparison_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    job_count = models.IntegerField()
    machine_count = models.IntegerField()

    # Genetic Algorithm results
    ga_makespan = models.FloatField(null=True, blank=True)
    ga_tardiness = models.FloatField(null=True, blank=True)
    ga_cost = models.FloatField(null=True, blank=True)
    ga_runtime = models.FloatField(null=True, blank=True)  # seconds

    # Dispatch Rule results (JSON for all rules)
    dispatch_results = models.JSONField(null=True, blank=True)

    # Best rule
    best_rule = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = "algorithm_comparison"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comparison {self.comparison_id} - {self.job_count} jobs"


# ============================================================================
# STEP 2: Execution Data Models (DOWN_RISK 예측 기반)
# ============================================================================
from .execution_models import OperationActual, ExecutionEvent

# ============================================================================
# STEP 3: Analytics Models (미계획 원인 분석)
# ============================================================================
from .analytics_models import UnplannedReason
