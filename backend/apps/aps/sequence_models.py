from django.db import models
from django.utils import timezone


class JobSequence(models.Model):
    """
    Represents a specific ordering/sequence of jobs for a machine or production line
    """
    sequence_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Target machine or line
    mc_cd = models.CharField(max_length=50, db_index=True, blank=True)

    # Sequence data: list of job IDs in order
    job_sequence = models.JSONField(default=list)

    # Sequencing rule used
    SEQUENCING_RULES = [
        ("MANUAL", "Manual Order"),
        ("FIFO", "First In First Out"),
        ("LIFO", "Last In First Out"),
        ("SPT", "Shortest Processing Time"),
        ("LPT", "Longest Processing Time"),
        ("EDD", "Earliest Due Date"),
        ("SLACK", "Minimum Slack"),
        ("CR", "Critical Ratio"),
        ("WSPT", "Weighted Shortest Processing Time"),
        ("ATC", "Apparent Tardiness Cost"),
    ]
    sequencing_rule = models.CharField(max_length=50, choices=SEQUENCING_RULES, default="MANUAL")

    # Performance metrics
    estimated_makespan = models.FloatField(null=True, blank=True)
    estimated_tardiness = models.FloatField(null=True, blank=True)
    estimated_flowtime = models.FloatField(null=True, blank=True)

    # Status
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("ACTIVE", "Active"),
        ("ARCHIVED", "Archived"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")

    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "aps_job_sequence"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["mc_cd", "status"]),
            models.Index(fields=["created_at"]),
        ]


class SequenceOptimization(models.Model):
    """
    Records of sequence optimization runs
    """
    optimization_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Input parameters
    mc_cd = models.CharField(max_length=50, db_index=True, blank=True)
    job_ids = models.JSONField(default=list)

    # Optimization objective
    OBJECTIVES = [
        ("MAKESPAN", "Minimize Makespan"),
        ("TARDINESS", "Minimize Total Tardiness"),
        ("FLOWTIME", "Minimize Total Flow Time"),
        ("WEIGHTED_TARDINESS", "Minimize Weighted Tardiness"),
        ("MULTI_OBJECTIVE", "Multi-Objective"),
    ]
    objective = models.CharField(max_length=50, choices=OBJECTIVES, default="MAKESPAN")

    # Results: list of {rule, sequence, metrics}
    results = models.JSONField(default=list)

    # Best sequence found
    best_sequence = models.ForeignKey(
        JobSequence,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="optimizations"
    )

    # Execution time
    execution_time = models.FloatField(default=0.0)  # seconds

    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "aps_sequence_optimization"
        ordering = ["-created_at"]


class SequenceComparison(models.Model):
    """
    Compare multiple job sequences side by side
    """
    comparison_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Sequences being compared
    sequences = models.ManyToManyField(JobSequence, related_name="comparisons")

    # Comparison metrics
    comparison_data = models.JSONField(default=dict)

    # Recommended sequence
    recommended_sequence = models.ForeignKey(
        JobSequence,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recommended_comparisons"
    )

    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "aps_sequence_comparison"
        ordering = ["-created_at"]
