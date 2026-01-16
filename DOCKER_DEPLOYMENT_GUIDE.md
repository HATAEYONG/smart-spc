# Smart SPC Docker 배포 가이드

이 가이드는 Smart SPC 시스템을 Docker 컨테이너로 배포하는 방법을 안내합니다.

## 목차

1. [사전 요구사항](#사전-요구사항)
2. [프로젝트 구조](#프로젝트-구조)
3. [개발 환경 배포](#개발-환경-배포)
4. [프로덕션 환경 배포](#프로덕션-환경-배포)
5. [환경 변수 설정](#환경-변수-설정)
6. [SSL/HTTPS 설정](#sslhttps-설정)
7. [데이터베이스 마이그레이션](#데이터베이스-마이그레이션)
8. [트러블슈팅](#트러블슈팅)
9. [모니터링 및 로그](#모니터링-및-로그)

---

## 사전 요구사항

### 필수 소프트웨어

- **Docker**: 20.10 이상
- **Docker Compose**: 2.0 이상
- **Git**: 2.0 이상

### 설치 확인

```bash
docker --version
docker compose version
git --version
```

---

## 프로젝트 구조

```
online-aps-cps-scheduler/
├── backend/                    # Django 백엔드
│   ├── Dockerfile             # Backend Dockerfile
│   ├── .dockerignore          # Docker 무시 파일
│   ├── requirements.txt       # Python 의존성
│   ├── smart_spc/            # Django 설정
│   └── manage.py             # Django 관리 스크립트
├── frontend/                   # React 프론트엔드
│   ├── Dockerfile             # Frontend Dockerfile
│   ├── .dockerignore          # Docker 무시 파일
│   ├── package.json           # Node.js 의존성
│   ├── src/                   # React 소스 코드
│   └── nginx.conf             # Nginx 설정 (프로덕션)
├── nginx/                      # Nginx 설정 (리버스 프록시)
│   ├── nginx.conf             # 메인 Nginx 설정
│   ├── conf.d/                # 추가 설정
│   │   └── default.conf       # 기본 설정
│   └── ssl/                   # SSL 인증서 (생성 필요)
├── docker-compose.yml          # 개발 환경 Compose 파일
├── docker-compose.prod.yml     # 프로덕션 환경 Compose 파일
└── .env.production            # 프로덕션 환경 변수
```

---

## 개발 환경 배포

### 1. 환경 변수 설정

`.env` 파일을 프로젝트 루트에 생성:

```bash
cp .env.example .env
```

### 2. 개발 환경 시작

```bash
# 모든 서비스 시작
docker compose up -d

# 로그 확인
docker compose logs -f

# 특정 서비스만 시작
docker compose up -d backend frontend db redis
```

### 3. 데이터베이스 초기화

```bash
# 마이그레이션 실행
docker compose exec backend python manage.py migrate

# 슈퍼유저 생성
docker compose exec backend python manage.py createsuperuser

# 샘플 데이터 생성 (선택사항)
docker compose exec backend python create_sample_data.py --clear
```

### 4. 서비스 확인

```bash
# Django Backend
curl http://localhost:8000/api/v1/health/

# React Frontend
curl http://localhost:5173/

# Django Admin
open http://localhost:8000/admin/
```

### 5. 개발 환경 중지

```bash
# 모든 서비스 중지
docker compose down

# 볼륨 포함하여 모두 삭제
docker compose down -v
```

---

## 프로덕션 환경 배포

### 1. 환경 변수 설정

```bash
# 프로덕션 환경 변수 복사
cp .env.production .env

# 환경 변수 편집
nano .env
```

**중요 설정값 변경:**
- `DJANGO_SECRET_KEY`: 안전한 랜덤 문자열로 변경
- `POSTGRES_PASSWORD`: 강력한 비밀번호로 변경
- `ALLOWED_HOSTS`: 실제 도메인으로 변경
- `CORS_ALLOWED_ORIGINS`: 실제 도메인으로 변경
- `FRONTEND_URL`: 실제 도메인으로 변경

### 2. SSL 인증서 준비 (HTTPS)

#### 옵션 1: Let's Encrypt 사용 (권장)

```bash
# Certbot 설치
sudo apt-get install certbot

# 인증서 발급
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# 인증서 복사
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
```

#### 옵션 2: 자체 서명 인증서 (테스트용)

```bash
# SSL 디렉토리 생성
mkdir -p nginx/ssl

# 자체 서명 인증서 생성
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=KR/ST=Seoul/L=Seoul/O=SPC/CN=your-domain.com"
```

### 3. Nginx 설정 업데이트

`nginx/conf.d/default.conf`에서 HTTPS 설정 주석 해제:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ... 나머지 설정
}
```

### 4. 프로덕션 빌드 및 시작

```bash
# 프로덕션 환경 빌드 및 시작
docker compose -f docker-compose.prod.yml up -d --build

# 로그 확인
docker compose -f docker-compose.prod.yml logs -f

# 상태 확인
docker compose -f docker-compose.prod.yml ps
```

### 5. 데이터베이스 초기화

```bash
# 마이그레이션 실행
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate

# 슈퍼유저 생성
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# static 파일 수집
docker compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# 샘플 데이터 생성 (선택사항)
docker compose -f docker-compose.prod.yml exec backend python create_sample_data.py --clear
```

### 6. 프로덕션 배포 확인

```bash
# Health check
curl https://your-domain.com/health

# API 확인
curl https://your-domain.com/api/v1/quality/issues/

# Frontend 확인
curl https://your-domain.com/
```

---

## 환경 변수 설정

### 주요 환경 변수

| 변수 | 설명 | 기본값 | 필수 |
|------|------|--------|------|
| `DJANGO_SECRET_KEY` | Django 시크릿 키 | - | ✅ |
| `DEBUG` | 디버그 모드 | False | ✅ |
| `ALLOWED_HOSTS` | 허용된 호스트 | localhost | ✅ |
| `CORS_ALLOWED_ORIGINS` | CORS 허용 오리진 | http://localhost | ✅ |
| `POSTGRES_DB` | 데이터베이스 이름 | spc_db | ✅ |
| `POSTGRES_USER` | DB 사용자 | postgres | ✅ |
| `POSTGRES_PASSWORD` | DB 비밀번호 | - | ✅ |
| `OPENAI_API_KEY` | OpenAI API 키 | - | ❌ |

---

## SSL/HTTPS 설정

### SSL 인증서 자동 갱신

```bash
# Certbot 갱신 테스트
sudo certbot renew --dry-run

# Cron 작업 추가 (매일 새벽 2시에 갱신)
echo "0 2 * * * certbot renew --quiet && docker compose -f docker-compose.prod.yml restart nginx" | sudo crontab -
```

---

## 데이터베이스 마이그레이션

### SQLite에서 PostgreSQL로 마이그레이션

```bash
# 1. SQLite 데이터 백업
docker compose exec backend python manage.py dumpdata > backup.json

# 2. PostgreSQL로 전환하여 데이터 로드
docker compose -f docker-compose.prod.yml exec backend python manage.py loaddata backup.json

# 3. 데이터 검증
docker compose -f docker-compose.prod.yml exec backend python manage.py check
```

---

## 트러블슈팅

### 문제 1: 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker compose logs backend
docker compose logs frontend

# 컨테이너 상태 확인
docker compose ps

# 재시작
docker compose restart backend
```

### 문제 2: 데이터베이스 연결 실패

```bash
# DB 컨테이너 상태 확인
docker compose ps db

# DB 로그 확인
docker compose logs db

# DB 재시작
docker compose restart db

# 마이그레이션 재실행
docker compose exec backend python manage.py migrate
```

### 문제 3: Nginx 502 Bad Gateway

```bash
# Backend 상태 확인
docker compose ps backend

# Nginx 로그 확인
docker compose logs nginx

# Backend 재시작
docker compose restart backend
```

### 문제 4: CORS 오류

```bash
# 환경 변수 확인
docker compose exec backend env | grep CORS

# .env 파일의 CORS_ALLOWED_ORIGINS 설정 확인
nano .env
```

---

## 모니터링 및 로그

### 로그 확인

```bash
# 모든 서비스 로그
docker compose logs -f

# 특정 서비스 로그
docker compose logs -f backend
docker compose logs -f nginx

# 최근 100줄만 확인
docker compose logs --tail=100 backend
```

### 컨테이너 리소스 모니터링

```bash
# 컨테이너 상태
docker stats

# 디스크 사용량
docker system df

# 볼륨 확인
docker volume ls
```

### 데이터베이스 백업

```bash
# PostgreSQL 백업
docker compose exec db pg_dump -U postgres spc_db > backup_$(date +%Y%m%d).sql

# PostgreSQL 복원
docker compose exec -T db psql -U postgres spc_db < backup_20250116.sql
```

---

## 배포 체크리스트

### 배포 전

- [ ] 환경 변수 설정 완료
- [ ] SSL 인증서 준비
- [ ] 방화벽 설정 (80, 443 포트)
- [ ] DNS 설정 확인
- [ ] 데이터베이스 비밀번호 변경

### 배포 후

- [ ] Health check 통과
- [ ] API 정상 작동 확인
- [ ] Frontend 접속 확인
- [ ] Admin 페이지 접속 확인
- [ ] 데이터베이스 마이그레이션 완료
- [ ] 로그 확인 (에러 없음)
- [ ] SSL/HTTPS 정상 작동
- [ ] CORS 설정 확인

---

## 추가 도구

### Flower (Celery 모니터링)

```bash
# Flower 접속
open http://localhost:5555

# 프로덕션에서는 주석 처리되어 있음
# docker-compose.prod.yml에서 flower 서비스 활성화
```

### Django Debug Toolbar (개발용)

개발 환경에서는 자동으로 활성화됩니다.

---

## 참고 자료

- [Docker 공식 문서](https://docs.docker.com/)
- [Django 배포 가이드](https://docs.djangoproject.com/en/4.2/howto/deployment/)
- [Nginx 설정 가이드](https://nginx.org/en/docs/)

---

*마지막 업데이트: 2026-01-16*
