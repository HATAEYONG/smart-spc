from django.db import models
from django.utils import timezone


class Report(models.Model):
    """
    Report definitions and generation history
    """
    report_id = models.AutoField(primary_key=True)

    # Report metadata
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Report type
    REPORT_TYPES = [
        ("PRODUCTION_SUMMARY", "Production Summary"),
        ("PERFORMANCE_ANALYSIS", "Performance Analysis"),
        ("QUALITY_REPORT", "Quality Report"),
        ("SCHEDULE_ADHERENCE", "Schedule Adherence"),
        ("BOTTLENECK_ANALYSIS", "Bottleneck Analysis"),
        ("OEE_REPORT", "OEE Report"),
        ("MACHINE_UTILIZATION", "Machine Utilization"),
        ("ALERT_SUMMARY", "Alert Summary"),
        ("CUSTOM", "Custom Report"),
    ]
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES, default="PRODUCTION_SUMMARY")

    # Time period
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    # Filters
    filters = models.JSONField(default=dict, blank=True)  # machine, item, etc.

    # Report content
    data = models.JSONField(default=dict, blank=True)
    summary = models.JSONField(default=dict, blank=True)
    charts = models.JSONField(default=list, blank=True)

    # Export options
    EXPORT_FORMATS = [
        ("PDF", "PDF Document"),
        ("EXCEL", "Excel Spreadsheet"),
        ("CSV", "CSV File"),
        ("JSON", "JSON Data"),
    ]
    export_format = models.CharField(max_length=20, choices=EXPORT_FORMATS, default="PDF")

    # Status
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("GENERATING", "Generating"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    # File reference
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.IntegerField(default=0)  # bytes

    # Execution info
    generation_time = models.FloatField(default=0.0)  # seconds
    error_message = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    created_by = models.CharField(max_length=100, blank=True)
    generated_at = models.DateTimeField(null=True, blank=True)

    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(
        max_length=20,
        choices=[
            ("DAILY", "Daily"),
            ("WEEKLY", "Weekly"),
            ("MONTHLY", "Monthly"),
            ("ONCE", "Once"),
        ],
        default="ONCE"
    )
    next_run = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "aps_report"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["report_type", "-created_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["is_scheduled", "next_run"]),
        ]


class ReportTemplate(models.Model):
    """
    Predefined report templates
    """
    template_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Template configuration
    report_type = models.CharField(max_length=50, choices=Report.REPORT_TYPES)
    default_filters = models.JSONField(default=dict, blank=True)
    sections = models.JSONField(default=list, blank=True)  # List of sections to include
    chart_types = models.JSONField(default=list, blank=True)  # Charts to include

    # Display options
    include_charts = models.BooleanField(default=True)
    include_summary = models.BooleanField(default=True)
    include_details = models.BooleanField(default=True)

    # Access control
    is_public = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False)  # System-provided template

    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.CharField(max_length=100, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "aps_report_template"
        ordering = ["name"]


class ExportHistory(models.Model):
    """
    History of data exports
    """
    export_id = models.AutoField(primary_key=True)

    # Export details
    export_type = models.CharField(
        max_length=50,
        choices=[
            ("SCHEDULE", "Schedule Export"),
            ("REPORT", "Report Export"),
            ("DATA", "Raw Data Export"),
            ("BACKUP", "Data Backup"),
        ],
        default="DATA"
    )

    # Related report (optional)
    report = models.ForeignKey(
        Report,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exports"
    )

    # Export content
    data_type = models.CharField(max_length=100)  # e.g., "plans", "performance", etc.
    record_count = models.IntegerField(default=0)

    # File info
    file_format = models.CharField(max_length=20, choices=Report.EXPORT_FORMATS)
    file_path = models.CharField(max_length=500)
    file_size = models.IntegerField(default=0)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("SUCCESS", "Success"),
            ("FAILED", "Failed"),
        ],
        default="SUCCESS"
    )
    error_message = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    created_by = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "aps_export_history"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["export_type", "-created_at"]),
            models.Index(fields=["data_type"]),
        ]
