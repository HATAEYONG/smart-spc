from django.db import models
from django.utils import timezone


class Scenario(models.Model):
    """
    What-If scenario model for testing different planning configurations
    """
    SCENARIO_STATUS = [
        ("DRAFT", "DRAFT"),
        ("RUNNING", "RUNNING"),
        ("COMPLETED", "COMPLETED"),
        ("FAILED", "FAILED"),
    ]

    scenario_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    # Scenario configuration
    base_plan_date = models.DateTimeField(null=True, blank=True)

    # Modifications (JSON)
    # Examples:
    # - Add new jobs: {"type": "add_jobs", "jobs": [...]}
    # - Remove machines: {"type": "remove_machines", "machines": ["MC001"]}
    # - Change capacity: {"type": "change_capacity", "machine": "MC001", "factor": 1.5}
    # - Add breakdown: {"type": "add_breakdown", "machine": "MC001", "start": "...", "duration": 120}
    modifications = models.JSONField(default=list, blank=True)

    # Scheduling parameters
    algorithm = models.CharField(max_length=50, default="GA")  # GA, FIFO, SPT, EDD, etc.
    algorithm_params = models.JSONField(null=True, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=SCENARIO_STATUS, default="DRAFT")

    # Results (JSON)
    results = models.JSONField(null=True, blank=True)

    # Comparison with baseline
    baseline_scenario = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="variants"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        app_label = 'aps'
        db_table = "scenario"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"], name="ix_scenario_status_ts"),
        ]

    def __str__(self):
        return f"{self.name} ({self.status})"


class ScenarioResult(models.Model):
    """
    Detailed results for a scenario execution
    """
    result_id = models.AutoField(primary_key=True)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="detailed_results")

    # Performance metrics
    makespan = models.FloatField(default=0)
    total_tardiness = models.FloatField(default=0)
    max_tardiness = models.FloatField(default=0)
    avg_utilization = models.FloatField(default=0)
    total_cost = models.FloatField(default=0)

    # Job statistics
    total_jobs = models.IntegerField(default=0)
    completed_jobs = models.IntegerField(default=0)
    tardy_jobs = models.IntegerField(default=0)

    # Machine statistics
    total_machines = models.IntegerField(default=0)
    avg_machine_utilization = models.FloatField(default=0)
    bottleneck_machines = models.JSONField(null=True, blank=True)

    # Detailed schedule (JSON)
    schedule = models.JSONField(null=True, blank=True)

    # Execution metadata
    execution_time = models.FloatField(default=0)  # seconds
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'aps'
        db_table = "scenario_result"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Result for {self.scenario.name} - Makespan: {self.makespan:.1f}"


class ScenarioComparison(models.Model):
    """
    Compare multiple scenarios side-by-side
    """
    comparison_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    # Scenarios being compared
    scenarios = models.ManyToManyField(Scenario, related_name="comparisons")

    # Comparison metrics
    comparison_data = models.JSONField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        app_label = 'aps'
        db_table = "scenario_comparison"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comparison: {self.name}"
