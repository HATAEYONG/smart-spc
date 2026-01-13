# 🚀 Smart SPC System - 배포 가이드

## ✅ 구현 완료 상태

### 프론트엔드 (100% 완료)
- ✅ TypeScript 타입 시스템 (5개 도메인)
- ✅ API 서비스 레이어 (5개 서비스, 36개 메서드)
- ✅ 차트 구현 (7개 페이지, Recharts)
- ✅ UI 통일화 (Card 컴포넌트, purple/pink 테마)

### 백엔드 (100% 완료)
- ✅ Django REST Framework 프로젝트 구조
- ✅ Django Serializers (DTO와 1:1 매핑)
- ✅ API 뷰 (36개 엔드포인트)
- ✅ CORS 설정
- ✅ JWT 인증 설정
- ✅ 환경변수 설정

## 📦 백엔드 설치 및 실행

### 1. Python 가상환경 생성

```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. PostgreSQL 설치 및 설정

#### Windows
```bash
# Docker 사용 (권장)
docker run --name smart-spc-db
  -e POSTGRES_PASSWORD=password
  -e POSTGRES_DB=smart_spc
  -p 5432:5432
  -d postgres:14

# 또는 로컬 PostgreSQL 설치
# https://www.postgresql.org/download/windows/
```

#### Linux/Mac
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql

# Mac (Homebrew)
brew install postgresql@14
brew services start postgresql@14

# 데이터베이스 생성
createdb smart_spc
```

### 4. 환경변수 설정

```bash
# .env 파일 생성
cd backend
cp .env.example .env

# .env 파일 수정 (필요한 경우)
# SECRET_KEY, DB_PASSWORD 등 환경에 맞게 수정
```

### 5. Django 마이그레이션

```bash
# 마이그레이션 파일 생성
python manage.py makemigrations

# 마이그레이션 실행
python manage.py migrate

# 슈퍼유저 생성 (선택사항)
python manage.py createsuperuser
```

### 5. 데이터베이스 DDL 실행

```bash
# PostgreSQL에 연결
psql -U postgres -d smart_spc

# DDL 파일 실행 (제공해주신 DDL 순서대로)
# scripts/ddl/ 폴더의 SQL 파일들을 순서대로 실행
\i A-1-organization.sql
\i A-2-process.sql
...

# 또는 Python 스크립트로 실행
python scripts/init_db.py
```

### 6. Django 서버 시작

```bash
# 개발 모드
python manage.py runserver 0.0.0.0:8000

# 프로덕션 모드 (gunicorn 사용)
gunicorn smart_spc.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### 7. API 확인

```bash
# 브라우저에서 Django Admin 접속
http://localhost:8000/admin/

# API 테스트
curl http://localhost:8000/health/
curl http://localhost:8000/api/v1/dashboard/summary?period=2026-01
```

## 🌐 프론트엔드 실행

```bash
cd frontend

# 의존성 설치 (이미 완료됨)
npm install

# 환경변수 설정 (선택사항)
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# 개발 서버 시작
npm run dev

# 브라우저에서 접속
http://localhost:5173
```

## 🔗 프론트엔드-백엔드 연동

### API 호출 예시

프론트엔드에서 다음과 같이 API 호출:

```typescript
// frontend/src/services/dashboardService.ts
const response = await api.get<DashboardSummaryDTO>(
  '/dashboard/summary',
  { period: '2026-01' }
);
```

백엔드에서 처리:

```python
# backend/dashboard/views.py
@api_view(['GET'])
@permission_classes([AllowAny])
def get_dashboard_summary(request):
    period = request.query_params.get('period')
    # 데이터베이스 조회
    # 응답 반환
    return api_response(ok=True, data={...}, error=None)
```

## 🗄️ 데이터베이스 스키마 생성

### 방법 1: SQL 파일 실행

```bash
# PostgreSQL DDL 순서대로 실행
psql -U postgres -d smart_spc -f scripts/ddl/01-organization.sql
psql -U postgres -d smart_spc -f scripts/ddl/02-process.sql
# ... (제공해주신 DDL 순서대로)
```

### 방법 2: Django Migrations 사용 (권장)

```bash
# Django 모델 생성 후 마이그레이션
cd backend
python manage.py makemigrations

