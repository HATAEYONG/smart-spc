"""
SPC WebSocket Consumers
실시간 품질 알림 및 데이터 업데이트
"""
import json
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import Q

from .models import QualityAlert, QualityMeasurement, Product


class SPCNotificationConsumer(AsyncWebsocketConsumer):
    """SPC 실시간 알림 Consumer"""

    async def connect(self):
        """WebSocket 연결"""
        self.user_id = self.scope["user"].id if self.scope.get("user") else "anonymous"
        self.group_name = f"spc_notifications_{self.user_id}"

        # 그룹에 참여
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # 연결 환영 메시지
        await self.send(text_data=json.dumps({
            "type": "connection",
            "message": "SPC 실시간 알림에 연결되었습니다",
            "timestamp": datetime.now().isoformat()
        }))

    async def disconnect(self, close_code):
        """WebSocket 연결 해제"""
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """클라이언트로부터 메시지 수신"""
        try:
            data = json.loads(text_data)
            message_type = data.get("type")

            if message_type == "subscribe_product":
                # 특정 제품의 알림 구독
                product_id = data.get("product_id")
                if product_id:
                    product_group = f"spc_product_{product_id}"
                    await self.channel_layer.group_add(product_group, self.channel_name)
                    await self.send(text_data=json.dumps({
                        "type": "subscription",
                        "message": f"제품 {product_id}의 알림을 구독합니다",
                        "product_id": product_id
                    }))

            elif message_type == "unsubscribe_product":
                # 특정 제품의 알림 구독 해지
                product_id = data.get("product_id")
                if product_id:
                    product_group = f"spc_product_{product_id}"
                    await self.channel_layer.group_discard(product_group, self.channel_name)
                    await self.send(text_data=json.dumps({
                        "type": "unsubscription",
                        "message": f"제품 {product_id}의 알림 구독을 해지합니다",
                        "product_id": product_id
                    }))

            elif message_type == "get_alerts":
                # 최근 알림 조회
                alerts = await self.get_recent_alerts(data.get("limit", 10))
                await self.send(text_data=json.dumps({
                    "type": "alerts",
                    "alerts": alerts
                }))

        except Exception as e:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": str(e)
            }))

    async def spc_alert(self, event):
        """품질 경고 알림"""
        await self.send(text_data=json.dumps({
            "type": "alert",
            "alert": event["alert"],
            "timestamp": event["timestamp"]
        }))

    async def measurement_update(self, event):
        """측정 데이터 업데이트 알림"""
        await self.send(text_data=json.dumps({
            "type": "measurement",
            "measurement": event["measurement"],
            "timestamp": event["timestamp"]
        }))

    async def capability_update(self, event):
        """공정능력 업데이트 알림"""
        await self.send(text_data=json.dumps({
            "type": "capability",
            "capability": event["capability"],
            "timestamp": event["timestamp"]
        }))

    @database_sync_to_async
    def get_recent_alerts(self, limit=10):
        """최근 경고 조회"""
        alerts = QualityAlert.objects.select_related('product').order_by('-created_at')[:limit]
        return [
            {
                "id": alert.id,
                "product_code": alert.product.product_code,
                "alert_type": alert.alert_type,
                "priority": alert.priority,
                "message": alert.message,
                "status": alert.status,
                "created_at": alert.created_at.isoformat()
            }
            for alert in alerts
        ]


class ProductDataConsumer(AsyncWebsocketConsumer):
    """특정 제품의 실시간 데이터 Consumer"""

    async def connect(self):
        """WebSocket 연결"""
        self.product_id = self.scope["url_route"]["kwargs"]["product_id"]
        self.product_group = f"spc_product_{self.product_id}"

        # 제품 그룹에 참여
        await self.channel_layer.group_add(self.product_group, self.channel_name)
        await self.accept()

        # 연결 시 제품 정보 전송
        product = await self.get_product_info(self.product_id)
        if product:
            await self.send(text_data=json.dumps({
                "type": "connection",
                "message": f"제품 {product['product_code']}의 실시간 데이터에 연결되었습니다",
                "product": product
            }))

    async def disconnect(self, close_code):
        """WebSocket 연결 해제"""
        await self.channel_layer.group_discard(self.product_group, self.channel_name)

    async def receive(self, text_data):
        """클라이언트로부터 메시지 수신"""
        try:
            data = json.loads(text_data)
            message_type = data.get("type")

            if message_type == "get_latest_data":
                # 최근 측정 데이터 조회
                measurements = await self.get_latest_measurements(self.product_id, data.get("limit", 20))
                await self.send(text_data=json.dumps({
                    "type": "measurements",
                    "product_id": self.product_id,
                    "measurements": measurements
                }))

        except Exception as e:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": str(e)
            }))

    @database_sync_to_async
    def get_product_info(self, product_id):
        """제품 정보 조회"""
        try:
            product = Product.objects.get(id=product_id)
            return {
                "id": product.id,
                "product_code": product.product_code,
                "product_name": product.product_name,
                "usl": product.usl,
                "lsl": product.lsl,
                "target_value": product.target_value,
                "unit": product.unit
            }
        except Product.DoesNotExist:
            return None

    @database_sync_to_async
    def get_latest_measurements(self, product_id, limit=20):
        """최근 측정 데이터 조회"""
        measurements = QualityMeasurement.objects.filter(
            product_id=product_id
        ).order_by('-measured_at')[:limit]

        return [
            {
                "id": m.id,
                "measurement_value": m.measurement_value,
                "sample_number": m.sample_number,
                "subgroup_number": m.subgroup_number,
                "is_within_spec": m.is_within_spec,
                "is_within_control": m.is_within_control,
                "measured_at": m.measured_at.isoformat()
            }
            for m in measurements
        ]
