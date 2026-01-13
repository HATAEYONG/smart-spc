# WebSocket 실시간 알림 가이드

## 개요

SPC 품질관리 시스템의 WebSocket 실시간 알림 기능은 품질 이벤트 발생 시 즉시 사용자에게 알림을 전송합니다.

---

## 기능

### 1. 실시간 알림 유형

- **품질 경고 (Alert)**: 새로운 QualityAlert 생성 시
- **측정 데이터 (Measurement)**: 규격 외/관리한계 외 측정값 생성 시
- **공정능력 (Capability)**: 공정능력 분석 완료 시
- **Run Rule 위반**: 통계적 규칙 위반 감지 시

### 2. WebSocket 엔드포인트

| 엔드포인트 | 용도 |
|-----------|------|
| `ws://localhost:8000/ws/spc/notifications/` | 일반 알림 |
| `ws://localhost:8000/ws/spc/product/{id}/` | 제품별 알림 |

---

## 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │      RealtimeNotifications.tsx                        │ │
│  │  - WebSocket 연결 관리                                  │ │
│  │  - 메시지 수신 및 토스트 표시                           │ │
│  │  - 자동 재연결                                          │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ WebSocket Protocol
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (Django)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           ASGI Application (asgi.py)                   │ │
│  │  - ProtocolTypeRouter (HTTP + WebSocket)               │ │
│  │  - AuthMiddlewareStack                                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         SPC Routing (routing.py)                       │ │
│  │  - /ws/spc/notifications/                              │ │
│  │  - /ws/spc/product/{id}/                              │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          WebSocket Consumers (consumers.py)            │ │
│  │  - SPCNotificationConsumer                             │ │
│  │  - ProductDataConsumer                                 │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Channel Layer
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Django Signals (signals.py)                    │
│  - QualityAlert post_save → WebSocket notification         │
│  - QualityMeasurement post_save → WebSocket notification   │
│  - ProcessCapability post_save → WebSocket notification   │
└─────────────────────────────────────────────────────────────┘
```

---

## 사용 방법

### 1. 서버 시작

**Backend (Django with Channels):**
```bash
cd backend
python manage.py runserver 8000
```

**Frontend (Vite):**
```bash
cd frontend
npm run dev
```

### 2. WebSocket 연결

프론트엔드에서 자동으로 WebSocket 연결이 시도됩니다. 브라우저 개발자 콘솔에서 확인:

```javascript
// WebSocket connecting to: ws://localhost:8000/ws/spc/notifications/
// WebSocket connected successfully
```

### 3. 알림 수신

연결되면 다음 이벤트에서 자동 알림:

1. **새로운 QualityAlert 생성** (Django Admin 또는 API)
2. **규격 외 측정값 입력**
3. **공정능력 분석 실행**
4. **Run Rule 위반 발생**

---

## 테스트

### 1. WebSocket 연결 테스트

```bash
# websockets 라이브러리 설치
pip install websockets

# 테스트 스크립트 실행
python test_websocket.py
```

### 2. 테스트 경고 생성

**방법 1: Django Admin**
1. http://localhost:8000/admin 접속
2. SPC → QualityAlert 이동
3. 새로운 경고 생성

**방법 2: Python 스크립트**
```bash
python test_websocket.py --create-alert
```

**방법 3: API**
```bash
curl -X POST http://localhost:8000/api/spc/alerts/ \
  -H "Content-Type: application/json" \
  -d '{
    "product": 1,
    "alert_type": "OUT_OF_SPEC",
    "priority": 4,
    "title": "Test Alert",
    "message": "WebSocket test alert"
  }'
