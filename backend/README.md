# Smart SPC System - Backend

FastAPI 기반 품질관리 시스템 백엔드

## 기술 스택
- Python 3.10+
- FastAPI 0.104+
- PostgreSQL 14+
- SQLAlchemy 2.0+
- Pydantic v2
- JWT Authentication

## 설치

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션
alembic upgrade head

# 서버 시작
uvicorn app.main:app --reload --port 8000
```

## 프로젝트 구조

```
backend/
├── app/
│   ├── main.py              # FastAPI 앱 진입점
│   ├── config.py            # 설정
│   ├── database.py          # DB 연결
│   ├── models/              # SQLAlchemy ORM 모델
│   ├── schemas/             # Pydantic 스키마 (DTO)
│   ├── api/                 # API 라우터
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── qcost.py
│   │   │   │   ├── inspection.py
│   │   │   │   ├── spc.py
│   │   │   │   └── qa.py
│   ├── core/                # 핵심 기능
│   │   ├── security.py      # JWT 인증
│   │   ├── deps.py          # 의존성 주입
│   └── services/            # 비즈니스 로직
├── alembic/                 # DB 마이그레이션
├── scripts/                 # DDL 및 초기 데이터
└── tests/                   # 테스트
```

## API 문서

서버 시작 후 http://localhost:8000/docs 접속

## 환경변수

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/smart_spc
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
