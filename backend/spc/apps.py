"""
SPC App Configuration
"""
from django.apps import AppConfig


class SpcConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'spc'
    verbose_name = 'SPC'
