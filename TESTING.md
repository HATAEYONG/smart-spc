# 테스팅 가이드

이 문서는 Online APS-CPS Scheduler 프로젝트의 테스트 전략과 실행 방법을 설명합니다.

## 📋 목차

- [테스트 구조](#테스트-구조)
- [설치 및 설정](#설치-및-설정)
- [테스트 실행](#테스트-실행)
- [테스트 커버리지](#테스트-커버리지)
- [작성된 테스트](#작성된-테스트)

## 🏗️ 테스트 구조

프로젝트는 세 가지 주요 테스트 스위트로 구성되어 있습니다:

```
online-aps-cps-scheduler/
├── backend/           # Django + DRF 테스트
│   ├── apps/core/tests/
│   ├── apps/online/tests/
│   ├── pytest.ini
│   └── conftest.py
├── worker/           # Python 모듈 테스트
│   └── tests/
└── frontend/         # React 컴포넌트 테스트
    ├── src/components/__tests__/
    ├── src/hooks/__tests__/
    ├── src/utils/__tests__/
    └── vitest.config.ts
```

## 🔧 설치 및 설정

### Backend 테스트 설정

```bash
cd backend
pip install -r requirements.txt
```

필수 패키지:
- pytest
- pytest-django
- pytest-cov
- factory-boy
- faker

### Worker 테스트 설정

Worker는 backend와 동일한 Python 환경을 사용합니다.

### Frontend 테스트 설정

```bash
cd frontend
npm install
```

필수 패키지:
- vitest
- @testing-library/react
- @testing-library/jest-dom
- @testing-library/user-event
- jsdom

## ▶️ 테스트 실행

### 모든 테스트 실행

**Linux/Mac:**
```bash
bash run_all_tests.sh
```

**Windows:**
```cmd
run_all_tests.bat
```

### Backend 테스트만 실행

**Linux/Mac:**
```bash
cd backend
bash run_tests.sh
```

**Windows:**
```cmd
cd backend
run_tests.bat
```

**또는 직접 pytest 실행:**
```bash
cd backend
pytest --cov=apps --cov-report=html -v
```

### Worker 테스트만 실행

**Linux/Mac:**
```bash
cd worker
bash run_tests.sh
```

**Windows:**
```cmd
cd worker
run_tests.bat
```

**또는 직접 pytest 실행:**
```bash
cd worker
pytest tests/ -v
```

### Frontend 테스트만 실행

```bash
cd frontend
npm test              # 인터랙티브 모드
npm run test:ui       # UI 모드
npm run test:coverage # 커버리지 포함
```

### 특정 테스트 파일 실행

**Backend:**
```bash
pytest apps/core/tests/test_models.py -v
```

**Frontend:**
```bash
npm test -- src/components/__tests__/ExportButton.test.tsx
```

### 특정 테스트 케이스 실행

**Backend:**
```bash
pytest apps/core/tests/test_models.py::TestAPSEvent::test_create_event -v
```

**Frontend:**
```bash
npm test -- -t "renders export button"
```

## 📊 테스트 커버리지

### Backend 커버리지 확인

테스트 실행 후 HTML 리포트 생성:
```bash
cd backend
pytest --cov=apps --cov-report=html
```

리포트 확인:
```bash
open htmlcov/index.html  # Mac
start htmlcov/index.html # Windows
```

### Frontend 커버리지 확인

```bash
cd frontend
npm run test:coverage
```

리포트 확인:
```bash
open coverage/index.html  # Mac
start coverage/index.html # Windows
```

## ✅ 작성된 테스트

### Backend Tests

#### Core App Models
**파일:** `backend/apps/core/tests/test_models.py`

- ✅ APSEvent 모델 테스트
  - 이벤트 생성
  - 문자열 표현
  - JSON payload 처리
  - 이벤트 타입 검증

- ✅ APSDecisionLog 모델 테스트
  - 결정 로그 생성
  - KPI 메트릭 저장
  - 이벤트 관계
  - 이유(reason) 텍스트 처리

- ✅ APSDepEdge 모델 테스트
  - 의존성 엣지 생성
  - Unique constraint 검증
  - 엣지 타입 검증

- ✅ StageFactPlanOut 모델 테스트
  - 계획 레코드 생성
  - Freeze level 처리
  - 타임스탬프 검증

#### Online App API
**파일:** `backend/apps/online/tests/test_api.py`

- ✅ APSEvent API 테스트
  - 이벤트 목록 조회 (GET /api/online/events/)
  - 이벤트 생성 (POST /api/online/events/)
  - 이벤트 상세 조회
  - 검색 기능
  - 정렬 기능

- ✅ APSDecisionLog API 테스트
  - 결정 로그 목록 조회
  - 결정 상세 조회
  - Read-only 검증
  - 필터링 (machine, decision, date)
  - 검색 기능

- ✅ 페이지네이션 테스트
  - 기본 페이지네이션
  - 커스텀 페이지 크기
  - 다음 페이지 이동

### Worker Tests

#### APS Solver
**파일:** `worker/tests/test_aps_solver.py`

- ✅ APSSolver 테스트
  - 솔버 초기화
  - 빈 스코프 처리
  - 단일 작업 스케줄링
  - 다중 작업 스케줄링
  - 다중 기계 스케줄링
  - Hard freeze 제약
  - Precedence 제약

#### CPS Gate
**파일:** `worker/tests/test_cps_gate.py`

- ✅ CPSGate 테스트
  - Gate 초기화
  - 빈 계획 시뮬레이션
  - 단일/다중 작업 시뮬레이션
  - KPI 메트릭 계산
  - APPLY/HOLD 결정 로직
  - 높은 utilization 처리
  - 높은 delay 처리

- ✅ Machine & Job 클래스 테스트
  - Machine 리소스 생성
  - Job 처리
  - SimPy 환경 통합

### Frontend Tests

#### Components
**파일:** `frontend/src/components/__tests__/`

- ✅ ExportButton 테스트
  - 버튼 렌더링
  - 메뉴 표시/숨김
  - CSV/JSON 내보내기
  - 빈 데이터 처리
  - 다운로드 링크 생성

- ✅ GanttChart 테스트
  - 차트 렌더링
  - 기계별 그룹핑
  - 작업 표시
  - Freeze level 색상
  - 상세 패널 열기/닫기
  - 빈 상태 처리

#### Hooks
**파일:** `frontend/src/hooks/__tests__/`

- ✅ useAutoRefresh 테스트
  - 초기 상태 설정
  - 인터벌 콜백 실행
  - 토글 기능
  - 비활성화 시 콜백 중단
  - 비동기 콜백 처리
  - 언마운트 시 정리

#### Utils
**파일:** `frontend/src/utils/__tests__/`

- ✅ Export Utilities 테스트
  - CSV 생성
  - JSON 생성
  - 데이터 평탄화 (flattenData)
  - 중첩 객체 처리
  - 배열을 문자열로 변환
  - null/undefined 처리

## 🎯 테스트 작성 가이드라인

### Backend (pytest)

1. **Fixtures 사용**
   ```python
   @pytest.mark.django_db
   def test_create_event(api_client):
       event = APSEventFactory()
       assert event.event_type in ['EMERGENCY_ORDER', 'BREAKDOWN']
   ```

2. **Factory Boy 활용**
   ```python
   event = APSEventFactory(
       event_type='BREAKDOWN',
       mc_cd='MC001'
   )
   ```

3. **API 테스트**
   ```python
   url = reverse('apsevent-list')
   response = api_client.get(url)
   assert response.status_code == status.HTTP_200_OK
   ```

### Frontend (Vitest)

1. **컴포넌트 테스트**
   ```typescript
   import { render, screen } from '../../test/utils';

   it('renders component', () => {
     render(<MyComponent />);
     expect(screen.getByText('Hello')).toBeInTheDocument();
   });
   ```

2. **User Interactions**
   ```typescript
   import { fireEvent } from '@testing-library/react';

   const button = screen.getByRole('button');
   fireEvent.click(button);
   ```

3. **Hook 테스트**
   ```typescript
   import { renderHook, act } from '@testing-library/react';

   const { result } = renderHook(() => useMyHook());
   act(() => {
     result.current.doSomething();
   });
   ```

## 🐛 디버깅 팁

### Backend 디버깅

```bash
# 실패한 테스트에서 중단
pytest -x

# 상세 출력
pytest -vv

# 마지막 실패 테스트만 재실행
pytest --lf

# 특정 마커만 실행
pytest -m unit
```

### Frontend 디버깅

```bash
# UI 모드로 실행 (브라우저에서 확인)
npm run test:ui

# watch 모드
npm test

# 특정 파일만 실행
npm test -- ExportButton.test.tsx
```

## 📈 CI/CD 통합

테스트는 CI/CD 파이프라인에 통합될 수 있습니다:

```yaml
# .github/workflows/test.yml 예시
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run all tests
        run: bash run_all_tests.sh
```

## 🆘 문제 해결

### 일반적인 문제

1. **ModuleNotFoundError (Backend)**
   ```bash
   # PYTHONPATH 설정
   export PYTHONPATH="${PYTHONPATH}:/path/to/backend"
   ```

2. **Database Errors**
   ```bash
   # 테스트 DB 재생성
   pytest --create-db
   ```

3. **Frontend Import Errors**
   ```bash
   # node_modules 재설치
   rm -rf node_modules
   npm install
   ```

## 📚 추가 리소스

- [pytest 문서](https://docs.pytest.org/)
- [Django Testing 문서](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Vitest 문서](https://vitest.dev/)
- [React Testing Library 문서](https://testing-library.com/react)

---

**버전**: 1.0.0
**최종 업데이트**: 2025-12-29
