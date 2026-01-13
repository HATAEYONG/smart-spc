# 🚀 Smart SPC System - Quick Start Guide

## 완성된 기능 요약

### ✅ Backend (Django REST Framework)
- **5개 Django 앱**: Dashboard, Q-COST, Inspection, SPC, QA
- **25개 Django Models**: 완전한 데이터베이스 스키마
- **36개 API 엔드포인트**: 실제 DB 쿼리로 구현 완료
- **Django Admin**: 모든 모델 웹 관리 인터페이스
- **AI Service Layer**: OpenAI GPT-4 / Anthropic Claude 지원

### ✅ Frontend (React + TypeScript)
- **TypeScript 타입 시스템**: 5개 도메인, 36개 DTO
- **API 서비스 레이어**: 5개 서비스
- **7개 차트 페이지**: Recharts로 구현
- **통합 UI**: Card 컴포넌트, purple/pink 테마

## ⚡ 5분 빠른 시작

### 1. PostgreSQL 설치 (Docker)

```bash
# Windows CMD
docker run --name smart-spc-db ^
  -e POSTGRES_PASSWORD=password ^
  -e POSTGRES_DB=smart_spc ^
  -p 5432:5432 ^
  -d postgres:14
```

### 2. 백엔드 설정

```bash
# 1. 가상환경 생성 및 활성화
cd backend
python -m venv venv
venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경변수 설정
copy .env.example .env
# .env 파일을 열어 필요한 키값 수정

# 4. 마이그레이션 실행
python manage.py makemigrations
python manage.py migrate

# 5. 슈퍼유저 생성 (선택사항)
python manage.py createsuperuser

# 6. 샘플 데이터 생성
python scripts/create_sample_data.py

# 7. 서버 시작
python manage.py runserver 0.0.0.0:8000
```

### 3. 프론트엔드 실행

```bash
cd frontend
npm run dev
```

### 4. 접속

| 서비스 | URL | 설명 |
|--------|-----|------|
| 프론트엔드 | http://localhost:5173 | React 앱 |
| 백엔드 API | http://localhost:8000 | Django REST API |
| Django Admin | http://localhost:8000/admin | 웹 관리자 |
| API Health | http://localhost:8000/health/ | 헬스체크 |

## 📡 API 테스트

```bash
# Dashboard Summary
curl http://localhost:8000/api/v1/dashboard/summary?period=2026-01

# Q-COST Categories
curl http://localhost:8000/api/v1/qcost/categories

# Inspection Flows
curl http://localhost:8000/api/v1/inspection/flows

# SPC Sampling Rule
curl "http://localhost:8000/api/v1/spc/sampling/rules?standard=MIL-STD-105E&aql=1.5&lot_size=100"

# QA Processes
curl http://localhost:8000/api/v1/qa/processes
```

## 🗄️ 데이터베이스 스키마

### Dashboard (4개 테이블)
- `dashboard_kpi`: KPI 저장
- `top_defect`: 상위 불량 현황
- `alert`: 알림 관리
- `ai_insight`: AI 인사이트

### Q-COST (4개 테이블)
- `qcost_category`: 카테고리 (예방/평가/내부실패/외부실패)
- `qcost_item`: 비용 아이템
- `qcost_entry`: 비용 엔트리
- `ai_classification_history`: AI 분류 기록

### Inspection (5개 테이블)
- `process_flow`: 검사 프로세스 흐름
- `process_step`: 프로세스 단계
- `inspection_run`: 검사 실시
- `inspection_result`: 검사 결과
- `ai_process_design_history`: AI 공정 설계 기록

### SPC (4개 테이블)
- `sampling_rule`: 표본 추출 규칙
- `spc_chart_definition`: SPC 관리도 정의
- `spc_point`: 측정 포인트
- `spc_event`: SPC 이벤트

### QA (7개 테이블)
- `qa_process`: QA 프로세스
- `qa_checklist_item`: 체크리스트 아이템
- `qa_assessment`: QA 평가
- `qa_finding`: QA 발견사항
- `capa`: CAPA
- `capa_action`: CAPA 조치
- `ai_root_cause_analysis_history`: AI 근본원인분석 기록

## 🔧 API 구현 현황

| 앱 | 엔드포인트 | DB 쿼리 | AI 연동 |
|----|-----------|----------|---------|
| Dashboard | ✓ | ✓ | - |
| Q-COST | ✓ | ✓ | ⏳ |
| Inspection | ✓ | ✓ | ⏳ |
| SPC | ✓ | ✓ | - |
| QA | ✓ | ✓ | ⏳ |

- ✓: 완료
- ⏳: 구현 예정 (AI service 연동 필요)

## 📝 다음 단계

### 1. AI 서비스 연동
```python
# backend/ai_service/services.py
# OpenAI 또는 Anthropic API 키를 .env에 설정
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
# 또는
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

### 2. 프로덕션 배포

#### Gunicorn 사용
```bash
pip install gunicorn
gunicorn smart_spc.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

#### Docker Compose
```bash
docker-compose up -d
```

### 3. 추가 기능 구현
- SPC 차트 재계산 로직
- 실시간 WebSocket 알림
- Excel 업로드/다운로드
- 리포트 PDF 생성

## 🐛 문제 해결

### 마이그레이션 오류
```bash
# 마이그레이션 파일 삭제 후 재생성
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

### 포트 충돌
```bash
# 다른 포트 사용
python manage.py runserver 0.0.0.0:8001
```

### DB 연결 오류
```bash
# PostgreSQL 상태 확인
docker ps | grep smart-spc-db

# 로그 확인
docker logs smart-spc-db
```

## 📚 참고 자료

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Recharts](https://recharts.org/)
- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic Claude](https://docs.anthropic.com/)

---

**개발 완료**: 2025-01-14
**버전**: 1.0.0
**상태**: ✅ 모든 핵심 기능 구현 완료
