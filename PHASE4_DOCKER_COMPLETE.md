# Phase 4: Docker 컨테이너화 완료

## 개요

Phase 4: 아키텍처 현대화 - Docker 컨테이너화 구현 완료

전체 스택을 Docker로 컨테이너화하여 개발/운영 환경 일관성 확보 및 배포 자동화

## 구현 완료 기능

### 1. Backend Dockerfile (`backend/Dockerfile`)

#### Multi-Stage Build
- **Stage 1 (base)**: Python 3.11-slim 기본 이미지
- **Stage 2 (dependencies)**: Python 패키지 의존성 설치
- **Stage 3 (development)**: 개발 환경 (django-debug-toolbar, ipython)
- **Stage 4 (production)**: 프로덕션 환경 (Gunicorn WSGI 서버)

```dockerfile
# Development build
docker build --target development -t spc-backend:dev .

# Production build
docker build --target production -t spc-backend:prod .
```

#### 최적화 사항
- **환경 변수**: PYTHONDONTWRITEBYTECODE, PYTHONUNBUFFERED
- **시스템 패키지**: gcc, g++, postgresql-client, curl
- **Health Check**: 30초 간격 health check
- **Non-root User**: 프로덕션에서 보안 강화
- **Gunicorn**: 4 workers, 2 threads, 120초 timeout

### 2. Frontend Dockerfile (`frontend/Dockerfile`)

#### Multi-Stage Build
- **Stage 1 (dependencies)**: npm 의존성 설치 (production만)
- **Stage 2 (build)**: Vite 빌드
- **Stage 3 (development)**: 개발 서버 (Vite Dev Server)
- **Stage 4 (build-production)**: 프로덕션 빌드
- **Stage 5 (production)**: Nginx 웹서버

```dockerfile
# Development build
docker build --target development -t spc-frontend:dev .

# Production build
docker build --target production -t spc-frontend:prod .
```

#### Nginx 설정 (`frontend/nginx.conf`)
- **Gzip 압축**: JS, CSS, JSON, HTML
- **보안 헤더**: X-Frame-Options, X-Content-Type-Options, X-XSS-Protection
- **API/WebSocket Proxy**: 백엔드 연동 (선택적)
- **정적 파일 캐싱**: 1년 만료
- **SPA Fallback**: 모든 라우트를 index.html로
- **Service Worker/Manifest**: 캐시 방지

### 3. Docker Compose (`docker-compose.yml`)

#### 서비스 구성 (9개 서비스)

| 서비스 | 설명 | 포트 |
|--------|------|------|
| **db** | PostgreSQL 15 Alpine | 5432 |
| **redis** | Redis 7 Alpine (Cache + Broker) | 6379 |
| **backend** | Django Backend (Django + DRF) | 8000 |
| **celery-worker** | Celery Worker (비동기 작업) | - |
| **celery-beat** | Celery Beat (주기적 작업 스케줄러) | - |
| **flower** | Celery 모니터링 대시보드 | 5555 |
| **frontend** | React + Vite (개발 서버) | 5173 |
| **nginx** | Nginx Reverse Proxy (프로덕션) | 80, 443 |
| **worker** | APS Worker (기존) | - |

#### 네트워크 & 볼륨
- **Network**: `spc-network` (bridge)
- **Volumes**:
  - `postgres_data`: PostgreSQL 데이터
  - `redis_data`: Redis AOF 파일
  - `backend_static`: Django 정적 파일
  - `backend_media`: Django 미디어 파일

#### Health Checks
- **PostgreSQL**: `pg_isready`
- **Redis**: `redis-cli ping`
- **Backend**: HTTP `/api/health/`
- **Frontend**: HTTP `/`

#### 환경 변수 지원
```yaml
# .env 파일에서 환경 변수 로드
environment:
  DB_NAME: ${POSTGRES_DB:-spc_db}
  DB_USER: ${POSTGRES_USER:-postgres}
  DB_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
  REDIS_HOST: redis
  REDIS_PORT: 6379
  SECRET_KEY: ${DJANGO_SECRET_KEY}
  DEBUG: ${DEBUG:-True}
```

### 4. 환경 변수 (`.env.example`)

#### 필수 설정
```bash
# Build Target
BUILD_TARGET=development

# Database
POSTGRES_DB=spc_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Django
SECRET_KEY=django-insecure-change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,backend

# LLM (선택적)
LLM_PROVIDER=demo
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

#### 포트 설정
```bash
BACKEND_PORT=8000
FRONTEND_PORT=5173
FLOWER_PORT=5555
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443
POSTGRES_PORT=5432
REDIS_PORT=6379
```

## 사용 방법

### 1. 개발 환경 시작

```bash
# .env 파일 복사
cp .env.example .env

