from django.apps import AppConfig


class SpcConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.spc'
    verbose_name = 'SPC Quality Control'

    def ready(self):
        """앱이 준비될 때 signals 연결"""
        import apps.spc.signals  # noqa
