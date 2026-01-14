# SPC (Statistical Process Control) Quality Control System

**AI 기반 품질관리 시스템 - 통계적 공정관리 및 실시간 모니터링**

[![CI](https://img.shields.io/badge/CI-CD-success)](https://github.com/username/spc-scheduler/actions)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-4.2+-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 📋 목차 (Table of Contents)

- [개요](#개요-overview)
- [주요 기능](#주요-기능-key-features)
- [기술 스택](#기술-스택-tech-stack)
- [빠른 시작](#빠른- 시작-quick-start)
- [설치 방법](#설치-방법-installation)
- [사용 방법](#사용-방법-usage)
- [API 문서](#api-문서-api-documentation)
- [개발 가이드](#개발-가이드-development-guide)
- [배포](#배포-deployment)

---

## 개요 (Overview)

SPC 품질관리 시스템은 제조 현장의 품질 데이터를 실시간으로 수집, 분석, 모니터링하는 AI 기반 통계적 공정관리 솔루션입니다.

### 핵심 가치

- 🎯 **실시간 모니터링**: 생산 라인의 품질 데이터를 실시간으로 추적
- 🤖 **AI 기반 분석**: LLM을 활용한 지능형 품질 분석 및 예측
- 📊 **통계적 공정관리**: Western Electric Rules 기반 관리도 및 공정능력 분석
- 🔔 **자동 알림**: 이상 징후 자동 감지 및 즉시 알림
- 📈 **시계열 예측**: 4가지 알고리즘을 활용한 미래 품질 예측
- 📱 **반응형 웹**: 모든 디바이스에서 접근 가능한 PWA 지원

---

## 주요 기능 (Key Features)

### 1. 📊 품질 데이터 관리
- **제품 관리**: 다양한 제품의 규격 설정 및 관리
- **검사 계획**: 주기별 샘플링 계획 수립
- **측정 데이터**: 실시간 품질 측정값 수집
- **데이터 추적**: 로트별, 기계별 추적 가능

### 2. 📈 통계적 공정관리 (SPC)
- **관리도 (Control Charts)**:
  - X-bar & R Chart
  - X-bar & S Chart
  - Individual & Moving Range (I-MR) Chart
  - p-Chart, np-Chart, c-Chart, u-Chart
- **Western Electric Rules**: 8가지 Run Rule 자동 감지
- **공정능력 분석**: Cp, Cpk, Pp, Ppk 지수 계산
- **정규성 검정**: Anderson-Darling 테스트

### 3. 🤖 AI 기반 분석
- **5개 AI 제공자 지원**:
  - OpenAI GPT-4 (최고 성능)
  - Anthropic Claude 3 Opus (긴 컨텍스트)
  - Google Gemini Pro (무료 사용 가능)
  - Ollama (로컬 오픈소스: Llama 2, Mistral)
  - HuggingFace (클라우드 오픈소스)
- **자동 분석**: 데이터 패턴 자동 해석
- **지능형 조언**: 품질 개선 방안 제시
- **비용 최적화**: 응답 캐싱으로 API 비용 절감

**자세한 내용**: [AI_SERVICE_GUIDE.md](AI_SERVICE_GUIDE.md)

### 4. 📉 시계열 예측
- **4가지 예측 알고리즘**:
  - Simple Moving Average (단순 이동평균)
  - Exponential Smoothing (지수 평활)
  - Linear Trend (선형 추세)
  - Combined Ensemble (결합 앙상블)
- **이상 감지**:
  - Z-score 기반 통계적 이상 감지
  - 패턴 기반 이상 감지 (Spike, Trend Shift)
- **예지 보전**: 설비 건전도 점수 및 고장 예측

### 5. 🔔 알림 및 경고
- **실시간 알림**:
  - 규격 이탈 (Out of Spec)
  - 관리 한계 이탈 (Out of Control)
  - Run Rule 위반
  - 트렌드 경고
- **우선순위**: 4단계 우선순위 (낮음, 보통, 높음, 긴급)
- **상태 관리**: 신규 → 확인 → 조사중 → 해결 → 종료
- **근본 원인 분석**: 5Why, Fishbone 도구 지원

### 6. 📱 사용자 인터페이스
- **반응형 디자인**: Desktop, Tablet, Mobile 지원
- **PWA (Progressive Web App)**: 오프라인 지원
- **다크 모드**: 눈의 피로 감소
- **대시보드 커스터마이징**: 위젯 배치 및 크기 조절
- **3D 시각화**: Plotly.js 기반 인터랙티브 차트
- **접근성**: WCAG 2.1 준수

### 7. 🔐 인증 및 권한
- **JWT 기반 인증**: Access Token + Refresh Token
- **역할 기반 접근제어 (RBAC)**:
  - Admin: 전체 권한
  - Quality Manager: 관리 및 승인
  - Quality Engineer: 분석 및 조사
  - Operator: 데이터 입력 및 조회
- **토큰 블랙리스트**: 로그아웃된 토큰 관리

### 8. ⚡ 비동기 처리
- **Celery Integration**: 백그라운드 작업 처리
- **주기적 작업**: 일일 보고서, 시계열 분석 자동 실행
- **Flower Monitoring**: Celery 작업 모니터링 대시보드
- **작업 큐**: 이메일 발송, 보고서 생성 등

---

## 기술 스택 (Tech Stack)

### Backend
```
Python 3.11+
├── Django 4.2+          # Web Framework
├── Django REST Framework    # API Framework
├── Django Channels      # WebSocket Support
├── PostgreSQL 15        # Database
├── Redis 7              # Cache & Message Broker
├── Celery 5             # Async Task Queue
├── Gunicorn             # WSGI Server
└── Nginx                # Reverse Proxy
```

### Frontend
```
TypeScript 5+
├── React 18             # UI Library
├── Vite 5               # Build Tool
├── React Router 6       # Routing
├── TanStack Query       # Data Fetching
├── Zustand              # State Management
├── Plotly.js            # Data Visualization
└── Tailwind CSS         # Styling
```

### DevOps
```
├── Docker               # Containerization
├── Docker Compose       # Orchestration
├── GitHub Actions       # CI/CD
└── Nginx                # Web Server
```

---

## 빠른 시작 (Quick Start)

### Docker Compose로 시작 (권장)

```bash
# 1. 저장소 복제
git clone https://github.com/username/spc-scheduler.git
cd spc-scheduler

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일에서 필요한 설정 변경

# 3. 모든 서비스 시작
docker-compose up -d

# 4. 데이터베이스 마이그레이션
docker-compose exec backend python manage.py migrate

# 5. 슈퍼유저 생성
docker-compose exec backend python manage.py createsuperuser

# 6. 샘플 데이터 생성 (선택사항)
docker-compose exec backend python scripts/create_sample_data.py

# 7. 서비스 접속
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000/api
# Backend Health: http://localhost:8000/health/
# Django Admin: http://localhost:8000/admin
# Flower (Celery Monitoring): http://localhost:5555
```

### 개발 환경 설정

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Frontend (별도 터미널)
cd frontend
npm install
npm run dev
```

---

## 설치 방법 (Installation)

### 요구사항 (Prerequisites)

- **Python**: 3.11 이상
- **Node.js**: 18 이상
- **PostgreSQL**: 15 이상
- **Redis**: 7 이상
- **Docker**: 20.10 이상 (선택사항)

### Backend 설치

```bash
cd backend

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example ../.env
# .env 파일 편집

# 데이터베이스 마이그레이션
python manage.py migrate

# 슈퍼유저 생성
python manage.py createsuperuser

# 개발 서버 시작
python manage.py runserver
```

### Frontend 설치

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 시작 (VITE_API_URL은 자동 설정됨)
npm run dev

# 프로덕션 빌드
npm run build
```

**환경 변수** (`.env`):
```bash
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
```

---

## 사용 방법 (Usage)

### 샘플 데이터 생성

```bash
# 기본 설정 (5개 제품, 30일 데이터)
python manage.py create_sample_data

# 사용자 정의
python manage.py create_sample_data --products=10 --days=60

# 기존 데이터 삭제 후 생성
python manage.py create_sample_data --clear
```

**자세한 내용**: [SAMPLE_DATA_COMMAND.md](SAMPLE_DATA_COMMAND.md)

### 데모 계정

| 사용자 | 역할 | 비밀번호 |
|--------|------|----------|
| admin_spc | Admin | demo1234 |
| demo_manager | Quality Manager | demo1234 |
| demo_engineer | Quality Engineer | demo1234 |
| demo_operator | Operator | demo1234 |

### 주요 API 엔드포인트

#### SPC (Statistical Process Control) API

```
# 제품 관리
GET    /api/products/              # 제품 목록
POST   /api/products/              # 제품 생성
GET    /api/products/{id}/         # 제품 상세
PUT    /api/products/{id}/         # 제품 수정
DELETE /api/products/{id}/         # 제품 삭제

# 검사 계획
GET    /api/inspection-plans/      # 검사 계획 목록
POST   /api/inspection-plans/      # 검사 계획 생성
GET    /api/inspection-plans/{id}/ # 검사 계획 상세

# 품질 측정
GET    /api/measurements/          # 측정 데이터 목록
POST   /api/measurements/          # 측정 데이터 생성
GET    /api/measurements/{id}/     # 측정 데이터 상세
GET    /api/measurements/bulk-upload/  # 대량 업로드

# 관리도
GET    /api/control-charts/        # 관리도 목록
GET    /api/control-charts/{id}/   # 관리도 상세
GET    /api/control-charts/{id}/data/  # 관리도 데이터 포인트

# 공정능력
GET    /api/capabilities/          # 공정능력 목록
GET    /api/capabilities/{id}/     # 공정능력 상세
POST   /api/capabilities/analyze/  # 공정능력 분석 요청

# Run Rule 위반
GET    /api/violations/            # 위반 목록
GET    /api/violations/{id}/       # 위반 상세

# 알림
GET    /api/alerts/                # 알림 목록
GET    /api/alerts/{id}/           # 알림 상세
PATCH  /api/alerts/{id}/acknowledge  # 알림 확인
PATCH  /api/alerts/{id}/resolve    # 알림 해결
GET    /api/alerts/dashboard/      # 알림 대시보드 요약
```

#### Predictive Maintenance API

```
# 설비 관리
GET    /api/equipment/             # 설비 목록
POST   /api/equipment/             # 설비 생성
GET    /api/equipment/{id}/        # 설비 상세
GET    /api/equipment/{id}/health/ # 설비 건전도

# 센서 데이터
GET    /api/sensor-data/           # 센서 데이터 목록
POST   /api/sensor-data/           # 센서 데이터 생성
GET    /api/sensor-data/latest/    # 최신 센서 데이터
GET    /api/sensor-data/statistics/ # 센서 데이터 통계

# 예방 보전 계획
GET    /api/maintenance-plans/     # 보전 계획 목록
POST   /api/maintenance-plans/     # 보전 계획 생성
GET    /api/maintenance-plans/{id}/ # 보전 계획 상세
GET    /api/maintenance-plans/calendar/  # 📅 캘린더 형태 일정
GET    /api/maintenance-plans/upcoming/  # 📅 다가오는 일정 (7일 이내)
GET    /api/maintenance-plans/overdue/   # 📅 지연된 계획

# 보전 기록
GET    /api/maintenance-records/   # 보전 기록 목록
POST   /api/maintenance-records/   # 보전 기록 생성
GET    /api/maintenance-records/{id}/  # 보전 기록 상세

# 고장 예측
GET    /api/failure-predictions/   # 고장 예측 목록
POST   /api/failure-predictions/predict/  # 예측 요청
```

#### AI Analysis API

```
# AI 분석
POST   /api/ai/analyze/            # LLM 분석 요청
POST   /api/ai/forecast/           # 예측 요청
GET    /api/ai/cache/              # 캐시된 분석 결과
DELETE /api/ai/cache/{id}/         # 캐시 삭제
```

#### Quality Cost API

```
# 품질 비용
GET    /api/quality-costs/         # 품질 비용 목록
POST   /api/quality-costs/         # 품질 비용 생성
GET    /api/quality-costs/summary/ # 품질 비용 요약
```

#### 인증 API

```
POST   /api/auth/register/         # 회원가입
POST   /api/auth/login/            # 로그인
POST   /api/auth/token/refresh/    # 토큰 갱신
POST   /api/auth/logout/           # 로그아웃
```

---

## API 문서 (API Documentation)

### Swagger UI
개발 모드에서 Swagger UI 제공:
- http://localhost:8000/api/docs/

### Postman Collection
`docs/postman_collection.json` 파일 참조

### 상세 API 명세서

#### 기본 정보

**Base URL**: `http://localhost:8000/api`

**인증 방식**: JWT (JSON Web Token)
```
Authorization: Bearer <access_token>
```

**응답 형식**: JSON
```
{
  "count": 100,
  "next": "http://api.example.com/resource/?page=2",
  "previous": null,
  "results": [...]
}
```

---

#### Predictive Maintenance Calendar API

**1. 캘린더 형태 일정 조회**

```http
GET /api/maintenance-plans/calendar/?start_date=2026-01-01&end_date=2026-01-31&equipment=1
```

**Query Parameters:**
- `start_date` (string, optional): 조회 시작日期 (YYYY-MM-DD)
- `end_date` (string, optional): 조회 종료日期 (YYYY-MM-DD)
- `equipment` (integer, optional): 설비 ID 필터

**Response:**
```json
[
  {
    "id": 1,
    "title": "정기 점검 - CNC 머신 A",
    "start": "2026-01-15",
    "end": "2026-01-15",
    "backgroundColor": "#ef4444",
    "borderColor": "#dc2626",
    "equipment": 1,
    "plan_type": "DAILY",
    "frequency_display": "매일",
    "days_remaining": 2,
    "is_overdue": false
  }
]
```

**색상 코드 (우선순위):**
- `#ef4444` (빨강): 긴급 (D-3 이내)
- `#f97316` (주황): 주의 (D-7 이내)
- `#eab308` (노랑): 예약됨 (D-14 이내)
- `#3b82f6` (파랑): 정상 (D-15 이상)

---

**2. 다가오는 예방 보전 일정**

```http
GET /api/maintenance-plans/upcoming/
```

**설명**: 향후 7일 이내의 예방 보전 일정 반환

**Response:**
```json
[
  {
    "id": 5,
    "equipment": 1,
    "equipment_name": "CNC 머신 A",
    "plan_name": "주간 정기 점검",
    "plan_type": "WEEKLY",
    "frequency_display": "매주",
    "next_due_date": "2026-01-16T10:00:00Z",
    "days_remaining": 2,
    "assigned_to": "홍길동",
    "task_description": "오일 교체, 베어링 점검",
    "priority": "HIGH",
    "estimated_duration": 120
  }
]
```

---

**3. 지연된 예방 보전 계획**

```http
GET /api/maintenance-plans/overdue/
```

**설명**: 기한이 지난 미완료 보전 계획 반환

**Response:**
```json
[
  {
    "id": 8,
    "equipment": 3,
    "equipment_name": "프레스 기계 B",
    "plan_name": "월간 안전 점검",
    "plan_type": "MONTHLY",
    "due_date": "2026-01-10T10:00:00Z",
    "days_overdue": 4,
    "assigned_to": "김철수",
    "priority": "URGENT"
  }
]
```

---

#### SPC 품질관리 API

**1. 제품 목록 조회**

```http
GET /api/products/?page=1&page_size=20&is_active=true
```

**Query Parameters:**
- `page` (integer, optional): 페이지 번호 (default: 1)
- `page_size` (integer, optional): 페이지당 결과 수 (default: 20)
- `is_active` (boolean, optional): 활성화된 제품만 필터
- `search` (string, optional): 제품명/코드 검색

**Response:**
```json
{
  "count": 45,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "product_code": "PRD-001",
      "product_name": "자동차 부품 A",
      "usl": 10.5,
      "lsl": 9.5,
      "target_value": 10.0,
      "unit": "mm",
      "description": "엔진 부품",
      "is_active": true,
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-01-14T12:00:00Z"
    }
  ]
}
```

---

**2. 품질 측정 데이터 생성**

```http
POST /api/measurements/
```

**Request Body:**
```json
{
  "product": 1,
  "inspection_plan": 5,
  "measurement_value": 10.23,
  "sample_number": 1,
  "subgroup_number": 100,
  "measured_at": "2026-01-14T10:30:00Z",
  "measured_by": "operator_1",
  "machine_id": "MACHINE-A",
  "lot_number": "LOT-2026-0114",
  "remarks": "정상 측정"
}
```

**Response:**
```json
{
  "id": 5001,
  "product": 1,
  "product_name": "자동차 부품 A",
  "product_code": "PRD-001",
  "measurement_value": 10.23,
  "is_within_spec": true,
  "is_within_control": true,
  "created_at": "2026-01-14T10:30:00Z"
}
```

---

**3. 관리도 데이터 조회**

```http
GET /api/control-charts/{id}/data/?limit=50
```

**Path Parameters:**
- `id` (integer, required): 관리도 ID

**Query Parameters:**
- `limit` (integer, optional): 반환할 데이터 포인트 수 (default: 50)

**Response:**
```json
{
  "chart_type": "XBAR_R",
  "limits": {
    "xbar": {
      "ucl": 10.45,
      "cl": 10.02,
      "lcl": 9.59
    },
    "r": {
      "ucl": 0.82,
      "cl": 0.35,
      "lcl": 0.00
    }
  },
  "data": [
    {
      "subgroup_number": 95,
      "xbar": 10.05,
      "r": 0.42,
      "measured_at": "2026-01-14T09:00:00Z"
    }
  ]
}
```

---

**4. 공정능력 분석 요청**

```http
POST /api/capabilities/analyze/
```

**Request Body:**
```json
{
  "product": 1,
  "analysis_start": "2026-01-01T00:00:00Z",
  "analysis_end": "2026-01-14T23:59:59Z",
  "confidence_level": 0.95
}
```

**Response:**
```json
{
  "id": 1,
  "product": 1,
  "product_name": "자동차 부품 A",
  "cp": 1.67,
  "cpk": 1.42,
  "cpu": 1.55,
  "cpl": 1.28,
  "mean": 10.02,
  "std_deviation": 0.12,
  "sample_size": 500,
  "is_normal": true,
  "normality_test_statistic": 0.023,
  "normality_test_p_value": 0.48,
  "analysis_start": "2026-01-01T00:00:00Z",
  "analysis_end": "2026-01-14T23:59:59Z",
  "analyzed_at": "2026-01-14T15:00:00Z"
}
```

---

**5. 알림 대시보드 요약**

```http
GET /api/alerts/dashboard/
```

**Response:**
```json
{
  "total": 25,
  "by_priority": {
    "urgent": 3,
    "high": 7,
    "medium": 10,
    "low": 5
  },
  "by_status": {
    "new": 8,
    "acknowledged": 5,
    "investigating": 4,
    "resolved": 6,
    "closed": 2
  },
  "by_type": {
    "OUT_OF_SPEC": 5,
    "OUT_OF_CONTROL": 8,
    "RUN_RULE": 7,
    "TREND": 3,
    "PREDICTION": 2
  }
}
```

---

#### AI 분석 API

**1. LLM 기반 품질 분석**

```http
POST /api/ai/analyze/
```

**Request Body:**
```json
{
  "product": 1,
  "analysis_type": "control_chart",
  "time_range": "7d",
  "ai_provider": "openai",
  "include_recommendations": true
}
```

**Response:**
```json
{
  "id": "analysis_123",
  "product": 1,
  "analysis_type": "control_chart",
  "summary": "최근 7일간 공정은 안정적인 상태를 유지하고 있습니다.",
  "key_findings": [
    "모든 데이터 포인트가 관리 한계 내에 위치",
    "Cpk 지수 1.42로 우수한 공정능력 달성"
  ],
  "recommendations": [
    "현재 공정 파라미터 유지 권장",
    "주간 보고서에 포함될 수 있는 우수 사례"
  ],
  "charts_used": ["XBAR_R"],
  "analyzed_at": "2026-01-14T15:30:00Z",
  "cache_id": "cache_456"
}
```

---

**2. 시계열 예측**

```http
POST /api/ai/forecast/
```

**Request Body:**
```json
{
  "product": 1,
  "forecast_periods": 10,
  "algorithms": ["sma", "exponential_smoothing", "linear_trend", "combined"],
  "confidence_interval": 0.95
}
```

**Response:**
```json
{
  "product": 1,
  "product_name": "자동차 부품 A",
  "forecast_data": [
    {
      "period": 101,
      "forecast": 10.05,
      "lower_bound": 9.82,
      "upper_bound": 10.28
    }
  ],
  "anomalies": [
    {
      "period": 95,
      "value": 11.2,
      "z_score": 3.4,
      "type": "SPIKE"
    }
  ],
  "algorithm_performance": {
    "sma": { "mse": 0.023 },
    "combined": { "mse": 0.018 }
  }
}
```

---

#### WebSocket API

**연결:**

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/quality-updates/');

ws.onopen = () => {
  // 인증 토큰 전송
  ws.send(JSON.stringify({
    type: 'authenticate',
    token: 'your_jwt_token'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

**이벤트 타입:**

1. **새 측정 데이터**
```json
{
  "type": "new_measurement",
  "data": {
    "product": 1,
    "value": 10.23,
    "is_out_of_spec": false
  }
}
```

2. **알림 발생**
```json
{
  "type": "new_alert",
  "data": {
    "alert_id": 123,
    "priority": "HIGH",
    "message": "규격 이탈 감지",
    "product": "PRD-001"
  }
}
```

3. **Run Rule 위반**
```json
{
  "type": "violation_detected",
  "data": {
    "rule": "RULE_1",
    "description": "1개 포인트가 3시그마 밖에 위치",
    "chart": 5
  }
}
```

---

#### 에러 응답

**400 Bad Request**
```json
{
  "detail": "Validation error",
  "errors": {
    "measurement_value": ["This field is required."],
    "product": ["Invalid product ID."]
  }
}
```

**401 Unauthorized**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**404 Not Found**
```json
{
  "detail": "Not found."
}
```

**429 Rate Limit Exceeded**
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

**500 Internal Server Error**
```json
{
  "detail": "Internal server error. Please contact support.",
  "error_code": "ERR-5001"
}
```

---

## 개발 가이드 (Development Guide)

### 프로젝트 구조

```
online-aps-cps-scheduler/
├── backend/
│   ├── apps/
│   │   ├── spc/              # SPC 핵심 기능
│   │   │   ├── models/       # Data Models
│   │   │   ├── views/        # API Views
│   │   │   ├── services/     # Business Logic
│   │   │   │   ├── llm_service.py
│   │   │   │   └── time_series_analysis.py
│   │   │   └── serializers/  # DRF Serializers
│   │   └── auth_app/         # 인증
│   ├── config/               # Django Settings
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       # React Components
│   │   ├── pages/            # Page Components
│   │   ├── services/         # API Services
│   │   ├── store/            # Zustand Store
│   │   └── types/            # TypeScript Types
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── .github/
    └── workflows/
        ├── ci.yml
        └── cd.yml
```

### 코드 컨벤션

**Backend (Python)**
- PEP 8 준수
- Black formatting
- isort import 정렬
- Docstring (Google Style)

**Frontend (TypeScript)**
- ESLint + Prettier
- Functional Components
- Custom Hooks for Logic
- TypeScript Strict Mode

---

## 배포 (Deployment)

### Docker 배포

```bash
# 프로덕션 빌드
export BUILD_TARGET=production
docker-compose build

# 프로덕션 시작
docker-compose --profile production up -d
```

### CI/CD

GitHub Actions를 통한 자동화:
- **CI**: 푸시/PR 시 자동 테스트
- **CD**: main 브랜치 자동 배포

**자세한 내용**:
- [PHASE4_DOCKER_COMPLETE.md](PHASE4_DOCKER_COMPLETE.md) - Docker 컨테이너화
- [PHASE4_CICD_COMPLETE.md](PHASE4_CICD_COMPLETE.md) - CI/CD 파이프라인

### 배포 체크리스트

**자세한 내용**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

---

## 문서 (Documentation)

### 시스템 문서
- [Docker 컨테이너화 가이드](PHASE4_DOCKER_COMPLETE.md)
- [CI/CD 파이프라인 가이드](PHASE4_CICD_COMPLETE.md)
- [샘플 데이터 생성 가이드](SAMPLE_DATA_COMMAND.md)
- [배포 체크리스트](DEPLOYMENT_CHECKLIST.md)

### 기술 문서
- [AI 서비스 통합 가이드](AI_SERVICE_GUIDE.md)
- [빠른 시작 가이드](QUICK_START.md)
- [API 문서](backend/docs/API.md)
- [LLM 서비스 가이드](backend/apps/spc/services/llm_service.py)
- [시계열 분석 가이드](backend/apps/spc/services/time_series_analysis.py)

---

## 라이선스 (License)

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 연락처 (Contact)

- **Project Maintainer**: SPC Quality Team
- **Email**: support@spc-quality.com
- **Issues**: [GitHub Issues](https://github.com/username/spc-scheduler/issues)

---

**마지막 업데이트**: 2026-01-14
**버전**: 1.0.0
