"""
Extended User Models for SPC System
"""
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Extended user profile for SPC system
    """
    ROLE_CHOICES = [
        ('viewer', 'Viewer'),          # Read-only access
        ('operator', 'Operator'),      # Can input data
        ('quality_engineer', 'Quality Engineer'),  # Full access
        ('admin', 'Admin'),            # All permissions
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='spc_profile',
        verbose_name='User'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='viewer',
        verbose_name='Role'
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Department'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Phone Number'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        db_table = 'spc_user_profile'

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_quality_engineer(self):
        return self.role in ['quality_engineer', 'admin']

    @property
    def is_operator(self):
        return self.role in ['operator', 'quality_engineer', 'admin']


class AuditLog(models.Model):
    """
    Audit log for tracking user actions
    """
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create_product', 'Create Product'),
        ('update_product', 'Update Product'),
        ('delete_product', 'Delete Product'),
        ('create_measurement', 'Create Measurement'),
        ('bulk_create_measurements', 'Bulk Create Measurements'),
        ('resolve_alert', 'Resolve Alert'),
        ('generate_report', 'Generate Report'),
        ('export_data', 'Export Data'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name='User'
    )
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        verbose_name='Action'
    )
    entity_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Entity Type'
    )
    entity_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Entity ID'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP Address'
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )

    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        db_table = 'spc_audit_log'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['entity_type', 'entity_id']),
        ]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.created_at}"


class BlacklistedToken(models.Model):
    """
    Blacklisted tokens for logout functionality
    """
    token = models.TextField(
        unique=True,
        verbose_name='Token'
    )
    jti = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name='JWT ID'
    )
    user_id = models.IntegerField(
        verbose_name='User ID'
    )
    blacklisted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Blacklisted At'
    )
    expires_at = models.DateTimeField(
        verbose_name='Expires At'
    )

    class Meta:
        verbose_name = 'Blacklisted Token'
        verbose_name_plural = 'Blacklisted Tokens'
        db_table = 'spc_blacklisted_token'
        indexes = [
            models.Index(fields=['jti']),
            models.Index(fields=['user_id', '-blacklisted_at']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Token for user {self.user_id} - {self.blacklisted_at}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at