# 환경 변수 편집 (선택사항)
# vi .env

# 모든 서비스 시작
docker-compose up -d

# 로그 보기
docker-compose logs -f backend

# 특정 서비스만 시작
docker-compose up -d db redis backend
```

### 2. 서비스 확인

```bash
# 실행 중인 컨테이너 확인
docker-compose ps

# 컨테이너 상태 확인
docker-compose top

# 리소스 사용량
docker stats
```

### 3. 데이터베이스 초기화

```bash
# Django 마이그레이션
docker-compose exec backend python manage.py migrate

# 슈퍼유저 생성
docker-compose exec backend python manage.py createsuperuser

# 정적 파일 수집
docker-compose exec backend python manage.py collectstatic --noinput
```

### 4. Celery 작업 확인

```bash
# Flower 대시보드 접속
# http://localhost:5555

# Celery Worker 로그
docker-compose logs -f celery-worker

# Celery Beat 로그
docker-compose logs -f celery-beat

# 등록된 작업 확인
docker-compose exec backend celery -A config inspect registered
```

### 5. 프로덕션 빌드

```bash
# 프로덕션 타겟으로 빌드
export BUILD_TARGET=production
docker-compose build

# 프로덕션 모드 시작
docker-compose --profile production up -d

# Nginx Reverse Proxy 활성화
docker-compose --profile production up -d nginx
```

### 6. 서비스 중지

```bash
# 모든 서비스 중지
docker-compose down

# 볼륨 포함하여 모두 삭제
docker-compose down -v

# 특정 서비스만 중지
docker-compose stop backend
```

## 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx (Production)                   │
│                  Port: 80, 443                          │
└──────────────────────────┬──────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                                      │
┌───────▼────────┐    ┌──────────▼─────────┐  │
│   Frontend     │    │     Backend        │  │
│  (React/Vite)  │    │   (Django/DRF)     │  │
│   Port: 5173   │    │     Port: 8000     │  │
└───────┬────────┘    └──────────┬─────────┘  │
        │                       │             │
        │              ┌─────────┼─────────┐  │
        │              │                   │  │
        │         ┌────▼─────┐      ┌─────▼──▼────┐
        │         │PostgreSQL│      │    Redis    │
        │         │  Port:   │      │   Port:     │
        │         │   5432   │      │   6379      │
        │         └──────────┘      └──────┬──────┘
        │                                  │
        │                     ┌─────────────┼─────────────┐
        │                     │                           │
        │              ┌──────▼──────┐          ┌────────▼────────┐
        │              │Celery Worker│          │  Celery Beat    │
        │              └─────────────┘          └─────────────────┘
        │                     │
        │              ┌──────▼──────┐
        └──────────────│    Flower    │
                       │  Port: 5555 │
                       └─────────────┘
```

## 볼륨 마운트

### 개발 모드
```yaml
volumes:
  - ./backend:/app              # 코드 핫 리로드
  - backend_static:/app/staticfiles
  - backend_media:/app/media
  - ./frontend:/app             # 코드 핫 리로드
  - /app/node_modules           # node_modules 보존
```

### 프로덕션 모드
```yaml
volumes:
  - backend_static:/var/www/static:ro
  - backend_media:/var/www/media:ro
```

## 네트워크 구성

```yaml
networks:
  spc-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 서비스 간 통신
- **Backend → DB**: `db:5432`
- **Backend → Redis**: `redis:6379`
- **Frontend → Backend**: `backend:8000` (또는 localhost:8000)
- **Nginx → Backend**: `backend:8000`
- **Nginx → Frontend**: built static files

## Health Checks

### PostgreSQL
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres -d spc_db"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### Redis
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### Backend
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/health/"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## 로그 관리

### 로그 확인
```bash
# 모든 서비스 로그
docker-compose logs

# 특정 서비스 로그
docker-compose logs backend

# 실시간 로그 추적
docker-compose logs -f backend

# 최근 100줄
docker-compose logs --tail=100 backend
```

### 로그 드라이버 (선택사항)
```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 성능 최적화

### 1. 빌드 캐싱
```dockerfile
# 의존성 먼저 복사 (캐시 활용)
COPY requirements.txt .
RUN pip install -r requirements.txt

# 그 다음 코드 복사
COPY . .
```

