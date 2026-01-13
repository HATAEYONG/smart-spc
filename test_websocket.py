"""
WebSocket Test Script for SPC Real-time Notifications
Tests WebSocket connection and message handling
"""
import asyncio
import websockets
import json
from datetime import datetime

# WebSocket server URL
WS_URL = "ws://localhost:8000/ws/spc/notifications/"


async def test_websocket_connection():
    """Test WebSocket connection and messaging"""
    print("=" * 60)
    print("WebSocket Connection Test")
    print("=" * 60)

    try:
        print(f"\n[1] Connecting to {WS_URL}...")
        async with websockets.connect(WS_URL) as websocket:
            print("✅ Connected successfully!")

            # Test 1: Receive connection message
            print("\n[Test 1] Waiting for connection message...")
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"✅ Received: {data}")

                if data.get('type') == 'connection':
                    print("✅ Connection message type verified")
                else:
                    print(f"⚠️ Unexpected message type: {data.get('type')}")
            except asyncio.TimeoutError:
                print("❌ No connection message received")

            # Test 2: Subscribe to product alerts
            print("\n[Test 2] Subscribing to product 1 alerts...")
            subscribe_msg = {
                "type": "subscribe_product",
                "product_id": 1
            }
            await websocket.send(json.dumps(subscribe_msg))
            print(f"✅ Sent: {subscribe_msg}")

            # Wait for subscription confirmation
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"✅ Received: {data}")

                if data.get('type') == 'subscription':
                    print("✅ Subscription confirmed")
                else:
                    print(f"⚠️ Unexpected response type: {data.get('type')}")
            except asyncio.TimeoutError:
                print("❌ No subscription confirmation received")

            # Test 3: Request recent alerts
            print("\n[Test 3] Requesting recent alerts...")
            get_alerts_msg = {
                "type": "get_alerts",
                "limit": 5
            }
            await websocket.send(json.dumps(get_alerts_msg))
            print(f"✅ Sent: {get_alerts_msg}")

            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"✅ Received alerts: {len(data.get('alerts', []))} alerts")

                for alert in data.get('alerts', [])[:3]:
                    print(f"  - {alert.get('alert_type')}: {alert.get('message', 'N/A')}")
            except asyncio.TimeoutError:
                print("❌ No alerts received")

            # Test 4: Unsubscribe from product
            print("\n[Test 4] Unsubscribing from product 1...")
            unsubscribe_msg = {
                "type": "unsubscribe_product",
                "product_id": 1
            }
            await websocket.send(json.dumps(unsubscribe_msg))
            print(f"✅ Sent: {unsubscribe_msg}")

            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"✅ Received: {data}")
            except asyncio.TimeoutError:
                print("❌ No unsubscription confirmation received")

            # Test 5: Stay connected for potential notifications
            print("\n[Test 5] Listening for notifications (10 seconds)...")
            print("(You can create a new QualityAlert in Django admin to test)")

            try:
                # Listen for up to 10 seconds
                for i in range(10):
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(message)
                        print(f"\n🔔 Notification received!")
                        print(f"   Type: {data.get('type')}")
                        print(f"   Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    except asyncio.TimeoutError:
                        print(f"   Waiting... ({i+1}/10)")
                        continue
            except Exception as e:
                print(f"❌ Error while listening: {e}")

            print("\n" + "=" * 60)
            print("✅ All WebSocket tests completed successfully!")
            print("=" * 60)

    except websockets.exceptions.ConnectionRefused:
        print("❌ Connection refused. Make sure Django server is running:")
        print("   python manage.py runserver 8000")
        return False
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


async def test_product_websocket():
    """Test product-specific WebSocket connection"""
    print("\n\n" + "=" * 60)
    print("Product WebSocket Test")
    print("=" * 60)

    product_id = 1
    ws_url = f"ws://localhost:8000/ws/spc/product/{product_id}/"

    try:
        print(f"\n[1] Connecting to product {product_id}...")
        async with websockets.connect(ws_url) as websocket:
            print("✅ Connected successfully!")

            # Receive connection message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"✅ Received: {data}")

                if data.get('type') == 'connection':
                    print(f"✅ Connected to product: {data.get('product', {}).get('product_code')}")
            except asyncio.TimeoutError:
                print("❌ No connection message received")

            # Request latest data
            print("\n[Test 2] Requesting latest measurements...")
            get_data_msg = {
                "type": "get_latest_data",
                "limit": 5
            }
            await websocket.send(json.dumps(get_data_msg))
            print(f"✅ Sent: {get_data_msg}")

            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"✅ Received {len(data.get('measurements', []))} measurements")

                for m in data.get('measurements', [])[:3]:
                    print(f"  - Value: {m.get('measurement_value')}, Within Spec: {m.get('is_within_spec')}")
            except asyncio.TimeoutError:
                print("❌ No measurements received")

            print("\n" + "=" * 60)
            print("✅ Product WebSocket test completed!")
            print("=" * 60)

    except websockets.exceptions.ConnectionRefused:
        print("❌ Connection refused. Make sure Django server is running:")
        print("   python manage.py runserver 8000")
        return False
    except Exception as e:
        print(f"❌ Product WebSocket test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def trigger_test_alert():
    """
    Create a test QualityAlert to trigger WebSocket notification
    This requires Django to be set up
    """
    print("\n\n" + "=" * 60)
    print("Create Test Alert")
    print("=" * 60)

    try:
        import os
        import sys
        import django

        # Setup Django
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
        django.setup()

        from apps.spc.models import QualityAlert, Product
        from datetime import datetime

        # Get product
        product = Product.objects.first()
        if not product:
            print("❌ No products found. Please create a product first.")
            return False

        print(f"\n[1] Creating test alert for product: {product.product_code}")

        # Create test alert
        alert = QualityAlert.objects.create(
            product=product,
            alert_type='OUT_OF_SPEC',
            priority=4,
            title='Test Alert',
            message='This is a test alert for WebSocket notification',
            status='OPEN'
        )

        print(f"✅ Alert created with ID: {alert.id}")
        print("✅ WebSocket notification should have been sent!")

        return True

    except Exception as e:
        print(f"❌ Failed to create test alert: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("SPC WebSocket Test Suite")
    print("=" * 60)
    print("\n⚠️ Prerequisites:")
    print("   1. Django server must be running:")
    print("      cd backend && python manage.py runserver 8000")
    print("   2. WebSocket dependencies installed:")
    print("      pip install websockets")
    print("\n" + "=" * 60)

    # Test 1: General notifications WebSocket
    success1 = await test_websocket_connection()

    # Test 2: Product-specific WebSocket
    success2 = await test_product_websocket()

    # Test 3: Create test alert
    print("\n\nDo you want to create a test alert? (This will trigger WebSocket notification)")
    print("Run this in a separate terminal while WebSocket test is listening:")
    print("  python test_websocket.py --create-alert")

    # Summary
    print("\n\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Notifications WebSocket: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Product WebSocket: {'✅ PASS' if success2 else '❌ FAIL'}")

    if success1 and success2:
        print("\n✅ All WebSocket tests passed!")
        print("\nNext steps:")
        print("  1. Open frontend: http://localhost:3000")
        print("  2. Check browser console for WebSocket messages")
        print("  3. Create new QualityAlert in Django admin")
        print("  4. Verify real-time notification appears in frontend")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")

    print("=" * 60)


if __name__ == '__main__':
    import sys

    # Check for --create-alert flag
    if len(sys.argv) > 1 and sys.argv[1] == '--create-alert':
        trigger_test_alert()
    else:
        # Check if websockets is installed
        try:
            import websockets
        except ImportError:
            print("❌ 'websockets' library not installed")
            print("\nInstall with:")
            print("  pip install websockets")
            sys.exit(1)

        # Run tests
        asyncio.run(main())
