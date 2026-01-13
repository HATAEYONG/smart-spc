"""
SPC WebSocket Routing
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/spc/notifications/$', consumers.SPCNotificationConsumer.as_asgi()),
    re_path(r'ws/spc/product/(?P<product_id>\d+)/$', consumers.ProductDataConsumer.as_asgi()),
]