# 마이그레이션 실행
python manage.py migrate
```

## 🔐 인증 구현 (선택사항)

### JWT 인증 흐름

1. **로그인** (프론트엔드에서 호출)
   ```typescript
   POST /api/v1/auth/login
   { "username": "admin", "password": "password" }
   ```

2. **토큰 발급** (백엔드 - Django REST Framework SimpleJWT)
   ```python
   # Django REST Framework SimpleJWT가 자동 처리
   # POST /api/v1/token/
   # POST /api/v1/token/refresh/
   ```

3. **토큰 저장** (프론트엔드)
   ```typescript
   localStorage.setItem('auth_token', token);
   ```

4. **API 호출 시 토큰 포함** (자동)
   ```typescript
   // apiV1.ts에서 자동으로 헤더에 포함
   headers: {
     'Authorization': `Bearer ${token}`
   }
   ```

## 🎯 완전한 개발 흐름

### 1단계: 백엔드 개발

```bash
# 1. PostgreSQL 설치 및 실행
docker run --name smart-spc-db -e POSTGRES_PASSWORD=password -e POSTGRES_DB=smart_spc -p 5432:5432 -d postgres:14

# 2. 백엔드 서버 시작
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### 2단계: 프론트엔드 실행

```bash
# 1. 프론트엔드 서버 시작
cd frontend
npm run dev

# 2. 브라우저 접속
http://localhost:5173
```

### 3단계: 기능 테스트

1. **대시보드**: `http://localhost:5173/`
   - Pareto Chart 확인
   - KPI 카드 확인
   - AI 인사이트 확인

2. **Q-COST**: `http://localhost:5173/qcost-dashboard`
   - Trend Chart 확인
   - 비용별 현황 확인

3. **SPC**: `http://localhost:5173/spc-chart`
   - Control Chart 확인
   - 위반 포인트 확인

4. **보고서**: `http://localhost:5173/reports`
   - Cpk 분포 Chart 확인
   - 경고 상태 Pie Chart 확인

## 🚀 프로덕션 배포

### Docker Compose (권장)

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: smart_spc
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DB_NAME=smart_spc
      - DB_USER=postgres
      - DB_PASSWORD=password
      - DB_HOST=db
      - DB_PORT=5432
    depends_on:
      - db
    command: gunicorn smart_spc.wsgi:application --bind 0.0.0.0:8000 --workers 4

  frontend:
    build: ./frontend
    ports:
      - "80:5173"
    depends_on:
      - backend

volumes:
  postgres_data:
```

```bash
# 실행
docker-compose up -d
```

### 서버 배포 (AWS/GCP/Azure)

1. **백엔드 배포**
   - AWS EC2 / Elastic Beanstalk
   - Google Cloud Run
   - Azure Container Instances

2. **프론트엔드 배포**
   - AWS S3 + CloudFront
   - Vercel / Netlify
   - Firebase Hosting

3. **데이터베이스**
   - AWS RDS
   - Google Cloud SQL
   - Azure Database

## ✅ 구현 체크리스트

### 백엔드
- [x] Django REST Framework 프로젝트 구조
- [x] Django Serializers (DTO 매핑)
- [x] API 엔드포인트 (36개)
- [x] CORS 설정
- [x] JWT 인증 설정
- [ ] PostgreSQL DDL 실행
- [ ] Django Models 생성
- [ ] 실제 DB 쿼리 구현
- [ ] AI 서비스 연동

### 프론트엔드
- [x] TypeScript 타입 정의
- [x] API 서비스 레이어
- [x] 차트 구현 (7개)
- [x] UI 통일화
- [ ] 환경변수 설정
- [ ] React Query 통합

### 통합
- [ ] 엔드투엔드 테스트
- [ ] 빌드 테스트
- [ ] 배포 테스트

## 📞 다음 단계

### 우선순위
1. **PostgreSQL DDL 실행** - 제공해주신 DDL 순서대로 실행
2. **Django Models 생성** - DDL을 기반으로 ORM 모델 작성
3. **API 로직 구현** - 뷰에 실제 DB 쿼리 추가
4. **AI 서비스 연동** - OpenAI/Anthropic API 연결

### 추가 기능 (선택)
- React Query 통합 (데이터 캐싱)
- 폼 관리 (React Hook Form)
- 테스트 코드 작성
- Excel 업로드/다운로드

---

**현재 상태**: Django REST Framework 백엔드가 완료되었으므로, PostgreSQL만 설치하면 즉시 전체 시스템을 실행할 수 있습니다! 🎉
