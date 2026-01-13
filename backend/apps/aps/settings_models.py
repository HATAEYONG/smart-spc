from django.db import models
from django.utils import timezone


class UserSettings(models.Model):
    """
    User preferences and settings
    """
    setting_id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=100, unique=True, db_index=True)
    username = models.CharField(max_length=200, blank=True)

    # UI Preferences
    theme = models.CharField(
        max_length=20,
        choices=[
            ("LIGHT", "Light"),
            ("DARK", "Dark"),
            ("AUTO", "Auto"),
        ],
        default="LIGHT"
    )
    language = models.CharField(
        max_length=10,
        choices=[
            ("ko", "Korean"),
            ("en", "English"),
            ("ja", "Japanese"),
            ("zh", "Chinese"),
        ],
        default="ko"
    )
    user_timezone = models.CharField(max_length=50, default="Asia/Seoul")

    # Dashboard Preferences
    default_dashboard = models.CharField(max_length=50, default="enhanced")
    dashboard_refresh_interval = models.IntegerField(default=30)  # seconds
    show_kpi_cards = models.BooleanField(default=True)
    kpi_card_order = models.JSONField(default=list, blank=True)

    # Gantt Chart Preferences
    gantt_view_mode = models.CharField(
        max_length=20,
        choices=[
            ("DAY", "Day View"),
            ("WEEK", "Week View"),
            ("MONTH", "Month View"),
        ],
        default="WEEK"
    )
    gantt_show_dependencies = models.BooleanField(default=True)
    gantt_color_scheme = models.CharField(max_length=50, default="status")

    # Notification Preferences
    enable_notifications = models.BooleanField(default=True)
    notification_sound = models.BooleanField(default=True)
    alert_threshold_critical = models.IntegerField(default=1)
    alert_threshold_warning = models.IntegerField(default=3)
    email_notifications = models.BooleanField(default=False)
    email_address = models.EmailField(blank=True)

    # Algorithm Preferences
    default_algorithm = models.CharField(
        max_length=50,
        choices=[
            ("GA", "Genetic Algorithm"),
            ("FIFO", "First In First Out"),
            ("SPT", "Shortest Processing Time"),
            ("EDD", "Earliest Due Date"),
        ],
        default="GA"
    )
    ga_population_size = models.IntegerField(default=50)
    ga_generations = models.IntegerField(default=100)
    ga_mutation_rate = models.FloatField(default=0.1)

    # Display Preferences
    items_per_page = models.IntegerField(default=20)
    date_format = models.CharField(max_length=50, default="YYYY-MM-DD")
    time_format = models.CharField(
        max_length=10,
        choices=[
            ("24H", "24 Hour"),
            ("12H", "12 Hour"),
        ],
        default="24H"
    )
    number_format = models.CharField(max_length=20, default="1,234.56")

    # Advanced Settings
    advanced_features_enabled = models.BooleanField(default=False)
    developer_mode = models.BooleanField(default=False)
    auto_save = models.BooleanField(default=True)
    auto_save_interval = models.IntegerField(default=300)  # seconds

    # Custom Settings
    custom_settings = models.JSONField(default=dict, blank=True)

    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "aps_user_settings"
        ordering = ["user_id"]


class Preset(models.Model):
    """
    Saved configuration presets for algorithms and scheduling
    """
    preset_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Preset type
    PRESET_TYPES = [
        ("ALGORITHM", "Algorithm Configuration"),
        ("SCHEDULE", "Schedule Configuration"),
        ("FILTER", "Filter Preset"),
        ("VIEW", "View Preset"),
        ("DASHBOARD", "Dashboard Layout"),
    ]
    preset_type = models.CharField(max_length=50, choices=PRESET_TYPES)

    # Configuration
    configuration = models.JSONField(default=dict)

    # Access control
    is_public = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)
    owner = models.CharField(max_length=100, blank=True)

    # Usage statistics
    usage_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)

    # Favorite
    is_favorite = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "aps_preset"
        ordering = ["-is_favorite", "-last_used", "-created_at"]
        indexes = [
            models.Index(fields=["preset_type", "owner"]),
            models.Index(fields=["is_public", "preset_type"]),
        ]


class UserActivity(models.Model):
    """
    Track user activity and usage patterns
    """
    activity_id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=100, db_index=True)

    # Activity details
    ACTIVITY_TYPES = [
        ("LOGIN", "User Login"),
        ("LOGOUT", "User Logout"),
        ("VIEW_PAGE", "Page View"),
        ("CREATE", "Create Item"),
        ("UPDATE", "Update Item"),
        ("DELETE", "Delete Item"),
        ("EXPORT", "Export Data"),
        ("GENERATE_REPORT", "Generate Report"),
        ("RUN_ALGORITHM", "Run Algorithm"),
        ("SAVE_PRESET", "Save Preset"),
    ]
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)

    # Context
    page = models.CharField(max_length=100, blank=True)
    action = models.CharField(max_length=100, blank=True)
    details = models.JSONField(default=dict, blank=True)

    # Performance
    duration_ms = models.IntegerField(null=True, blank=True)  # milliseconds
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    # Metadata
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        db_table = "aps_user_activity"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user_id", "-timestamp"]),
            models.Index(fields=["activity_type", "-timestamp"]),
        ]


class SystemConfiguration(models.Model):
    """
    Global system configuration
    """
    config_id = models.AutoField(primary_key=True)
    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.TextField()
    value_type = models.CharField(
        max_length=20,
        choices=[
            ("STRING", "String"),
            ("INTEGER", "Integer"),
            ("FLOAT", "Float"),
            ("BOOLEAN", "Boolean"),
            ("JSON", "JSON"),
        ],
        default="STRING"
    )

    # Metadata
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True)
    is_editable = models.BooleanField(default=True)
    requires_restart = models.BooleanField(default=False)

    # Audit
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "aps_system_configuration"
        ordering = ["category", "key"]
