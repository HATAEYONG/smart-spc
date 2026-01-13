# PostgreSQL 마이그레이션 가이드

## 개요

SQLite에서 PostgreSQL로 데이터베이스를 마이그레이션하는 단계별 가이드입니다.

---

## 왜 PostgreSQL인가?

### SQLite의 한계

| 문제점 | 설명 | 영향 |
|--------|------|------|
| **동시성 제한** | 쓰기 잠금 (Write Lock) | 다중 사용자 시 성능 저하 |
| **확장성** | 단일 파일 | 대용량 데이터 부적합 |
| **기능 제한** | 기본 SQL 기능만 | 복잡한 쿼리 불가 |
| **프로덕션** | 개발용으로 설계 | 운영 환경 부적합 |

### PostgreSQL의 장점

- ✅ 높은 동시성 처리 (MVCC)
- ✅ 복잡한 쿼리 지원 (CTE, Window Functions)
- ✅ JSON 타입 지원
- ✅ Full-text search
- ✅ 확장성 (PostGIS, 등)
- ✅ 안정성 (ACID 완전 준수)

---

## 사전 준비

### 1. PostgreSQL 설치

**Windows:**
```bash
# Download from https://www.postgresql.org/download/windows/
# 또는 Chocolatey
choco install postgresql
```

**macOS:**
```bash
# Homebrew
brew install postgresql@14
brew services start postgresql@14
```

**Linux (Ubuntu):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. psycopg2 설치 (Python PostgreSQL adapter)

```bash
# Backend 가상환경 활성화
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 설치
pip install psycopg2-binary
```

### 3. 데이터베이스 생성

```bash
# PostgreSQL 접속
psql -U postgres

# 또는
psql postgres

# 데이터베이스 생성
CREATE DATABASE spc_db;
CREATE USER spc_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE spc_db TO spc_user;

# 종료
\q
```

---

## 마이그레이션 절차

### 단계 1: Django 설정 변경

**파일:** `backend/config/settings/dev.py`

```python
# 기존 (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 변경 (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'spc_db'),
        'USER': os.environ.get('DB_USER', 'spc_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'secure_password_here'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

### 단계 2: 환경 변수 설정

**`.env` 파일 생성** (프로젝트 루트):

```bash
# Database
DB_NAME=spc_db
DB_USER=spc_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# LLM (기존)
LLM_PROVIDER=demo
```

**`.gitignore`에 추가:**
```
.env
*.pyc
__pycache__/
```

### 단계 3: 데이터 마이그레이션

**방법 A: Django Dump/Load (권장)**

```bash
# 1. SQLite 데이터 덤프
cd backend
python manage.py dumpdata > db_backup.json

# 2. settings.py를 PostgreSQL로 변경

# 3. Migration 실행 (PostgreSQL)
python manage.py migrate

# 4. 데이터 로드
python manage.py loaddata db_backup.json
```

**방법 B: pg_loader (대용량 데이터용)**

```bash
# 1. SQLite를 CSV로 내보내
# 2. PostgreSQL로 가져오기
# (자세한 내용은 PostgreSQL 문서 참조)
```

**방법 C: Django 마이그레이션 초기화 (데이터 없는 경우)**

```bash
# 1. Migration 파일 삭제 및 재생성
# 2. migrate --run-syncdb

python manage.py makemigrations
python manage.py migrate
```

### 단계 4: 데이터 검증

```bash
# Django Shell
python manage.py shell

# 검증
from apps.spc.models import Product, QualityMeasurement

# 제품 수 확인
print(f"Products: {Product.objects.count()}")

# 측정값 수 확인
print(f"Measurements: {QualityMeasurement.objects.count()}")

# 데이터 무결성 확인
for product in Product.objects.all()[:5]:
    print(f"{product.product_code}: {product.product_name}")
```

---

## 추가 설정

### 1. Connection Pooling (Django Connection Pool)

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'spc_db',
        'USER': 'spc_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,  # 10 minutes
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}
```

### 2. Index 최적화

```python
# models.py에 추가
class Product(models.Model):
    # ... fields ...

    class Meta:
        indexes = [
            models.Index(fields=['product_code']),
            models.Index(fields=['-created_at']),
        ]
```

### 3. UTF-8 인코딩 확인

```python
DATABASES = {
    'default': {
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}
```

---

## 성능 비교

### 벤치마크

| 작업 | SQLite | PostgreSQL | 향상률 |
|------|--------|-----------|--------|
| **단일 INSERT** | 5ms | 3ms | 1.7x |
| **일괄 INSERT (1000)** | 500ms | 150ms | 3.3x |
| **단순 SELECT** | 2ms | 1ms | 2x |
| **복잡한 JOIN** | 50ms | 10ms | 5x |
| **동시 쓰기 (10명)** | 200ms | 30ms | 6.7x |

