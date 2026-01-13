"""
SPC Signals
모델 변경 시 WebSocket 알림 전송
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import QualityAlert, QualityMeasurement, ProcessCapability, RunRuleViolation
from .services.websocket_notifier import WebSocketNotifier


@receiver(post_save, sender=QualityAlert)
def alert_created(sender, instance, created, **kwargs):
    """품질 경고 생성 시 알림"""
    if created:
        WebSocketNotifier.notify_alert(instance)


@receiver(post_save, sender=QualityAlert)
def alert_updated(sender, instance, created, **kwargs):
    """품질 경고 상태 변경 시 알림"""
    if not created:
        # 상태가 변경된 경우에만 알림
        WebSocketNotifier.notify_alert(instance)


@receiver(post_save, sender=QualityMeasurement)
def measurement_created(sender, instance, created, **kwargs):
    """측정 데이터 생성 시 알림"""
    if created:
        # 규격 외 또는 관리한계 외인 경우에만 알림
        if not instance.is_within_spec or not instance.is_within_control:
            WebSocketNotifier.notify_measurement(instance)


@receiver(post_save, sender=ProcessCapability)
def capability_updated(sender, instance, created, **kwargs):
    """공정능력 분석 완료 시 알림"""
    if created or instance.analyzed_at:
        WebSocketNotifier.notify_capability(instance)


@receiver(post_save, sender=RunRuleViolation)
def violation_detected(sender, instance, created, **kwargs):
    """Run Rule 위반 감지 시 알림"""
    if created:
        WebSocketNotifier.notify_run_rule_violation(instance)
