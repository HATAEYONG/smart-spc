from django.db import models
from django.utils import timezone


class ProductionStatus(models.Model):
    """
    Real-time production status tracking
    """
    status_id = models.AutoField(primary_key=True)

    # Machine/Line identification
    mc_cd = models.CharField(max_length=50, db_index=True)
    mc_nm = models.CharField(max_length=200, blank=True)

    # Current status
    STATUS_CHOICES = [
        ("IDLE", "Idle"),
        ("RUNNING", "Running"),
        ("SETUP", "Setup"),
        ("MAINTENANCE", "Maintenance"),
        ("BREAKDOWN", "Breakdown"),
        ("WAITING", "Waiting for Material"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="IDLE")

    # Current job
    current_wo_no = models.CharField(max_length=100, blank=True)
    current_item_cd = models.CharField(max_length=100, blank=True)

    # Progress
    planned_quantity = models.IntegerField(default=0)
    completed_quantity = models.IntegerField(default=0)
    defect_quantity = models.IntegerField(default=0)
    progress_percentage = models.FloatField(default=0.0)  # 0-100

    # Timing
    job_start_time = models.DateTimeField(null=True, blank=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)

    # Performance metrics
    current_cycle_time = models.FloatField(default=0.0)  # seconds
    average_cycle_time = models.FloatField(default=0.0)  # seconds
    utilization_rate = models.FloatField(default=0.0)  # 0-100
    oee = models.FloatField(default=0.0)  # Overall Equipment Effectiveness 0-100

    # Alerts
    has_alert = models.BooleanField(default=False)
    alert_type = models.CharField(max_length=50, blank=True)
    alert_message = models.TextField(blank=True)

    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "aps_production_status"
        ordering = ["mc_cd"]
        indexes = [
            models.Index(fields=["mc_cd", "status"]),
            models.Index(fields=["last_updated"]),
        ]


class MachineMetrics(models.Model):
    """
    Time-series machine performance metrics
    """
    metric_id = models.AutoField(primary_key=True)
    mc_cd = models.CharField(max_length=50, db_index=True)

    # Time bucket
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    bucket_type = models.CharField(
        max_length=20,
        choices=[
            ("MINUTE", "Minute"),
            ("HOUR", "Hour"),
            ("DAY", "Day"),
        ],
        default="HOUR"
    )

    # Production metrics
    output_quantity = models.IntegerField(default=0)
    defect_quantity = models.IntegerField(default=0)
    yield_rate = models.FloatField(default=100.0)  # percentage

    # Time metrics
    runtime_minutes = models.FloatField(default=0.0)
    downtime_minutes = models.FloatField(default=0.0)
    setup_time_minutes = models.FloatField(default=0.0)
    utilization_rate = models.FloatField(default=0.0)

    # Quality metrics
    avg_cycle_time = models.FloatField(default=0.0)
    target_cycle_time = models.FloatField(default=0.0)
    performance_rate = models.FloatField(default=100.0)

    # OEE components
    availability = models.FloatField(default=100.0)
    performance = models.FloatField(default=100.0)
    quality = models.FloatField(default=100.0)
    oee = models.FloatField(default=100.0)

    # Aggregation metadata
    aggregated_from_count = models.IntegerField(default=0)

    class Meta:
        db_table = "aps_machine_metrics"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["mc_cd", "-timestamp"]),
            models.Index(fields=["bucket_type", "-timestamp"]),
        ]
        unique_together = [["mc_cd", "timestamp", "bucket_type"]]


class Alert(models.Model):
    """
    System alerts and notifications
    """
    alert_id = models.AutoField(primary_key=True)

    # Alert classification
    SEVERITY_CHOICES = [
        ("INFO", "Information"),
        ("WARNING", "Warning"),
        ("ERROR", "Error"),
        ("CRITICAL", "Critical"),
    ]
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default="INFO")

    CATEGORY_CHOICES = [
        ("PRODUCTION", "Production Issue"),
        ("QUALITY", "Quality Issue"),
        ("SCHEDULE", "Schedule Deviation"),
        ("MACHINE", "Machine Issue"),
        ("MATERIAL", "Material Issue"),
        ("CONSTRAINT", "Constraint Violation"),
        ("SYSTEM", "System Issue"),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="SYSTEM")

    # Alert details
    title = models.CharField(max_length=200)
    message = models.TextField()

    # Related entities
    mc_cd = models.CharField(max_length=50, blank=True, db_index=True)
    wo_no = models.CharField(max_length=100, blank=True)
    related_data = models.JSONField(default=dict, blank=True)

    # Alert state
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("ACKNOWLEDGED", "Acknowledged"),
        ("RESOLVED", "Resolved"),
        ("DISMISSED", "Dismissed"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")

    # Actions
    recommended_action = models.TextField(blank=True)
    action_taken = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Users
    created_by = models.CharField(max_length=100, blank=True)
    acknowledged_by = models.CharField(max_length=100, blank=True)
    resolved_by = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "aps_alert"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["severity", "status"]),
            models.Index(fields=["category", "-created_at"]),
            models.Index(fields=["mc_cd", "-created_at"]),
        ]


class KPISnapshot(models.Model):
    """
    Periodic snapshots of key performance indicators
    """
    snapshot_id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    # Production KPIs
    total_output = models.IntegerField(default=0)
    total_planned = models.IntegerField(default=0)
    plan_achievement_rate = models.FloatField(default=0.0)  # percentage

    # Quality KPIs
    total_defects = models.IntegerField(default=0)
    overall_yield_rate = models.FloatField(default=100.0)
    first_pass_yield = models.FloatField(default=100.0)

    # Efficiency KPIs
    avg_utilization = models.FloatField(default=0.0)
    avg_oee = models.FloatField(default=0.0)
    machines_running = models.IntegerField(default=0)
    machines_idle = models.IntegerField(default=0)
    machines_down = models.IntegerField(default=0)

    # Schedule KPIs
    jobs_completed = models.IntegerField(default=0)
    jobs_in_progress = models.IntegerField(default=0)
    jobs_delayed = models.IntegerField(default=0)
    on_time_delivery_rate = models.FloatField(default=100.0)

    # Alert summary
    active_alerts = models.IntegerField(default=0)
    critical_alerts = models.IntegerField(default=0)

    # Metadata
    snapshot_type = models.CharField(
        max_length=20,
        choices=[
            ("REALTIME", "Real-time"),
            ("HOURLY", "Hourly"),
            ("DAILY", "Daily"),
        ],
        default="REALTIME"
    )

    class Meta:
        db_table = "aps_kpi_snapshot"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["snapshot_type", "-timestamp"]),
        ]