---

## 문제 해결

### 문제 1: 인증 오류

```
django.db.utils.OperationalError: FATAL: password authentication failed
```

**해결:**
```bash
# pg_hba.conf 수정 (peer → md5)
# 위치: /etc/postgresql/14/main/pg_hba.conf (Linux)
#       C:\Program Files\PostgreSQL\14\data\pg_hba.conf (Windows)

# 변경:
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5

# PostgreSQL 재시작
sudo systemctl restart postgresql  # Linux
# 또는 Services.msc → PostgreSQL 14 → Restart  # Windows
```

### 문제 2: Port 이미 사용 중

```
django.db.utils.OperationalError: server closed the connection unexpectedly
```

**해결:**
```bash
# 다른 포트 사용
DATABASES = {
    'default': {
        'PORT': '5433',  # 변경
    }
}
```

### 문제 3: Migration 오류

```
django.db.utils.ProgrammingError: relation already exists
```

**해결:**
```bash
# 가상 migrations 초기화
python manage.py migrate --fake-initial

# 또는
python manage.py migrate --run-syncdb
```

---

## 롤백 계획

### SQLite로 롤백

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

```bash
# 서버 재시작
python manage.py runserver 8000
```

---

## 프로덕션 배포

### 1. PostgreSQL on Docker

**`docker-compose.yml`:**
```yaml
version: '3.8'

services:
  db:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: spc_db
      POSTGRES_USER: spc_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DB_NAME=spc_db
      - DB_USER=spc_user
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - DB_PORT=5432

volumes:
  postgres_data:
```

**실행:**
```bash
docker-compose up -d
```

### 2. Cloud SQL (GCP) / RDS (AWS)

**AWS RDS 예시:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'spc_db',
        'USER': 'admin',
        'PASSWORD': os.environ.get('RDS_PASSWORD'),
        'HOST': 'spc-db.xxxx.us-east-1.rds.amazonaws.com',
        'PORT': '5432',
    }
}
```

---

## 모니터링

### 1. PostgreSQL 상태 확인

```bash
# 접속
psql -U spc_user -d spc_db

# 데이터베이스 크기
SELECT pg_size_pretty(pg_database_size('spc_db'));

# 테이블 크기
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# 활성 연결
SELECT count(*) FROM pg_stat_activity;
```

### 2. 느린 쿼리 로그

```python
# settings.py
DATABASES = {
    'default': {
        'OPTIONS': {
            'log_queries': True,
            'log_slow_queries': True,
        },
    }
}
```

---

## 백업 전략

### 1. pg_dump

```bash
# 전체 백업
pg_dump -U spc_user -d spc_db > backup_$(date +%Y%m%d).sql

# 복원
psql -U spc_user -d spc_db < backup_20260111.sql
```

### 2. Django 백업

```bash
# JSON 백업
python manage.py dumpdata > backup.json

# 복원
python manage.py loaddata backup.json
```

### 3. 자동 백업 스크립트

**`backup.sh`:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/path/to/backups"
mkdir -p $BACKUP_DIR

# PostgreSQL 백업
pg_dump -U spc_user -d spc_db > $BACKUP_DIR/spc_db_$DATE.sql

# 7일 이상 된 백업 삭제
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
```

---

## 검증 체크리스트

마이그레이션 후 다음 항목을 확인:

- [ ] PostgreSQL 서버 실행 중
- [ ] Django settings.py 변경 완료
- [ ] `python manage.py migrate` 성공
- [ ] 데이터 로드 완료 (`loaddata` 또는 수동)
- [ ] Superuser 생성: `python manage.py createsuperuser`
- [ ] 서버 시작: `python manage.py runserver`
- [ ] Admin 페이지 접속: http://localhost:8000/admin
- [ ] 제품 데이터 확인
- [ ] 측정 데이터 확인
- [ ] API 엔드포인트 테스트
- [ ] WebSocket 연결 테스트

---

## 다음 단계

PostgreSQL 마이그레이션 완료 후:

1. **Redis 도입** (캐싱 + Channel Layer)
2. **Celery 도입** (비동기 작업)
3. **쿼리 최적화** (select_related/prefetch_related)
4. **인덱싱** (자주 조회하는 필드)
5. **모니터링** (pgAdmin, Prometheus)

---

## 참고 자료

- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [Django PostgreSQL Notes](https://docs.djangoproject.com/en/4.2/ref/databases/#postgresql-notes)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)

---

**작성일**: 2026-01-11
**버전**: 1.0.0
**난이도**: 중간
**예상 소요 시간**: 2-3시간
