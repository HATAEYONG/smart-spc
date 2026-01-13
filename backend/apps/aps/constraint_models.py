from django.db import models
from django.utils import timezone


class Constraint(models.Model):
    """
    Constraint definition for production scheduling
    """
    CONSTRAINT_TYPES = [
        ("MACHINE_AVAILABILITY", "Machine Availability"),  # 기계 가용성
        ("PRECEDENCE", "Precedence"),  # 선행 관계
        ("SETUP_TIME", "Setup Time"),  # 준비 시간
        ("SKILL_REQUIREMENT", "Skill Requirement"),  # 기술 요구사항
        ("MATERIAL_AVAILABILITY", "Material Availability"),  # 자재 가용성
        ("CAPACITY_LIMIT", "Capacity Limit"),  # 용량 제한
        ("TIME_WINDOW", "Time Window"),  # 시간 창
        ("BATCH_SIZE", "Batch Size"),  # 배치 크기
        ("RESOURCE_CONFLICT", "Resource Conflict"),  # 자원 충돌
        ("CUSTOM", "Custom"),  # 사용자 정의
    ]

    PRIORITY_LEVELS = [
        ("CRITICAL", "Critical"),  # 필수
        ("HIGH", "High"),  # 높음
        ("MEDIUM", "Medium"),  # 중간
        ("LOW", "Low"),  # 낮음
    ]

    constraint_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    constraint_type = models.CharField(max_length=50, choices=CONSTRAINT_TYPES)

    # Priority
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default="MEDIUM")

    # Active status
    is_active = models.BooleanField(default=True)

    # Constraint parameters (JSON)
    # Examples:
    # - Machine availability: {"machine": "MC001", "start": "2024-01-01T08:00", "end": "2024-01-01T17:00"}
    # - Precedence: {"job_a": "WO001", "job_b": "WO002", "min_lag": 60}
    # - Setup time: {"from_item": "ITM001", "to_item": "ITM002", "time": 30}
    parameters = models.JSONField(default=dict)

    # Affected entities
    machines = models.JSONField(null=True, blank=True)  # List of machine codes
    jobs = models.JSONField(null=True, blank=True)  # List of job/work order numbers
    items = models.JSONField(null=True, blank=True)  # List of item IDs

    # Violation handling
    allow_violation = models.BooleanField(default=False)
    violation_penalty = models.FloatField(default=1000.0)  # Penalty cost for violation

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "constraint"
        ordering = ["-priority", "-created_at"]
        indexes = [
            models.Index(fields=["constraint_type", "is_active"], name="ix_constraint_type_active"),
            models.Index(fields=["priority"], name="ix_constraint_priority"),
        ]

    def __str__(self):
        return f"{self.name} ({self.constraint_type})"


class ConstraintViolation(models.Model):
    """
    Track constraint violations during scheduling
    """
    VIOLATION_SEVERITIES = [
        ("CRITICAL", "Critical"),
        ("WARNING", "Warning"),
        ("INFO", "Info"),
    ]

    violation_id = models.AutoField(primary_key=True)
    constraint = models.ForeignKey(Constraint, on_delete=models.CASCADE, related_name="violations")

    # Violation details
    severity = models.CharField(max_length=20, choices=VIOLATION_SEVERITIES)
    description = models.TextField()

    # Affected entities
    job = models.CharField(max_length=30, null=True, blank=True)
    machine = models.CharField(max_length=20, null=True, blank=True)

    # Violation metrics
    violation_amount = models.FloatField(default=0)  # e.g., minutes over time window
    penalty_cost = models.FloatField(default=0)

    # Resolution
    is_resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(null=True, blank=True)

    # Metadata
    detected_at = models.DateTimeField(auto_now_add=True, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "constraint_violation"
        ordering = ["-detected_at"]
        indexes = [
            models.Index(fields=["severity", "is_resolved"], name="ix_violation_severity"),
        ]

    def __str__(self):
        return f"Violation of {self.constraint.name} - {self.severity}"


class ConstraintGroup(models.Model):
    """
    Group related constraints together
    """
    group_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    # Constraints in this group
    constraints = models.ManyToManyField(Constraint, related_name="groups")

    # Group settings
    is_active = models.BooleanField(default=True)
    apply_all = models.BooleanField(default=True)  # Apply all constraints or any

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "constraint_group"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ConstraintTemplate(models.Model):
    """
    Predefined constraint templates
    """
    template_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    constraint_type = models.CharField(max_length=50)

    # Template parameters
    template_parameters = models.JSONField(default=dict)

    # Usage count
    usage_count = models.IntegerField(default=0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    is_system = models.BooleanField(default=False)  # System template or user-created

    class Meta:
        db_table = "constraint_template"
        ordering = ["-usage_count", "name"]

    def __str__(self):
        return f"{self.name} Template"