```

---

## WebSocket 메시지 형식

### 클라이언트 → 서버

**제품 구독:**
```json
{
  "type": "subscribe_product",
  "product_id": 1
}
```

**제품 구독 해지:**
```json
{
  "type": "unsubscribe_product",
  "product_id": 1
}
```

**최근 알림 요청:**
```json
{
  "type": "get_alerts",
  "limit": 10
}
```

### 서버 → 클라이언트

**연결 성공:**
```json
{
  "type": "connection",
  "message": "SPC 실시간 알림에 연결되었습니다",
  "timestamp": "2026-01-11T12:00:00"
}
```

**품질 경고:**
```json
{
  "type": "alert",
  "alert": {
    "id": 1,
    "product_code": "BOLT-M10",
    "product_name": "M10 볼트",
    "alert_type": "OUT_OF_SPEC",
    "priority": 4,
    "title": "규격 이탈",
    "message": "측정값이 상한 규격을 초과했습니다",
    "status": "OPEN",
    "created_at": "2026-01-11T12:00:00"
  },
  "timestamp": "2026-01-11T12:00:00"
}
```

**측정 데이터:**
```json
{
  "type": "measurement",
  "measurement": {
    "id": 1001,
    "product_id": 1,
    "product_code": "BOLT-M10",
    "measurement_value": 10.65,
    "sample_number": 50,
    "subgroup_number": 10,
    "is_within_spec": false,
    "is_within_control": true,
    "measured_at": "2026-01-11T12:00:00"
  },
  "timestamp": "2026-01-11T12:00:00"
}
```

**공정능력 업데이트:**
```json
{
  "type": "capability",
  "capability": {
    "id": 5,
    "product_id": 1,
    "product_code": "BOLT-M10",
    "cp": 2.13,
    "cpk": 1.70,
    "pp": 2.05,
    "ppk": 1.65,
    "analyzed_at": "2026-01-11T12:00:00"
  },
  "timestamp": "2026-01-11T12:00:00"
}
```

---

## 프론트엔드 구현

### RealtimeNotifications.tsx

```typescript
// WebSocket 연결
useEffect(() => {
  const wsUrl = 'ws://localhost:8000/ws/spc/notifications/';
  const ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log('WebSocket connected');
    setWsEnabled(true);

    // 제품 구독
    ws.send(JSON.stringify({
      type: 'subscribe_product',
      product_id: 1
    }));
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    switch (data.type) {
      case 'alert':
        // 토스트 알림 표시
        addToast({
          type: 'alert',
          title: `품질 경고: ${data.alert.product_code}`,
          message: data.alert.message
        });
        break;
      // ... 다른 메시지 타입 처리
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    setWsEnabled(false);
  };

  ws.onclose = () => {
    console.log('WebSocket closed');
    setWsEnabled(false);

    // 자동 재연결
    setTimeout(() => {
      // 재연결 로직
    }, 5000);
  };

  return () => {
    ws.close();
  };
}, []);
```

---

## 백엔드 구현

### Signal-based 자동 알림

```python
# apps/spc/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import QualityAlert
from .services.websocket_notifier import WebSocketNotifier

@receiver(post_save, sender=QualityAlert)
def alert_created(sender, instance, created, **kwargs):
    """품질 경고 생성 시 자동 알림"""
    if created:
        WebSocketNotifier.notify_alert(instance)
```

### 수동 알림 전송

```python
from apps.spc.services.websocket_notifier import WebSocketNotifier

# 품질 경고 알림
WebSocketNotifier.notify_alert(alert_instance)

# 측정 데이터 알림
WebSocketNotifier.notify_measurement(measurement_instance)

# 공정능력 알림
WebSocketNotifier.notify_capability(capability_instance)
```

---

## 문제 해결

### 연결 거부 오류

**에러:**
```
WebSocket connection to 'ws://localhost:8000/ws/spc/notifications/' failed
```

**해결 방법:**
1. Django 서버가 실행 중인지 확인
   ```bash
   python manage.py runserver 8000
   ```

2. Channels가 설치되어 있는지 확인
   ```bash
   pip install channels channels-redis
   ```

3. ASGI 설정 확인 (config/asgi.py)

### 메시지 수신 안됨

**해결 방법:**
1. 브라우저 콘솔에서 WebSocket 연결 상태 확인
2. Django 로그에서 시그널 실행 확인
3. 제품을 올바르게 구독했는지 확인

### 재연결 불가

**해결 방법:**
- 프론트엔드에서 자동 재연결 로직 확인
- 네트워크 안정성 확인
- Django 서버 재시작

---

## 성능 최적화

### 1. Redis Channel Layer (권장)

**개발 환경 (In-Memory):**
```python
# config/settings/dev.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}
```

**프로덕션 (Redis):**
```python
# config/settings/production.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(REDIS_HOST, REDIS_PORT)],
        },
    },
}
```

**Redis 설치:**
```bash
pip install channels-redis
```

### 2. 연결 풀 관리

- 동시 연결 수 제한
- 연결 타임아웃 설정
-_idle_ 연결 정리

### 3. 메시지 배치 처리

여러 알림을 한 번에 전송하여 오버헤드 감소

---

## 보안 고려사항

### 1. 인증

**현재:** 개발용 (anonymous)

**프로덕션 권장:**
```python
# consumers.py
from channels.auth import AuthMiddlewareStack

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
```

### 2. 권한

사용자별로 제품 접근 권한 제어 필요

### 3. Rate Limiting

연결 및 메시지 전송 속도 제한

---

## 모니터링

### 로그 확인

**Django 로그:**
```bash
python manage.py runserver 8000
# WebSocket 연결 및 메시지 로그 확인
```

**브라우저 콘솔:**
```javascript
// WebSocket 메시지 로그
console.log('WebSocket message received:', data);
```

### 연결 상태 모니터링

```python
# 관리자 명령어 생성 가능
# python manage.py websocket_status
```

---

## 다음 단계

### 1. 프로덕션 배포

- Redis Channel Layer로 마이그레이션
- SSL/TLS (WSS) 설정
- 로드 밸런서에서 WebSocket 지원

### 2. 고급 기능

- 알림 우선순위 필터링
- 사용자별 알림 기본 설정
- 알림 히스토리 조회
- 알림 통계 대시보드

### 3. 모바일 지원

- React Native WebSocket 연결
- 푸시 알림 통합

---

## 참고 자료

- [Django Channels 문서](https://channels.readthedocs.io/)
- [WebSocket API MDN](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Channels Redis Layer](https://github.com/django/channels_redis/)

---

**버전**: 1.0.0
**마지막 업데이트**: 2026-01-11
**유지관리**: SPC 개발팀
