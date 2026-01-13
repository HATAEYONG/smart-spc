# 배포 가이드

이 문서는 Online APS-CPS Scheduler를 프로덕션 환경에 배포하는 방법을 설명합니다.

## 📋 목차

- [사전 요구사항](#사전-요구사항)
- [프로덕션 배포](#프로덕션-배포)
- [환경 변수 설정](#환경-변수-설정)
- [Docker Compose 배포](#docker-compose-배포)
- [수동 배포](#수동-배포)
- [모니터링 및 로깅](#모니터링-및-로깅)
- [백업 및 복구](#백업-및-복구)
- [트러블슈팅](#트러블슈팅)

## 🔧 사전 요구사항

### 서버 요구사항

**최소 사양:**
- CPU: 4 cores
- RAM: 8GB
- Disk: 50GB SSD
- OS: Ubuntu 20.04 LTS 이상 또는 CentOS 8 이상

**권장 사양:**
- CPU: 8 cores
- RAM: 16GB
- Disk: 100GB SSD
- OS: Ubuntu 22.04 LTS

### 소프트웨어 요구사항

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- (선택) Nginx for SSL termination

### 포트 요구사항

- 80 (HTTP)
- 443 (HTTPS)
- 5432 (PostgreSQL - 내부 네트워크만)

## 🚀 프로덕션 배포

### 1. 서버 준비

```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 로그아웃 후 재로그인
```

### 2. 프로젝트 클론

```bash
# 배포 디렉토리 생성
sudo mkdir -p /opt/aps-cps-scheduler
sudo chown $USER:$USER /opt/aps-cps-scheduler
cd /opt/aps-cps-scheduler

# 코드 클론
git clone https://github.com/your-org/online-aps-cps-scheduler.git .
```

### 3. 환경 변수 설정

```bash
# 데이터베이스 환경 변수
cp .env.db.example .env.db
nano .env.db
# POSTGRES_PASSWORD를 강력한 비밀번호로 변경

# 백엔드 환경 변수
cp backend/.env.production.example backend/.env.production
nano backend/.env.production
# SECRET_KEY, DB_PASSWORD, ALLOWED_HOSTS 설정

# 워커 환경 변수
cp worker/.env.production.example worker/.env.production
nano worker/.env.production
# APS_DSN 비밀번호 업데이트

# 프론트엔드 환경 변수
cp frontend/.env.production.example frontend/.env.production
nano frontend/.env.production
# VITE_API_URL 설정
```

### 4. SECRET_KEY 생성

```bash
# Django SECRET_KEY 생성
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# 생성된 키를 backend/.env.production의 SECRET_KEY에 입력
```

### 5. SSL 인증서 설정 (선택사항)

```bash
# Let's Encrypt 인증서 생성
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# 인증서를 nginx 폴더로 복사
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
sudo chown -R $USER:$USER nginx/ssl
```

### 6. 배포 실행

```bash
# 이미지 빌드 및 컨테이너 시작
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f
```

### 7. 초기 데이터베이스 설정

```bash
# 마이그레이션 실행
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# 슈퍼유저 생성
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# Static 파일 수집 (이미 Dockerfile에서 실행되지만 확인용)
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

### 8. 헬스 체크

```bash
# 백엔드 헬스 체크
curl http://localhost/api/health/

# 프론트엔드 헬스 체크
curl http://localhost/health

# 모든 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps
```

## 🔐 환경 변수 설정

### 필수 환경 변수

#### Backend (.env.production)

```bash
# 보안 - 반드시 변경!
SECRET_KEY=<강력한-랜덤-키>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# 데이터베이스
DB_NAME=aps_cps_db
DB_USER=apsuser
DB_PASSWORD=<강력한-비밀번호>
DB_HOST=db
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# 보안 설정
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

#### Worker (.env.production)

```bash
# 데이터베이스
APS_DSN=postgresql://apsuser:<비밀번호>@db:5432/aps_cps_db

# 설정
APS_GRAPH_DEPTH=3
APS_GATE_UTIL_THRESHOLD=0.85
APS_GATE_DELAY_THRESHOLD=120
```

#### Database (.env.db)

```bash
POSTGRES_DB=aps_cps_db
POSTGRES_USER=apsuser
POSTGRES_PASSWORD=<강력한-비밀번호>
```

## 🐳 Docker Compose 배포

### 서비스 관리 명령어

```bash
# 서비스 시작
docker-compose -f docker-compose.prod.yml up -d

# 서비스 중지
docker-compose -f docker-compose.prod.yml down

# 서비스 재시작
docker-compose -f docker-compose.prod.yml restart

# 특정 서비스만 재시작
docker-compose -f docker-compose.prod.yml restart backend

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f worker

# 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 리소스 사용량 확인
docker stats
```

### 업데이트 배포

```bash
# 최신 코드 가져오기
git pull origin main

# 이미지 재빌드
docker-compose -f docker-compose.prod.yml build

# 무중단 배포 (새 컨테이너로 교체)
docker-compose -f docker-compose.prod.yml up -d --force-recreate

# 마이그레이션 실행
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# 사용하지 않는 이미지 정리
docker system prune -af
```

## 🛠️ 수동 배포

Docker를 사용하지 않는 경우:

### Backend

```bash
cd backend

# 가상환경 생성
python -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 로드
export $(cat .env.production | xargs)

# 마이그레이션
python manage.py migrate

# Static 파일 수집
python manage.py collectstatic --noinput

# Gunicorn으로 실행
gunicorn --bind 0.0.0.0:8000 --workers 4 backend.wsgi:application
```

### Worker

```bash
cd worker

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 로드
export $(cat .env.production | xargs)

# Worker 실행
python event_listener.py
```

### Frontend

```bash
cd frontend

# 의존성 설치
npm install

# 프로덕션 빌드
npm run build

# Nginx로 서빙 (dist 폴더를 nginx root로)
sudo cp -r dist/* /var/www/html/
```

## 📊 모니터링 및 로깅

### 로그 수집

```bash
# 모든 서비스 로그
docker-compose -f docker-compose.prod.yml logs -f

# 특정 시간 이후 로그
docker-compose -f docker-compose.prod.yml logs --since 1h

# 로그를 파일로 저장
docker-compose -f docker-compose.prod.yml logs > logs.txt
```

### 로그 로테이션

`/etc/docker/daemon.json`:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### 헬스 체크 모니터링

```bash
# 간단한 모니터링 스크립트
cat << 'EOF' > /opt/health-check.sh
#!/bin/bash
curl -f http://localhost/api/health/ || echo "Backend unhealthy"
curl -f http://localhost/health || echo "Frontend unhealthy"
EOF

chmod +x /opt/health-check.sh

# Cron으로 5분마다 실행
echo "*/5 * * * * /opt/health-check.sh >> /var/log/health-check.log 2>&1" | crontab -
```

## 💾 백업 및 복구

### 데이터베이스 백업

```bash
# 백업 생성
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U apsuser aps_cps_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 정기 백업 스크립트
cat << 'EOF' > /opt/backup.sh
#!/bin/bash
BACKUP_DIR="/opt/backups"
mkdir -p $BACKUP_DIR
cd /opt/aps-cps-scheduler
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U apsuser aps_cps_db | gzip > $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql.gz
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
EOF

chmod +x /opt/backup.sh

# Cron으로 매일 02:00에 백업
echo "0 2 * * * /opt/backup.sh" | crontab -
```

### 데이터베이스 복구

```bash
# 백업에서 복구
cat backup_20250129.sql | docker-compose -f docker-compose.prod.yml exec -T db psql -U apsuser aps_cps_db

# gzip 압축된 백업 복구
gunzip -c backup_20250129.sql.gz | docker-compose -f docker-compose.prod.yml exec -T db psql -U apsuser aps_cps_db
```

## 🔥 트러블슈팅

### 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker-compose -f docker-compose.prod.yml logs <service-name>

# 컨테이너 재시작
docker-compose -f docker-compose.prod.yml restart <service-name>

# 강제 재생성
docker-compose -f docker-compose.prod.yml up -d --force-recreate <service-name>
```

### 데이터베이스 연결 오류

```bash
# PostgreSQL 상태 확인
docker-compose -f docker-compose.prod.yml exec db pg_isready -U apsuser

# 연결 테스트
docker-compose -f docker-compose.prod.yml exec backend python manage.py dbshell
```

### Nginx 502 Bad Gateway

```bash
# Backend 상태 확인
docker-compose -f docker-compose.prod.yml ps backend

# Nginx 설정 테스트
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Nginx 재시작
docker-compose -f docker-compose.prod.yml restart nginx
```

### 디스크 공간 부족

```bash
# Docker 디스크 사용량 확인
docker system df

# 사용하지 않는 리소스 정리
docker system prune -af --volumes

# 로그 파일 정리
find /var/lib/docker/containers -name "*.log" -exec truncate -s 0 {} \;
```

### 메모리 부족

```bash
# 메모리 사용량 확인
docker stats

# Gunicorn worker 수 줄이기 (backend/.env.production)
GUNICORN_WORKERS=2

# 서비스 재시작
docker-compose -f docker-compose.prod.yml restart backend
```

## 🔄 롤백 절차

```bash
# 1. 이전 버전으로 코드 되돌리기
git log --oneline  # 커밋 해시 확인
git checkout <previous-commit-hash>

# 2. 이미지 재빌드
docker-compose -f docker-compose.prod.yml build

# 3. 서비스 재시작
docker-compose -f docker-compose.prod.yml up -d --force-recreate

# 4. 마이그레이션 롤백 (필요시)
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate <app_name> <migration_number>
```

## 📈 성능 최적화

### Gunicorn 설정

```bash
# backend/.env.production
GUNICORN_WORKERS=4  # CPU 코어 수 * 2 + 1
GUNICORN_TIMEOUT=120
GUNICORN_KEEPALIVE=5
```

### PostgreSQL 튜닝

```bash
# .env.db
POSTGRES_SHARED_BUFFERS=256MB
POSTGRES_EFFECTIVE_CACHE_SIZE=1GB
POSTGRES_WORK_MEM=16MB
```

### Nginx 캐싱

```nginx
# nginx/nginx.conf에 추가
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;

location /api/ {
    proxy_cache my_cache;
    proxy_cache_valid 200 5m;
    # ...
}
```

## 🔗 추가 리소스

- [Docker 문서](https://docs.docker.com/)
- [Django 배포 체크리스트](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Nginx 설정 가이드](https://nginx.org/en/docs/)
- [PostgreSQL 튜닝](https://wiki.postgresql.org/wiki/Performance_Optimization)

---

**버전**: 1.0.0
**최종 업데이트**: 2025-12-29