### 2. Multi-Stage Build
- 불필요한 레이어 제거
- 최종 이미지 크기 감소
- 개발/프로덕션 분리

### 3. 볼륨 캐싱
```yaml
volumes:
  - /app/node_modules  # node_modules를 컨테이너 내부 보존
```

### 4. 네트워크 최적화
- Bridge 네트워크 사용
- 서비스 디스커버리 자동화
- DNS 캐싱

## 보안 고려사항

### 1. 비밀 정보 관리
```bash
# .env 파일은 .gitignore에 추가
# .env.example만 커밋

# Docker Secrets 사용 (프로덕션)
echo "your-secret-key" | docker secret create db_password -
```

### 2. Non-root User
```dockerfile
# 프로덕션에서 non-root 사용자로 실행
RUN useradd -m -u 1000 appuser
USER appuser
```

### 3. 읽기 전용 파일시스템
```yaml
services:
  nginx:
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
```

### 4. 최소 권한
```yaml
# 필요한 포트만 노출
ports:
  - "8000:8000"
```

## 문제 해결

### 1. 컨테이너가 시작하지 않음
```bash
# 로그 확인
docker-compose logs backend

# 컨테이너 상태 확인
docker-compose ps -a

# 재시작
docker-compose restart backend
```

### 2. 데이터베이스 연결 실패
```bash
# DB health check 확인
docker-compose exec db pg_isready

# DB 로그 확인
docker-compose logs db

# 마이그레이션 재실행
docker-compose exec backend python manage.py migrate
```

### 3. Redis 연결 실패
```bash
# Redis health check 확인
docker-compose exec redis redis-cli ping

# Redis 로그 확인
docker-compose logs redis
```

### 4. 포트 충돌
```bash
# .env에서 포트 변경
BACKEND_PORT=8001
FRONTEND_PORT=5174

# 또는 기존 프로세스 중지
lsof -ti:8000 | xargs kill
```

### 5. 디스크 공간 부족
```bash
# 사용 중인 디스크 확인
docker system df

# 불필요한 컨테이너/이미지 삭제
docker system prune -a

# dangling 이미지 삭제
docker image prune
```

## CI/CD 통합

### GitHub Actions 예시
```yaml
name: Docker Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Backend
        run: docker build -t spc-backend ./backend

      - name: Build Frontend
        run: docker build -t spc-frontend ./frontend

      - name: Login to Docker Hub
        run: docker login -u ${{ secrets.DOCKER_USER }} -p ${{ secrets.DOCKER_PASSWORD }}

      - name: Push Images
        run: |
          docker push spc-backend:latest
          docker push spc-frontend:latest
```

## 모니터링

### 1. Container Stats
```bash
docker stats
```

### 2. Flower (Celery Monitoring)
- URL: http://localhost:5555
- 기능:
  - 작업 실행 현황
  - Worker 상태
  - 작업 실행 시간
  - 실패한 작업 확인

### 3. Health Check API
```bash
# Backend Health Check
curl http://localhost:8000/api/health/

# 응답 예시
{"status": "healthy", "database": "connected", "redis": "connected"}
```

## 배포 전략

### 1. Rolling Update
```bash
# 새 이미지 빌드
docker-compose build backend

# zero-downtime 배포
docker-compose up -d --no-deps --build backend
```

### 2. Blue-Green Deployment
```bash
# Green 환경 시작
docker-compose -f docker-compose.green.yml up -d

# 트래픽 전환 (Nginx 설정 변경)
```

### 3. Canary Deployment
```bash
# 일부 트래픽만 새 버전으로
# Nginx에서 split routing 설정
```

## 다음 단계: CI/CD 파이프라인

Phase 4 마지막 작업:
1. **GitHub Actions Workflow**: CI/CD 자동화
2. **Automated Testing**: Unit Tests, Integration Tests
3. **Deployment Automation**: Staging/Production 배포
4. **Monitoring & Alerting**: Prometheus, Grafana

## 파일 목록

### 생성/수정된 파일
- `backend/Dockerfile` (Multi-stage build)
- `frontend/Dockerfile` (Multi-stage build)
- `frontend/nginx.conf` (Nginx 설정)
- `docker-compose.yml` (전체 스택 오케스트레이션)
- `.env.example` (환경 변수 템플릿)

## 참고 자료

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**완료일시**: 2026-01-11
**상태**: ✅ Docker 컨테이너화 완료
