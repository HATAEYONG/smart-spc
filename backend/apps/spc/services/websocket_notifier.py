"""
SPC WebSocket 알림 서비스
품질 이벤트 발생 시 WebSocket으로 실시간 알림 전송
"""
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from datetime import datetime
import json

channel_layer = get_channel_layer()


class WebSocketNotifier:
    """WebSocket 알림 서비스"""

    @staticmethod
    def notify_alert(alert):
        """품질 경고 알림 전송"""
        try:
            alert_data = {
                "id": alert.id,
                "product_code": alert.product.product_code,
                "product_name": alert.product.product_name,
                "alert_type": alert.alert_type,
                "priority": alert.priority,
                "title": alert.title,
                "message": alert.message,
                "status": alert.status,
                "created_at": alert.created_at.isoformat(),
            }

            # 전체 알림 그룹에 전송
            async_to_sync(channel_layer.group_send)(
                "spc_notifications_anonymous",  # 개발용 anonymous 그룹
                {
                    "type": "spc_alert",
                    "alert": alert_data,
                    "timestamp": datetime.now().isoformat()
                }
            )

            # 제품별 그룹에도 전송
            product_group = f"spc_product_{alert.product_id}"
            async_to_sync(channel_layer.group_send)(
                product_group,
                {
                    "type": "spc_alert",
                    "alert": alert_data,
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            print(f"WebSocket 알림 전송 실패: {e}")

    @staticmethod
    def notify_measurement(measurement):
        """측정 데이터 업데이트 알림"""
        try:
            measurement_data = {
                "id": measurement.id,
                "product_id": measurement.product_id,
                "product_code": measurement.product.product_code,
                "measurement_value": measurement.measurement_value,
                "sample_number": measurement.sample_number,
                "subgroup_number": measurement.subgroup_number,
                "is_within_spec": measurement.is_within_spec,
                "is_within_control": measurement.is_within_control,
                "measured_at": measurement.measured_at.isoformat(),
            }

            # 제품별 그룹에 전송
            product_group = f"spc_product_{measurement.product_id}"
            async_to_sync(channel_layer.group_send)(
                product_group,
                {
                    "type": "measurement_update",
                    "measurement": measurement_data,
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            print(f"WebSocket 측정 데이터 알림 전송 실패: {e}")

    @staticmethod
    def notify_capability(capability):
        """공정능력 업데이트 알림"""
        try:
            capability_data = {
                "id": capability.id,
                "product_id": capability.product_id,
                "product_code": capability.product.product_code,
                "cp": capability.cp,
                "cpk": capability.cpk,
                "pp": capability.pp,
                "ppk": capability.ppk,
                "analyzed_at": capability.analyzed_at.isoformat(),
            }

            # 제품별 그룹에 전송
            product_group = f"spc_product_{capability.product_id}"
            async_to_sync(channel_layer.group_send)(
                product_group,
                {
                    "type": "capability_update",
                    "capability": capability_data,
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            print(f"WebSocket 공정능력 알림 전송 실패: {e}")

    @staticmethod
    def notify_run_rule_violation(violation):
        """Run Rule 위반 알림"""
        try:
            violation_data = {
                "id": violation.id,
                "rule_type": violation.rule_type,
                "detected_at": violation.detected_at.isoformat(),
                "is_resolved": violation.is_resolved,
            }

            # 제품별 그룹에 전송
            product_group = f"spc_product_{violation.control_chart.product_id}"
            async_to_sync(channel_layer.group_send)(
                product_group,
                {
                    "type": "run_rule_violation",
                    "violation": violation_data,
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            print(f"WebSocket Run Rule 알림 전송 실패: {e}")


class AlertBroadcaster:
    """품질 경고 방송 서비스"""

    @staticmethod
    def broadcast_new_alert(alert):
        """새로운 경고를 모든 연결된 클라이언트에게 방송"""
        WebSocketNotifier.notify_alert(alert)

    @staticmethod
    def broadcast_measurement(measurement):
        """새로운 측정 데이터를 방송"""
        WebSocketNotifier.notify_measurement(measurement)

    @staticmethod
    def broadcast_capability_update(capability):
        """공정능력 업데이트를 방송"""
        WebSocketNotifier.notify_capability(capability)
