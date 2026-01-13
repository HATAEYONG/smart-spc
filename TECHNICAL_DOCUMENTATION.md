# APS-CPS Scheduler - 기술 문서

## 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [시스템 아키텍처](#시스템-아키텍처)
3. [기술 스택](#기술-스택)
4. [주요 기능](#주요-기능)
5. [데이터베이스 스키마](#데이터베이스-스키마)
6. [API 엔드포인트](#api-엔드포인트)
7. [프론트엔드 구조](#프론트엔드-구조)
8. [배포 가이드](#배포-가이드)
9. [개발 가이드](#개발-가이드)

---

## 프로젝트 개요

### 프로젝트명
**Online APS-CPS Scheduler** (Advanced Planning & Scheduling with Cyber-Physical System)

### 목적
제조 현장의 생산 계획 및 스케줄링을 최적화하고, 실시간 모니터링 및 시뮬레이션을 통해 효율적인 생산 관리를 지원하는 통합 시스템

### 주요 특징
- 🧬 유전 알고리즘(GA) 기반 생산 스케줄링 최적화
- 📊 실시간 생산 모니터링 및 KPI 대시보드
- 🎯 What-If 시나리오 분석 및 제약조건 관리
- 📈 병목 분석 및 성능 최적화
- 📄 다양한 포맷의 리포트 생성 및 내보내기
- ⚙️ 사용자 맞춤 설정 및 프리셋 관리

---

## 시스템 아키텍처

### 전체 구조
```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  ┌──────────┬──────────┬──────────┬──────────────────┐ │
│  │Dashboard │ Plans    │ Monitoring│ Settings         │ │
│  │          │ (Gantt)  │ & Reports │ & Presets        │ │
│  └──────────┴──────────┴──────────┴──────────────────┘ │
└─────────────────────┬───────────────────────────────────┘
                      │ REST API
┌─────────────────────┴───────────────────────────────────┐
│              Backend (Django REST Framework)             │
│  ┌──────────┬──────────┬──────────┬──────────────────┐ │
│  │ APS      │ Scenario │ Constraint│ Monitoring       │ │
│  │ Engine   │ Analysis │ Manager   │ System           │ │
│  └──────────┴──────────┴──────────┴──────────────────┘ │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│           Database (PostgreSQL / SQLite)                 │
│  ┌──────────┬──────────┬──────────┬──────────────────┐ │
│  │ Plans    │ Events   │ Metrics  │ Settings         │ │
│  └──────────┴──────────┴──────────┴──────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 컴포넌트 구성

#### Backend Layer
- **Django REST Framework**: RESTful API 서버
- **Celery Worker**: 비동기 작업 처리 (알고리즘 실행)
- **PostgreSQL/SQLite**: 데이터 영속성

#### Frontend Layer
- **React 18**: UI 컴포넌트 프레임워크
- **React Router**: 클라이언트 사이드 라우팅
- **Recharts**: 데이터 시각화
- **Axios**: HTTP 클라이언트

---

## 기술 스택

### Backend
| 기술 | 버전 | 용도 |
|------|------|------|
| Python | 3.11+ | 백엔드 언어 |
| Django | 4.2+ | 웹 프레임워크 |
| Django REST Framework | 3.14+ | REST API |
| Celery | 5.3+ | 비동기 작업 처리 |
| Redis | 7.0+ | 메시지 브로커 |
| PostgreSQL | 14+ | 데이터베이스 |
| DEAP | - | 유전 알고리즘 라이브러리 |

### Frontend
| 기술 | 버전 | 용도 |
|------|------|------|
| React | 18.2+ | UI 프레임워크 |
| TypeScript | 5.0+ | 타입 안정성 |
| Vite | 4.4+ | 빌드 도구 |
| React Router DOM | 6.14+ | 라우팅 |
| Recharts | 2.7+ | 차트 라이브러리 |
| Axios | 1.4+ | HTTP 클라이언트 |
| React Hot Toast | 2.4+ | 알림 |
| Lucide React | - | 아이콘 |

### DevOps
| 기술 | 용도 |
|------|------|
| Docker | 컨테이너화 |
| Docker Compose | 멀티 컨테이너 관리 |
| Nginx | 리버스 프록시 |

---

## 주요 기능

### Phase 1: 즉시 효과 기능

#### 1.1 병목 분석 및 최적화
**위치**: `backend/apps/aps/models.py`, `frontend/src/pages/BottleneckAnalysisPage.tsx`

**기능**:
- 기계별 활용률 분석 (0-100%)
- 병목 점수 계산 (활용률 50% + 대기열 30% + 대기시간 20%)
- 시각화: 활용률 Bar Chart, 트렌드 Line Chart, 히트맵
- 개선 권장사항 자동 생성

**주요 알고리즘**:
```python
bottleneck_score = (utilization_rate * 0.5 +
                   min(queue_length * 10, 30) +
                   min(avg_waiting_time / 10, 20))

is_bottleneck = bottleneck_score >= 70
```

#### 1.2 Gantt 차트 고도화
**위치**: `frontend/src/components/GanttChartEnhanced.tsx`

**기능**:
- HTML5 네이티브 드래그 앤 드롭
- 작업 시간 조정 (Resize)
- 기계 간 작업 이동
- 잠금/실행 중 작업 보호
- 실시간 업데이트

**이벤트 처리**:
```typescript
// 마우스 드래그로 작업 이동
handleMouseDown -> handleMouseMove -> handleMouseUp

// 기계 간 드래그 앤 드롭
handleDragStart -> handleDragOver -> handleDrop
```

#### 1.3 성능 대시보드 확장
**위치**: `frontend/src/pages/DashboardPageEnhanced.tsx`

**기능**:
- 5개 주요 KPI 카드
- 성능 트렌드 Area Chart
- 기계별 비교 Bar Chart
- 병목 알림 리스트

**KPI 지표**:
- Total Output (총 생산량)
- Plan Achievement (계획 달성률)
- Avg Utilization (평균 활용률)
- Avg OEE (평균 종합설비효율)
- On-Time Delivery (정시 납품률)

### Phase 2: 중기 효과 기능

#### 2.1 What-If 시나리오 분석
**위치**: `backend/apps/aps/scenario_models.py`, `frontend/src/pages/WhatIfScenarioPage.tsx`

**기능**:
- 4가지 사전 정의 템플릿
  - 기계 증설 시나리오
  - 기계 고장 시나리오
  - 긴급 작업 추가
  - 생산 능력 향상
- 시나리오 실행 (GA 또는 Dispatch Rules)
- 다중 시나리오 비교 (Bar Chart, Radar Chart)

**시나리오 수정 타입**:
```python
"add_machine"      # 기계 추가
"remove_machine"   # 기계 제거
"change_capacity"  # 생산 능력 변경
"add_job"         # 작업 추가
"modify_job"      # 작업 수정
```

#### 2.2 제약조건 관리
**위치**: `backend/apps/aps/constraint_models.py`, `frontend/src/pages/ConstraintManagementPage.tsx`

**기능**:
- 10가지 제약조건 타입 지원
- 제약조건 위반 추적 및 해결
- 우선순위 관리 (LOW, MEDIUM, HIGH, CRITICAL)
- 위반 페널티 설정

**제약조건 타입**:
1. MACHINE_AVAILABILITY - 기계 가용성
2. PRECEDENCE - 선행 관계
3. SETUP_TIME - 준비 시간
4. SKILL_REQUIREMENT - 기술 요구사항
5. MATERIAL_AVAILABILITY - 자재 가용성
6. CAPACITY_LIMIT - 용량 제한
7. TIME_WINDOW - 시간 창
8. BATCH_SIZE - 배치 크기
9. RESOURCE_CONFLICT - 자원 충돌
10. CUSTOM - 사용자 정의

#### 2.3 작업 순서 최적화
**위치**: `backend/apps/aps/sequence_models.py`, `frontend/src/pages/JobSequencePage.tsx`

**기능**:
- 7가지 시퀀싱 규칙 동시 비교
- 수동 순서 조정
- 다중 목표 최적화
- 순서 비교 분석

**시퀀싱 규칙**:
1. FIFO - First In First Out
2. SPT - Shortest Processing Time
3. LPT - Longest Processing Time
4. EDD - Earliest Due Date
5. CR - Critical Ratio
6. SLACK - Minimum Slack
7. WSPT - Weighted Shortest Processing Time

### Phase 3: 시스템 완성도 기능

#### 3.1 실시간 모니터링 대시보드
**위치**: `backend/apps/aps/monitoring_models.py`, `frontend/src/pages/RealtimeMonitoringPage.tsx`

**기능**:
- 6대 기계 실시간 상태 모니터링
- 5개 KPI 요약 카드
- 성능 트렌드 (12시간)
- 기계 상태 분포 Pie Chart
- 활성 알림 관리
- 자동 새로고침 (5s/10s/30s/1m)

**기계 상태**:
- RUNNING - 가동 중
- IDLE - 대기
- SETUP - 준비 중
- MAINTENANCE - 정비
- BREAKDOWN - 고장
- WAITING - 자재 대기

#### 3.2 리포트 생성 및 내보내기
**위치**: `backend/apps/aps/report_models.py`, `frontend/src/pages/ReportsPage.tsx`

**기능**:
- 8가지 리포트 타입
- 4가지 포맷 지원 (PDF, Excel, CSV, JSON)
- 3개 시스템 템플릿
- 빠른 내보내기 (스케줄, 성능 데이터)

**리포트 타입**:
1. Production Summary - 생산 요약
2. Performance Analysis - 성능 분석
3. Quality Report - 품질 보고서
4. Schedule Adherence - 일정 준수
5. Bottleneck Analysis - 병목 분석
6. OEE Report - OEE 보고서
7. Machine Utilization - 기계 활용도
8. Alert Summary - 알림 요약

#### 3.3 사용자 설정 및 프리셋 관리
**위치**: `backend/apps/aps/settings_models.py`, `frontend/src/pages/SettingsPage.tsx`

**기능**:
- 5개 설정 카테고리
- 프리셋 생성/복제/삭제
- 즐겨찾기 관리
- 설정 초기화

**설정 카테고리**:
1. UI Preferences - 테마, 언어, 타임존
2. Dashboard Preferences - 기본 대시보드, 새로고침 간격
3. Gantt Chart Preferences - 뷰 모드
4. Notification Preferences - 알림 활성화, 사운드
5. Algorithm Preferences - 기본 알고리즘, GA 파라미터

---

## 데이터베이스 스키마

### 핵심 테이블

#### 1. StageFactPlanOut (생산 계획)
```sql
CREATE TABLE stage_fact_plan_out (
    plan_id SERIAL PRIMARY KEY,
    wo_no VARCHAR(100),           -- 작업 지시 번호
    item_cd VARCHAR(100),          -- 품목 코드
    mc_cd VARCHAR(20),             -- 기계 코드
    fr_ts TIMESTAMP,               -- 시작 시간
    to_ts TIMESTAMP,               -- 종료 시간
    qty INTEGER,                   -- 수량
    freeze_level INTEGER DEFAULT 0,
    locked_yn VARCHAR(1) DEFAULT 'N',
    decision_yn VARCHAR(1) DEFAULT 'N'
);
```

#### 2. BottleneckAnalysis (병목 분석)
```sql
CREATE TABLE aps_bottleneck_analysis (
    analysis_id SERIAL PRIMARY KEY,
    mc_cd VARCHAR(20) INDEX,
    utilization_rate FLOAT,
    bottleneck_score FLOAT,
    is_bottleneck BOOLEAN,
    recommendations JSONB,
    analyzed_at TIMESTAMP
);
```

#### 3. Scenario (시나리오)
```sql
CREATE TABLE aps_scenario (
    scenario_id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    modifications JSONB,
    algorithm VARCHAR(50),
    status VARCHAR(20),
    results JSONB,
    created_at TIMESTAMP
);
```

#### 4. Constraint (제약조건)
```sql
CREATE TABLE aps_constraint (
    constraint_id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    constraint_type VARCHAR(50),
    priority VARCHAR(20),
    parameters JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    violation_penalty FLOAT
);
```

#### 5. ProductionStatus (생산 상태)
```sql
CREATE TABLE aps_production_status (
    status_id SERIAL PRIMARY KEY,
    mc_cd VARCHAR(50) INDEX,
    status VARCHAR(20),
    current_wo_no VARCHAR(100),
    progress_percentage FLOAT,
    utilization_rate FLOAT,
    oee FLOAT,
    has_alert BOOLEAN,
    last_updated TIMESTAMP
);
```

#### 6. Report (리포트)
```sql
CREATE TABLE aps_report (
    report_id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    report_type VARCHAR(50),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    data JSONB,
    export_format VARCHAR(20),
    status VARCHAR(20),
    created_at TIMESTAMP
);
```

#### 7. UserSettings (사용자 설정)
```sql
CREATE TABLE aps_user_settings (
    setting_id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE INDEX,
    theme VARCHAR(20) DEFAULT 'LIGHT',
    language VARCHAR(10) DEFAULT 'ko',
    default_algorithm VARCHAR(50) DEFAULT 'GA',
    ga_population_size INTEGER DEFAULT 50,
    ga_generations INTEGER DEFAULT 100,
    custom_settings JSONB
);
```

#### 8. Preset (프리셋)
```sql
CREATE TABLE aps_preset (
    preset_id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    preset_type VARCHAR(50),
    configuration JSONB,
    is_public BOOLEAN DEFAULT FALSE,
    is_favorite BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    owner VARCHAR(100)
);
```

### 인덱스 전략
```sql
-- 성능 최적화를 위한 주요 인덱스
CREATE INDEX idx_plan_mc_cd ON stage_fact_plan_out(mc_cd);
CREATE INDEX idx_plan_time ON stage_fact_plan_out(fr_ts, to_ts);
CREATE INDEX idx_bottleneck_mc_cd ON aps_bottleneck_analysis(mc_cd, analyzed_at);
CREATE INDEX idx_status_mc_cd ON aps_production_status(mc_cd, last_updated);
CREATE INDEX idx_alert_severity ON aps_alert(severity, status);
```

---

## API 엔드포인트

### 기본 구조
```
Base URL: http://localhost:8000/api/aps/
```

### 1. 생산 계획 (Plans)
```
GET    /plans/                           # 계획 목록
POST   /plans/                           # 계획 생성
GET    /plans/{id}/                      # 계획 상세
PUT    /plans/{id}/                      # 계획 수정
DELETE /plans/{id}/                      # 계획 삭제
POST   /plans/run_algorithm/             # 알고리즘 실행
GET    /plans/gantt_data/                # Gantt 차트 데이터
```

### 2. 알고리즘 비교 (Comparison)
```
POST   /comparison/compare/              # 알고리즘 비교 실행
GET    /comparison/{id}/results/         # 비교 결과 조회
```

### 3. 병목 분석 (Bottleneck)
```
POST   /bottleneck/run_analysis/         # 분석 실행
GET    /bottleneck/heatmap/              # 히트맵 데이터
GET    /bottleneck/trends/               # 트렌드 데이터
```

### 4. 성능 지표 (Performance)
```
GET    /performance/summary/             # 성능 요약
GET    /performance/machine_comparison/  # 기계별 비교
GET    /performance/trends/              # 성능 트렌드
GET    /performance/algorithm_history/   # 알고리즘 실행 이력
```

### 5. 시나리오 (Scenarios)
```
GET    /scenarios/                       # 시나리오 목록
POST   /scenarios/                       # 시나리오 생성
POST   /scenarios/{id}/run/              # 시나리오 실행
POST   /scenarios/{id}/clone/            # 시나리오 복제
GET    /scenarios/templates/             # 템플릿 조회
```

### 6. 시나리오 비교 (Scenario Comparisons)
```
POST   /scenario-comparisons/create_comparison/  # 비교 생성
GET    /scenario-comparisons/{id}/                # 비교 결과
```

### 7. 제약조건 (Constraints)
```
GET    /constraints/                     # 제약조건 목록
POST   /constraints/                     # 제약조건 생성
POST   /constraints/{id}/toggle_active/  # 활성화 토글
POST   /constraints/{id}/validate/       # 유효성 검증
GET    /constraints/summary/             # 요약 정보
```

### 8. 제약조건 위반 (Violations)
```
GET    /violations/                      # 위반 목록
POST   /violations/{id}/resolve/         # 위반 해결
```

### 9. 작업 순서 (Job Sequences)
```
GET    /job-sequences/                   # 순서 목록
POST   /job-sequences/                   # 순서 생성
POST   /job-sequences/{id}/apply/        # 순서 적용
POST   /job-sequences/{id}/reorder/      # 순서 재배치
POST   /job-sequences/{id}/clone/        # 순서 복제
```

### 10. 순서 최적화 (Sequence Optimizations)
```
POST   /sequence-optimizations/optimize/ # 최적화 실행
GET    /sequence-optimizations/{id}/     # 최적화 결과
```

### 11. 모니터링 (Monitoring)
```
GET    /monitoring/realtime_status/      # 실시간 상태
GET    /monitoring/kpi_summary/          # KPI 요약
GET    /monitoring/performance_trends/   # 성능 트렌드
GET    /monitoring/active_alerts/        # 활성 알림
GET    /monitoring/machine_details/      # 기계 상세 정보
```

### 12. 알림 (Alerts)
```
GET    /alerts/                          # 알림 목록
POST   /alerts/{id}/acknowledge/         # 알림 확인
POST   /alerts/{id}/resolve/             # 알림 해결
GET    /alerts/summary/                  # 알림 요약
```

### 13. 리포트 (Reports)
```
GET    /reports/                         # 리포트 목록
POST   /reports/generate/                # 리포트 생성
GET    /reports/{id}/download/           # 리포트 다운로드
GET    /reports/templates/               # 템플릿 목록
GET    /reports/recent/                  # 최근 리포트
```

### 14. 내보내기 (Exports)
```
POST   /exports/schedule/                # 스케줄 내보내기
POST   /exports/performance_data/        # 성능 데이터 내보내기
GET    /exports/history/                 # 내보내기 이력
```

### 15. 사용자 설정 (User Settings)
```
GET    /user-settings/my_settings/       # 설정 조회
PUT    /user-settings/my_settings/       # 설정 저장
POST   /user-settings/reset_to_default/  # 기본값 초기화
GET    /user-settings/export_settings/   # 설정 내보내기
```

### 16. 프리셋 (Presets)
```
GET    /presets/                         # 프리셋 목록
POST   /presets/                         # 프리셋 생성
POST   /presets/{id}/use/                # 프리셋 사용
POST   /presets/{id}/toggle_favorite/    # 즐겨찾기 토글
POST   /presets/{id}/duplicate/          # 프리셋 복제
GET    /presets/system_presets/          # 시스템 프리셋
GET    /presets/favorites/               # 즐겨찾기 목록
```

### 요청/응답 예시

#### 알고리즘 실행
```http
POST /api/aps/plans/run_algorithm/
Content-Type: application/json

{
  "algorithm": "GA",
  "params": {
    "population_size": 50,
    "generations": 100,
    "mutation_rate": 0.1
  }
}

Response:
{
  "status": "success",
  "execution_time": 15.3,
  "results": {
    "makespan": 1234.5,
    "total_delay": 45.2,
    "plans": [...]
  }
}
```

#### 시나리오 생성 및 실행
```http
POST /api/aps/scenarios/
Content-Type: application/json

{
  "name": "기계 추가 시나리오",
  "modifications": [
    {
      "type": "add_machine",
      "machine": {
        "mc_cd": "MC007",
        "capacity": 100
      }
    }
  ],
  "algorithm": "GA"
}

Response:
{
  "scenario_id": 123,
  "status": "DRAFT",
  "created_at": "2025-12-29T10:00:00Z"
}
```

---

## 프론트엔드 구조

### 디렉토리 구조
```
frontend/
├── src/
│   ├── components/          # 재사용 가능한 컴포넌트
│   │   ├── Layout.tsx
│   │   ├── Layout.css
│   │   ├── GanttChart.tsx
│   │   └── GanttChartEnhanced.tsx
│   ├── pages/              # 페이지 컴포넌트
│   │   ├── DashboardPageEnhanced.tsx
│   │   ├── PlansPage.tsx
│   │   ├── AlgorithmComparisonPage.tsx
│   │   ├── BottleneckAnalysisPage.tsx
│   │   ├── WhatIfScenarioPage.tsx
│   │   ├── ConstraintManagementPage.tsx
│   │   ├── JobSequencePage.tsx
│   │   ├── RealtimeMonitoringPage.tsx
│   │   ├── ReportsPage.tsx
│   │   ├── SettingsPage.tsx
│   │   └── ...
│   ├── config.ts           # 설정 파일
│   ├── App.tsx             # 메인 앱
│   └── main.tsx            # 엔트리 포인트
├── package.json
└── vite.config.ts
```

### 주요 컴포넌트

#### Layout (공통 레이아웃)
```typescript
const Layout = () => {
  const menuGroups = [
    { title: '대시보드', items: [...] },
    { title: 'APS', items: [...] },
    { title: 'CPS 시뮬레이션', items: [...] },
    { title: '모니터링', items: [...] },
    { title: '설정', items: [...] }
  ];

  return (
    <div className="layout">
      <header className="top-bar">...</header>
      <nav className="side-nav">...</nav>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
};
```

#### GanttChartEnhanced (향상된 Gantt 차트)
```typescript
const GanttChartEnhanced = ({ plans, machines, onPlanUpdate }) => {
  // 드래그 앤 드롭 상태 관리
  const [dragState, setDragState] = useState(null);

  // 마우스 이벤트 처리
  const handleMouseDown = (e, plan, action) => {...};
  const handleMouseMove = (e) => {...};
  const handleMouseUp = () => {...};

  // 기계 간 드래그
  const handleDragStart = (e, plan) => {...};
  const handleDrop = (e, targetMachine) => {...};

  return <div className="gantt-chart">...</div>;
};
```

### 상태 관리

#### 로컬 상태 (useState)
```typescript
// 페이지별 로컬 상태
const [data, setData] = useState([]);
const [loading, setLoading] = useState(false);
const [selectedItem, setSelectedItem] = useState(null);
```

#### API 호출 (useEffect)
```typescript
useEffect(() => {
  const loadData = async () => {
    try {
      const response = await axios.get(`${config.apiBaseUrl}/api/aps/...`);
      setData(response.data);
    } catch (error) {
      toast.error('Failed to load data');
    }
  };
  loadData();
}, [dependency]);
```

### 라우팅

```typescript
// App.tsx
<Routes>
  <Route path="/" element={<Layout />}>
    <Route index element={<DashboardPageEnhanced />} />
    <Route path="dashboard" element={<DashboardPageEnhanced />} />
    <Route path="plans" element={<PlansPage />} />
    <Route path="bottleneck-analysis" element={<BottleneckAnalysisPage />} />
    <Route path="whatif-scenarios" element={<WhatIfScenarioPage />} />
    <Route path="constraint-management" element={<ConstraintManagementPage />} />
    <Route path="job-sequence" element={<JobSequencePage />} />
    <Route path="realtime-monitoring" element={<RealtimeMonitoringPage />} />
    <Route path="reports" element={<ReportsPage />} />
    <Route path="settings" element={<SettingsPage />} />
  </Route>
</Routes>
```

---

## 배포 가이드

### Docker Compose 배포

#### 1. 환경 변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# 필수 환경 변수
POSTGRES_DB=aps_db
POSTGRES_USER=aps_user
POSTGRES_PASSWORD=secure_password
DJANGO_SECRET_KEY=your-secret-key
REDIS_URL=redis://redis:6379/0
```

#### 2. 서비스 시작
```bash
# 전체 서비스 빌드 및 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스만 재시작
docker-compose restart backend
```

#### 3. 데이터베이스 마이그레이션
```bash
# 마이그레이션 파일 생성
docker-compose exec backend python manage.py makemigrations

# 마이그레이션 실행
docker-compose exec backend python manage.py migrate

# 슈퍼유저 생성
docker-compose exec backend python manage.py createsuperuser
```

#### 4. 정적 파일 수집
```bash
docker-compose exec backend python manage.py collectstatic --noinput
```

### 프론트엔드 빌드

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 프로덕션 빌드
npm run build

# 빌드 결과 미리보기
npm run preview
```

### Nginx 설정

```nginx
# nginx.conf
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Static files
    location /static/ {
        alias /app/staticfiles/;
    }

    # Media files
    location /media/ {
        alias /app/media/;
    }
}
```

---

## 개발 가이드

### 개발 환경 설정

#### Backend
```bash
# Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r backend/requirements.txt

# 개발 서버 실행
cd backend
python manage.py runserver

# Celery Worker 실행 (별도 터미널)
celery -A config worker -l info
```

#### Frontend
```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# TypeScript 타입 체크
npm run type-check

# Linting
npm run lint
```

### 코드 스타일

#### Python (Backend)
```python
# PEP 8 준수
# Black formatter 사용
# Docstring 작성

class MyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing resources.

    Provides CRUD operations and custom actions.
    """
    queryset = MyModel.objects.all()
    serializer_class = MySerializer

    @action(detail=False, methods=["post"])
    def custom_action(self, request):
        """
        Custom action description.

        Args:
            request: HTTP request object

        Returns:
            Response with action result
        """
        # Implementation
        pass
```

#### TypeScript (Frontend)
```typescript
// 함수형 컴포넌트
// Props 타입 정의
// 명확한 변수명

interface MyComponentProps {
  data: DataType[];
  onAction: (id: number) => void;
}

const MyComponent: React.FC<MyComponentProps> = ({ data, onAction }) => {
  const [state, setState] = useState<StateType | null>(null);

  useEffect(() => {
    // Side effects
  }, [dependency]);

  return <div>...</div>;
};
```

### 새로운 기능 추가

#### 1. Backend 모델 추가
```python
# backend/apps/aps/models.py
class NewFeature(models.Model):
    feature_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    # ... 필드 정의

    class Meta:
        db_table = "aps_new_feature"
        ordering = ["-created_at"]
```

#### 2. Serializer 추가
```python
# backend/apps/aps/serializers.py
class NewFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewFeature
        fields = "__all__"
```

#### 3. ViewSet 추가
```python
# backend/apps/aps/views.py
class NewFeatureViewSet(viewsets.ModelViewSet):
    queryset = NewFeature.objects.all()
    serializer_class = NewFeatureSerializer

    @action(detail=False, methods=["post"])
    def custom_action(self, request):
        # 커스텀 액션 구현
        pass
```

#### 4. URL 등록
```python
# backend/apps/aps/urls.py
router.register(r'new-feature', NewFeatureViewSet, basename='new-feature')
```

#### 5. Frontend 페이지 추가
```typescript
// frontend/src/pages/NewFeaturePage.tsx
const NewFeaturePage = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    const response = await axios.get(`${config.apiBaseUrl}/api/aps/new-feature/`);
    setData(response.data);
  };

  return <div className="new-feature-page">...</div>;
};
```

#### 6. 라우트 추가
```typescript
// frontend/src/App.tsx
import NewFeaturePage from './pages/NewFeaturePage';

<Route path="new-feature" element={<NewFeaturePage />} />
```

#### 7. 메뉴 추가
```typescript
// frontend/src/components/Layout.tsx
{
  title: '그룹명',
  items: [
    { path: '/new-feature', label: '새 기능', icon: '🆕' }
  ]
}
```

### 테스트

#### Backend 테스트
```python
# backend/apps/aps/tests.py
from django.test import TestCase
from rest_framework.test import APIClient

class NewFeatureTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_feature(self):
        response = self.client.post('/api/aps/new-feature/', {
            'name': 'Test Feature'
        })
        self.assertEqual(response.status_code, 201)
```

실행:
```bash
python manage.py test apps.aps.tests
```

#### Frontend 테스트 (예시)
```typescript
// frontend/src/pages/NewFeaturePage.test.tsx
import { render, screen } from '@testing-library/react';
import NewFeaturePage from './NewFeaturePage';

test('renders new feature page', () => {
  render(<NewFeaturePage />);
  const heading = screen.getByText(/새 기능/i);
  expect(heading).toBeInTheDocument();
});
```

### 디버깅

#### Backend 디버깅
```python
# Django Debug Toolbar 사용
# settings.py
INSTALLED_APPS += ['debug_toolbar']

# 로깅 설정
import logging
logger = logging.getLogger(__name__)

def my_view(request):
    logger.debug(f"Request data: {request.data}")
    # ...
```

#### Frontend 디버깅
```typescript
// React DevTools 사용
// 콘솔 로그
console.log('Data:', data);

// 네트워크 요청 확인
axios.interceptors.request.use(request => {
  console.log('Request:', request);
  return request;
});
```

---

## 성능 최적화

### Backend 최적화

#### 1. 데이터베이스 쿼리 최적화
```python
# select_related (1:1, N:1)
Plan.objects.select_related('machine', 'item').all()

# prefetch_related (N:N, 1:N)
Plan.objects.prefetch_related('events').all()

# only() / defer()
Plan.objects.only('plan_id', 'wo_no')
```

#### 2. 캐싱
```python
from django.core.cache import cache

def get_expensive_data():
    cache_key = 'expensive_data'
    result = cache.get(cache_key)

    if result is None:
        result = expensive_computation()
        cache.set(cache_key, result, timeout=300)  # 5분

    return result
```

#### 3. 페이지네이션
```python
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
```

### Frontend 최적화

#### 1. 컴포넌트 메모이제이션
```typescript
// React.memo
const ExpensiveComponent = React.memo(({ data }) => {
  return <div>{/* ... */}</div>;
});

// useMemo
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data);
}, [data]);

// useCallback
const handleClick = useCallback(() => {
  doSomething(id);
}, [id]);
```

#### 2. 코드 스플리팅
```typescript
// Lazy loading
const LazyPage = React.lazy(() => import('./pages/LazyPage'));

<Suspense fallback={<div>Loading...</div>}>
  <LazyPage />
</Suspense>
```

#### 3. 데이터 Fetching 최적화
```typescript
// Promise.all로 병렬 요청
const loadData = async () => {
  const [data1, data2, data3] = await Promise.all([
    axios.get('/api/endpoint1'),
    axios.get('/api/endpoint2'),
    axios.get('/api/endpoint3')
  ]);
};
```

---

## 보안

### Backend 보안

#### 1. CORS 설정
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://your-domain.com"
]
```

#### 2. Authentication
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
}
```

#### 3. SQL Injection 방지
```python
# ORM 사용 (자동 이스케이프)
Plan.objects.filter(wo_no=user_input)

# Raw SQL 사용 시 파라미터 바인딩
cursor.execute("SELECT * FROM plans WHERE wo_no = %s", [user_input])
```

### Frontend 보안

#### 1. XSS 방지
```typescript
// React는 자동으로 이스케이프
<div>{userInput}</div>

// dangerouslySetInnerHTML 사용 시 주의
// DOMPurify 라이브러리 사용 권장
```

#### 2. CSRF 토큰
```typescript
// Axios 설정
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
```

---

## 모니터링 및 로깅

### 로깅 설정

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps.aps': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### 성능 모니터링

```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        logger.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper

@monitor_performance
def expensive_operation():
    # ...
    pass
```

---

## 문제 해결

### 일반적인 문제

#### 1. CORS 오류
```
Access to XMLHttpRequest has been blocked by CORS policy
```
**해결**: `settings.py`에서 `CORS_ALLOWED_ORIGINS` 확인

#### 2. 마이그레이션 충돌
```
Conflicting migrations detected
```
**해결**:
```bash
python manage.py makemigrations --merge
python manage.py migrate
```

#### 3. 포트 이미 사용 중
```
Error: Port 8000 is already in use
```
**해결**:
```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

#### 4. npm 의존성 오류
```
ERESOLVE unable to resolve dependency tree
```
**해결**:
```bash
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

---

## 버전 히스토리

### v1.0.0 (2025-12-29)
- ✅ 초기 릴리스
- ✅ Phase 1-3 모든 기능 구현
- ✅ 12개 주요 페이지 완성
- ✅ 47개 이상 API 엔드포인트
- ✅ Docker Compose 배포 지원

---

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

## 연락처 및 지원

- **프로젝트 저장소**: [GitHub Repository]
- **이슈 트래커**: [GitHub Issues]
- **문서**: [Documentation Site]

---

**마지막 업데이트**: 2025-12-29
**문서 버전**: 1.0.0
