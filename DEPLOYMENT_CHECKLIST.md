# 배포 체크리스트 (Deployment Checklist)

**SPC 품질관리 시스템 프로덕션 배포 가이드**

---

## 📋 목차

1. [사전 준비](#1-사전-준비-pre-deployment)
2. [서버 환경 설정](#2-서버-환경-설정-server-setup)
3. [데이터베이스 설정](#3-데이터베이스-설정-database-setup)
4. [애플리케이션 배포](#4-애플리케이션-배포-application-deployment)
5. [CI/CD 파이프라인](#5-cicd-파이프라인-cicd-pipeline)
6. [배포 후 검증](#6-배포-후-검증-post-deployment)
7. [모니터링 설정](#7-모니터링-설정-monitoring)
8. [보안 검사](#8-보안-검사-security-check)

---

## 1. 사전 준비 (Pre-Deployment)

### 1.1 코드 검토

- [ ] **코드 리뷰 완료**
  - [ ] 모든 PR이 리뷰되고 승인됨
  - [ ] Main 브랜치에 병합 완료
  - [ ] 충돌(conflicts) 해결됨

- [ ] **테스트 통과**
  - [ ] Backend 테스트 통과 (pytest)
  - [ ] Frontend 테스트 통과 (vitest)
  - [ ] E2E 테스트 통과 (Playwright)
  - [ ] 커버리지 80% 이상

- [ ] **문서화**
  - [ ] README.md 업데이트
  - [ ] CHANGELOG.md 업데이트
  - [ ] API 문서 업데이트

### 1.2 환경 변수 확인

- [ ] **`.env` 파일 준비**
  ```bash
  # 필수 환경 변수 체크리스트
  - [ ] SECRET_KEY (강력한 랜덤 키)
  - [ ] DEBUG=False
  - [ ] DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
  - [ ] REDIS_HOST, REDIS_PORT
  - [ ] ALLOWED_HOSTS (도메인 등록)
  - [ ] CORS_ALLOWED_ORIGINS (프론트엔드 도메인)
  - [ ] LLM_PROVIDER (demo/openai/anthropic)
  - [ ] OPENAI_API_KEY 또는 ANTHROPIC_API_KEY
  - [ ] EMAIL_HOST, EMAIL_PORT (알림용)
  ```

- [ ] **보안 키 생성**
  ```bash
  # Django SECRET_KEY 생성
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

### 1.3 리소스 계획

- [ ] **서버 사양**
  - [ ] CPU: 4코어 이상 권장
  - [ ] RAM: 8GB 이상 권장
  - [ ] Disk: 50GB 이상 (SSD 권장)
  - [ ] Network: 100Mbps 이상

- [ ] **데이터베이스**
  - [ ] PostgreSQL 15+ 설치 확인
  - [ ] 스토리지: 20GB 이상
  - [ ] 백업 공간: 50GB 이상

- [ ] **Redis**
  - [ ] Redis 7+ 설치 확인
  - [ ] 메모리: 2GB 이상 권장

---

## 2. 서버 환경 설정 (Server Setup)

### 2.1 운영체제

- [ ] **OS 업데이트**
  ```bash
  # Ubuntu/Debian
  sudo apt update && sudo apt upgrade -y

  # CentOS/RHEL
  sudo yum update -y
  ```

- [ ] **타임존 설정**
  ```bash
  sudo timedatectl set-timezone Asia/Seoul
  ```

- [ ] **필수 패키지 설치**
  ```bash
  # Ubuntu/Debian
  sudo apt install -y curl wget git vim ufw fail2ban

  # Python 3.11+
  sudo apt install -y python3.11 python3.11-venv python3-pip

  # Node.js 18+
  curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
  sudo apt install -y nodejs

  # Docker
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  sudo usermod -aG docker $USER

  # Docker Compose
  sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  ```

### 2.2 방화벽 설정

- [ ] **UFW (Uncomplicated Firewall)**
  ```bash
  # 기본 정책
  sudo ufw default deny incoming
  sudo ufw default allow outgoing

  # 허용할 포트
  sudo ufw allow 22/tcp    # SSH
  sudo ufw allow 80/tcp    # HTTP
  sudo ufw allow 443/tcp   # HTTPS

  # Docker Compose 포트 (선택사항)
  sudo ufw allow 8000/tcp  # Backend API (개발용)
  sudo ufw allow 5173/tcp  # Frontend (개발용)

  # 방화벽 활성화
  sudo ufw enable
  sudo ufw status
  ```

### 2.3 사용자 및 권한

- [ ] **전용 배포 사용자 생성**
  ```bash
  # 사용자 생성
  sudo useradd -m -s /bin/bash deploy

  # sudo 권한 부여
  sudo usermod -aG sudo deploy

  # docker 그룹에 추가
  sudo usermod -aG docker deploy

  # SSH 키 설정
  sudo su - deploy
  mkdir -p ~/.ssh
  chmod 700 ~/.ssh
  # 로컬에서 SSH 공개키 복사
  ```

---

## 3. 데이터베이스 설정 (Database Setup)

### 3.1 PostgreSQL 설치

- [ ] **PostgreSQL 15 설치**
  ```bash
  # Ubuntu/Debian
  sudo apt install -y postgresql-15 postgresql-contrib-15

  # 서비스 시작
  sudo systemctl start postgresql
  sudo systemctl enable postgresql
  ```

- [ ] **데이터베이스 및 사용자 생성**
  ```bash
  # PostgreSQL 접속
  sudo -u postgres psql

  # 데이터베이스 생성
  CREATE DATABASE spc_db;

  # 사용자 생성 및 권한 부여
  CREATE USER spc_user WITH PASSWORD 'strong_password_here';
  GRANT ALL PRIVILEGES ON DATABASE spc_db TO spc_user;

  # 종료
  \q
  ```

### 3.2 PostgreSQL 성능 최적화

- [ ] **`postgresql.conf` 설정**
  ```ini
  # /etc/postgresql/15/main/postgresql.conf

  # 메모리 설정 (서버 RAM에 따라 조정)
  shared_buffers = 2GB              # RAM의 25%
  effective_cache_size = 6GB        # RAM의 50-75%
  maintenance_work_mem = 512MB
  work_mem = 16MB

  # 연결 설정
  max_connections = 100

  # WAL 설정
  wal_buffers = 16MB
  checkpoint_completion_target = 0.9

  # 로깅
  logging_collector = on
  log_directory = 'pg_log'
  log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
  log_statement = 'mod'  # DDL과 변경 사항만 로깅
  ```

- [ ] **PostgreSQL 재시작**
  ```bash
  sudo systemctl restart postgresql
  ```

### 3.3 백업 설정

- [ ] **자동 백업 스크립트**
  ```bash
  # /usr/local/bin/backup_postgres.sh
  #!/bin/bash
  BACKUP_DIR="/backups/postgresql"
  DATE=$(date +"%Y%m%d_%H%M%S")
  mkdir -p $BACKUP_DIR

  pg_dump -U spc_user -h localhost spc_db | gzip > $BACKUP_DIR/spc_db_$DATE.sql.gz

  # 7일 이상 된 백업 삭제
  find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
  ```

- [ ] **크론 작업 등록**
  ```bash
  # 매일 새벽 2시 백업
  crontab -e
  0 2 * * * /usr/local/bin/backup_postgres.sh
  ```

---

## 4. 애플리케이션 배포 (Application Deployment)

### 4.1 소스 코드 배포

- [ ] **저장소 복제**
  ```bash
  sudo mkdir -p /opt/spc-scheduler
  sudo chown deploy:deploy /opt/spc-scheduler
  cd /opt/spc-scheduler

  # Git 복제
  git clone https://github.com/username/spc-scheduler.git .
  git checkout main  # 또는 specific tag
  ```

### 4.2 Docker Compose 배포

- [ ] **`.env` 파일 생성**
  ```bash
  cd /opt/spc-scheduler
  cp .env.example .env
  vim .env  # 환경 변수 편집
  ```

- [ ] **Docker 이미지 빌드**
  ```bash
  # 프로덕션 타겟으로 빌드
  export BUILD_TARGET=production
  docker-compose build

  # 이미지 확인
  docker images | grep spc
  ```

- [ ] **컨테이너 시작**
  ```bash
  # 프로덕션 프로필로 시작
  docker-compose --profile production up -d

  # 컨테이너 상태 확인
  docker-compose ps
  ```

### 4.3 데이터베이스 마이그레이션

- [ ] **마이그레이션 실행**
  ```bash
  docker-compose exec backend python manage.py migrate --noinput

  # 마이그레이션 확인
  docker-compose exec backend python manage.py showmigrations
  ```

- [ ] **슈퍼유저 생성**
  ```bash
  docker-compose exec backend python manage.py createsuperuser
  ```

- [ ] **정적 파일 수집**
  ```bash
  docker-compose exec backend python manage.py collectstatic --noinput --clear
  ```

### 4.4 샘플 데이터 (선택사항)

- [ ] **샘플 데이터 생성**
  ```bash
  docker-compose exec backend python manage.py create_sample_data --products=5 --days=30
  ```

---

## 5. CI/CD 파이프라인 (CI/CD Pipeline)

### 5.1 GitHub Actions 설정

- [ ] **Secrets 설정**
  - [ ] `STAGING_HOST`: 스테이징 서버 호스트
  - [ ] `STAGING_USER`: 배포 사용자
  - [ ] `STAGING_SSH_KEY`: SSH 개인키
  - [ ] `PRODUCTION_HOST`: 프로덕션 서버 호스트
  - [ ] `PRODUCTION_USER`: 배포 사용자
  - [ ] `PRODUCTION_SSH_KEY`: SSH 개인키
  - [ ] `SLACK_WEBHOOK`: Slack 알림용 (선택사항)

### 5.2 GitHub Environments

- [ ] **Staging Environment**
  - [ ] Name: `staging`
  - [ ] URL: `https://staging.spc.example.com`
  - [ ] Protection rules: 없음

- [ ] **Production Environment**
  - [ ] Name: `production`
  - [ ] URL: `https://spc.example.com`
  - [ ] Protection rules:
    - [ ] Required reviewers: 1명 이상
    - [ ] Wait timer: 0분
    - [ ] Deployment branches: main만 허용

### 5.3 CI 파이프라인 확인

- [ ] **CI 테스트 통과**
  - [ ] Backend tests 통과
  - [ ] Frontend tests 통과
  - [ ] Docker build 성공
  - [ ] Code quality checks 통과
  - [ ] Security scans 통과

### 5.4 CD 파이프라인 실행

- [ ] **수동 배포 테스트**
  1. GitHub Repository → Actions → CD - Continuous Deployment
  2. "Run workflow" 클릭
  3. Branch: main 선택
  4. Environment: staging 선택
  5. "Run workflow" 클릭

- [ ] **배포 로그 확인**
  - GitHub Actions 로그 확인
  - 서버 SSH 접속 후 컨테이너 상태 확인

---

## 6. 배포 후 검증 (Post-Deployment)

### 6.1 Health Checks

- [ ] **Backend Health Check**
  ```bash
  curl http://localhost:8000/api/health/
  # Expected: {"status": "healthy", "database": "connected", "redis": "connected"}
  ```

- [ ] **Database Health Check**
  ```bash
  curl http://localhost:8000/api/health/db/
  # Expected: {"status": "connected", "database": "spc_db"}
  ```

- [ ] **Redis Health Check**
  ```bash
  curl http://localhost:8000/api/health/redis/
  # Expected: {"status": "connected", "redis": "redis://redis:6379/0"}
  ```

### 6.2 기능 테스트

- [ ] **로그인 테스트**
  - [ ] JWT 발급 확인
  - [ ] Token refresh 확인
  - [ ] 로그아웃 확인

- [ ] **API 엔드포인트 테스트**
  - [ ] 제품 목록 조회
  - [ ] 측정 데이터 생성
  - [ ] 관리도 조회
  - [ ] 공정능력 분석

- [ ] **AI 기능 테스트**
  - [ ] LLM 분석 요청 (demo 모드)
  - [ ] 시계열 예측

- [ ] **Celery 작업 테스트**
  ```bash
  # Flower 대시보드 접속
  http://localhost:5555

  # 작업 등록 확인
  docker-compose exec backend python manage.py shell
  >>> from apps.spc.tasks import generate_daily_report
  >>> generate_daily_report.delay()
  ```

### 6.3 성능 테스트

- [ ] **로드 테스트**
  - [ ] 100 동시 사용자 시뮬레이션
  - [ ] 응답 시간 < 500ms
  - [ ] 에러율 < 1%

- [ ] **데이터베이스 쿼리**
  - [ ] 느린 쿼리 확인 (> 100ms)
  - [ ] 인덱스 최적화

---

## 7. 모니터링 설정 (Monitoring)

### 7.1 로그 관리

- [ ] **로그 회전 설정**
  ```yaml
  # docker-compose.yml
  services:
    backend:
      logging:
        driver: "json-file"
        options:
          max-size: "10m"
          max-file: "3"
  ```

- [ ] **로그 집계 (선택사항)**
  - [ ] ELK Stack (Elasticsearch, Logstash, Kibana)
  - [ ] 또는 Grafana Loki
  - [ ] 또는 CloudWatch (AWS)

### 7.2 메트릭 수집

- [ ] **Prometheus & Grafana** (선택사항)
  ```yaml
  # docker-compose.monitoring.yml
  services:
    prometheus:
      image: prom/prometheus
      volumes:
        - ./prometheus.yml:/etc/prometheus/prometheus.yml

    grafana:
      image: grafana/grafana
      environment:
        - GF_SECURITY_ADMIN_PASSWORD=admin
  ```

### 7.3 알림 설정

- [ ] **Slack 알림**
  - [ ] Slack Webhook URL 설정
  - [ ] `.github/workflows/cd.yml`에서 알림 활성화

- [ ] **이메일 알림**
  - [ ] SMTP 설정
  - [ ] Django 이메일 백엔드 설정
  - [ ] Critical alert 이메일 발송 테스트

### 7.4 정기 점검

- [ ] **일일 점검**
  - [ ] 디스크 사용량 확인
  - [ ] CPU/Memory 사용량 확인
  - [ ] 에러 로그 확인

- [ ] **주간 점검**
  - [ ] 백업 확인
  - [ ] 성능 메트릭 리뷰
  - [ ] 보안 패치 확인

- [ ] **월간 점검**
  - [ ] 용량 계획 수립
  - [ ] 비용 최적화 검토
  - [ ] 재해 복구 훈련

---

## 8. 보안 검사 (Security Check)

### 8.1 SSL/TLS 설정

- [ ] **Let's Encrypt 인증서 발급**
  ```bash
  # Certbot 설치
  sudo apt install certbot python3-certbot-nginx

  # 인증서 발급
  sudo certbot --nginx -d spc.example.com

  # 자동 갱신 설정
  sudo certbot renew --dry-run
  ```

- [ ] **HTTPS 강제**
  ```nginx
  # nginx.conf
  server {
      listen 80;
      server_name spc.example.com;
      return 301 https://$server_name$request_uri;
  }
  ```

### 8.2 보안 헤더 설정

- [ ] **Nginx 보안 헤더**
  ```nginx
  # nginx.conf
  add_header X-Frame-Options "SAMEORIGIN" always;
  add_header X-Content-Type-Options "nosniff" always;
  add_header X-XSS-Protection "1; mode=block" always;
  add_header Referrer-Policy "no-referrer-when-downgrade" always;
  add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
  ```

### 8.3 취약점 스캔

- [ ] **Trivy 스캔**
  ```bash
  # 이미지 스캔
  trivy image spc-backend:latest
  trivy image spc-frontend:latest

  # 파일 시스템 스캔
  trivy fs /opt/spc-scheduler/backend
  ```

- [ ] **의존성 업데이트**
  - [ ] 주요 보안 패치 확인
  - [ ] Dependabot 경고 확인
  - [ ] 취약점 있는 패키지 업데이트

### 8.4 접근 제어

- [ ] **IP 화이트리스트** (선택사항)
  ```nginx
  # nginx.conf
  allow 1.2.3.4/32;  # 관리자 IP
  deny all;
  ```

- [ ] **Rate Limiting**
  ```nginx
  # nginx.conf
  limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

  location /api/ {
      limit_req zone=api burst=20;
  }
  ```

---

## 9. 롤백 절차 (Rollback Procedure)

### 9.1 롤백 시나리오

**Health Check 실패 시 자동 롤백**:
- CI/CD 파이프라인에서 자동 실행
- 이전 커밋으로 체크아웃
- 재배포

**수동 롤백**:
```bash
# 1. 이전 버전 확인
git log --oneline -10

# 2. 이전 커밋으로 체크아웃
git checkout <previous-commit-hash>

# 3. 재배포
docker-compose --profile production up -d

# 4. 마이그레이션 (필요 시)
docker-compose exec backend python manage.py migrate

# 5. 정상 작동 확인
curl http://localhost:8000/api/health/
```

### 9.2 데이터베이스 롤백

```bash
# 백업에서 복구
gunzip < /backups/postgresql/spc_db_YYYYMMDD_HHMMSS.sql.gz | psql -U spc_user -h localhost spc_db
```

---

## 10. 문서화 (Documentation)

### 10.1 배포 기록

- [ ] **배포 일지 작성**
  - [ ] 배포 날짜 및 시간
  - [ ] 배포 버전 (Git commit hash)
  - [ ] 배포 담당자
  - [ ] 변경 사항 요약
  - [ ] 발생한 이슈 및 해결방안

### 10.2 운영 매뉴얼

- [ ] **일반 운영 가이드**
  - [ ] 서비스 시작/중지
  - [ ] 로그 확인 방법
  - [ ] 일반적인 문제 해결

- [ ] **비상 연락망**
  - [ ] 개발팀 연락처
  - [ ] 운영팀 연락처
  - [ ] 관리자 연락처

---

## 완료 체크리스트

### 배포 전 (Pre-Deployment)

- [ ] 모든 코드 리뷰 완료
- [ ] 테스트 통과 (단위, 통합, E2E)
- [ ] 환경 변수 설정 완료
- [ ] 데이터베이스 백업 완료
- [ ] 롤백 계획 수립

### 배포 중 (Deployment)

- [ ] 소스 코드 배포 완료
- [ ] Docker 이미지 빌드 완료
- [ ] 컨테이너 시작 완료
- [ ] 데이터베이스 마이그레이션 완료
- [ ] 정적 파일 수집 완료

### 배포 후 (Post-Deployment)

- [ ] Health Check 통과
- [ ] 기능 테스트 통과
- [ ] 성능 테스트 통과
- [ ] 모니터링 설정 완료
- [ ] 알림 설정 완료
- [ ] 배포 문서화 완료

---

## 추가 리소스

- [Docker Deployment Guide](PHASE4_DOCKER_COMPLETE.md)
- [CI/CD Pipeline Guide](PHASE4_CICD_COMPLETE.md)
- [Sample Data Generation](SAMPLE_DATA_COMMAND.md)
- [API Documentation](backend/docs/API.md)

---

**마지막 업데이트**: 2026-01-11
**버전**: 1.0.0
