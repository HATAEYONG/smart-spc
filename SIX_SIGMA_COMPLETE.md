# Six Sigma DMAIC 시스템 완료 문서

## 개요

SPC 품질관리 시스템에 Six Sigma DMAIC (Define, Measure, Analyze, Improve, Control) 방법론을 기반으로 한 품질 개선 프로젝트 관리 기능과 Minitab 스타일의 통계 분석 도구를 구현했습니다.

---

## 구현 완료 기능

### 1. 백엔드 (Backend Django)

#### 1.1 데이터 모델 (`backend/apps/spc/models/six_sigma.py`)

**DMAICProject**
- 프로젝트 기본 정보 (코드, 이름, 설명)
- 5단계 관리 (Define → Measure → Analyze → Improve → Control → Closed)
- 상태 및 우선순위 추적
- 담당자 (Champion, Process Owner, Team Members)
- 기간 및 비용 관리
- 목표 및 성과 추적

**DefinePhase** - 정의 단계
- VOC (Voice of Customer)
- CTQ (Critical to Quality) 항목
- 프로젝트 범위 (In/Out Scope)
- SIPOC 다이어그램
- 이해관계자 및 리스크

**MeasurePhase** - 측정 단계
- MSA (Measurement System Analysis)
- 데이터 수집 계획
- 기준선 성능 (Baseline)
- Yield, Defect Rate, DPMO 추적

**AnalyzePhase** - 분석 단계
- 통계적 분석 결과
- 근본 원인 분석 (Fishbone, 5-Why)
- 가설 검정 결과
- 공정능력 분석 (Cp, Cpk)

**ImprovePhase** - 개선 단계
- 해결책 선정
- 실험 계획법 (DOE)
- 구현 계획
- 예상 성과

**ControlPhase** - 관리 단계
- 관리 계획서
- 모니터링 계획
- SOP 표준화
- 교육 계획
- 교훈 및 다음 단계

**DMAICMilestone** - 마일스톤 관리
**DMAICDocument** - 문서 관리
**DMAICRisk** - 리스크 관리
**StatisticalTool** - 통계 도구 실행 결과 저장

#### 1.2 통계 분석 서비스 (`backend/apps/spc/services/six_sigma_tools.py`)

**SixSigmaAnalyzer 클래스** - 600+ 라인

구현된 통계 도구:
1. **기술 통계 (Descriptive Statistics)**
   - 평균, 중앙값, 최빈값
   - 표준편차, 분산, 범위
   - 사분위수 (Q1, Q3, IQR)
   - 왜도 (Skewness), 첨도 (Kurtosis)
   - 변동계수 (CV)

2. **히스토그램 (Histogram)**
   - 계급 구간 설정
   - 도수 분포
   - 밀도 추정

3. **파레토도 (Pareto Chart)**
   - 정렬 및 누적 백분율
   - 80/20 법칙 시각화

4. **상자 수염 그림 (Box Plot)**
   - 다중 그룹 비교
   - 이상치 식별
   - 사분위수 범위

5. **상관 분석 (Correlation)**
   - Pearson 상관계수
   - Spearman 순위 상관계수
   - 선형 회귀 분석
   - R-squared, 잔차 분석

6. **T-검정 (T-Test)**
   - 일표본 T-검정
   - 독립 표본 T-검정
   - 대응표본 T-검정
   - 신뢰구간

7. **분산분석 (ANOVA)**
   - 일원분산분석 (One-Way ANOVA)
   - F-검정
   - Eta 제곱 (효과 크기)

8. **공정능력 분석 (Process Capability)**
   - Cp, Cpk, Cpu, Cpl
   - 불량률 추정
   - DPMO (백만회당 불격수)
   - Sigma 레벨 계산
   - 해석 및 권장사항

9. **Gage R&R**
   - 측정 시스템 반복성 및 재현성
   - % Gage R&R
   - NDC (구별 가능한 범주 수)

10. **런 차트 (Run Chart)**
    - 추세 분석
    - 이동 평균

#### 1.3 API 시리얼라이저 (`backend/apps/spc/serializers/six_sigma.py`)

- DMAICProjectListSerializer, DMAICProjectDetailSerializer
- 5개 Phase 시리얼라이저 (Define, Measure, Analyze, Improve, Control)
- DMAICMilestone, DMAICDocument, DMAICRisk 시리얼라이저
- StatisticalTool 시리얼라이저
- 통계 도구 Request 시리얼라이저 (8개)

#### 1.4 API 뷰 (`backend/apps/spc/views/six_sigma.py`)

**DMAICProjectViewSet**
- 프로젝트 CRUD
- 필터링 (phase, status, priority)
- dashboard 액션: 대시보드 데이터
- advance_phase 액션: 단계 진행

**StatisticalToolViewSet**
- descriptive_statistics
- histogram
- pareto
- box_plot
- correlation
- t_test
- anova
- capability_analysis
- gage_rr
- run_chart
- scatter_plot
- save_analysis: 분석 결과 저장

### 2. 프론트엔드 (Frontend React + TypeScript)

#### 2.1 페이지 컴포넌트

**SixSigmaDashboardPage** (`frontend/src/pages/SixSigmaDashboardPage.tsx`)
- 대시보드 요약 카드 (전체 프로젝트, 진행 중, 완료, 긴급)
- DMAIC 단계별 현황 (5개 단계 시각화)
- 최근 프로젝트 테이블
- 빠른 액션 버튼 (프로젝트 생성, 통계 도구, 보고서)

**SixSigmaToolsPage** (`frontend/src/pages/SixSigmaToolsPage.tsx`)
- 8개 통계 도구 선택 카드
- 데이터 입력 영역
- 도구별 파라미터 입력
- 분석 실행 버튼
- 결과 표시 영역
- 빠른 참조 가이드

#### 2.2 API 서비스 (`frontend/src/services/sixSigmaApi.ts`)

```typescript
// DMAIC Projects
getDMAICProjects(params?)
getDMAICProject(id)
createDMAICProject(data)
updateDMAICProject(id, data)
advanceProjectPhase(id)

// Dashboard
getDashboardStats()

// Statistical Tools (8개)
descriptiveStatistics(data)
histogramAnalysis(data, bins)
paretoAnalysis(categories, values)
boxPlotAnalysis(groups)
correlationAnalysis(x_data, y_data)
tTest(sample1, sample2?, mu0, test_type, alpha)
anovaAnalysis(groups, alpha)
capabilityAnalysis(data, lsl, usl, target)
gageRRAnalysis(measurements)
```

#### 2.3 라우팅 추가 (`frontend/src/App.tsx`)

- `/six-sigma` - Six Sigma DMAIC 대시보드
- `/six-sigma/tools` - 통계 분석 도구

---

## API 엔드포인트

### DMAIC 프로젝트 관리

```
GET    /api/six-sigma/projects/              # 프로젝트 목록
GET    /api/six-sigma/projects/dashboard/     # 대시보드 데이터
POST   /api/six-sigma/projects/              # 프로젝트 생성
GET    /api/six-sigma/projects/{id}/         # 프로젝트 상세
PUT    /api/six-sigma/projects/{id}/         # 프로젝트 수정
DELETE /api/six-sigma/projects/{id}/         # 프로젝트 삭제
POST   /api/six-sigma/projects/{id}/advance_phase/  # 단계 진행
```

### DMAIC Phase 관리

```
GET    /api/six-sigma/define/               # Define 단계 목록
POST   /api/six-sigma/define/               # Define 단계 생성
GET    /api/six-sigma/measure/              # Measure 단계 목록
POST   /api/six-sigma/measure/              # Measure 단계 생성
GET    /api/six-sigma/analyze/              # Analyze 단계 목록
POST   /api/six-sigma/analyze/              # Analyze 단계 생성
GET    /api/six-sigma/improve/              # Improve 단계 목록
POST   /api/six-sigma/improve/              # Improve 단계 생성
GET    /api/six-sigma/control/              # Control 단계 목록
POST   /api/six-sigma/control/              # Control 단계 생성
```

### 서포트 기능

```
GET    /api/six-sigma/milestones/           # 마일스톤 목록
POST   /api/six-sigma/milestones/           # 마일스톤 생성
GET    /api/six-sigma/documents/            # 문서 목록
POST   /api/six-sigma/documents/            # 문서 업로드
GET    /api/six-sigma/risks/                # 리스크 목록
POST   /api/six-sigma/risks/                # 리스크 생성
```

### 통계 분석 도구

```
POST   /api/six-sigma/statistical-tools/descriptive_statistics/   # 기술 통계
POST   /api/six-sigma/statistical-tools/histogram/               # 히스토그램
POST   /api/six-sigma/statistical-tools/pareto/                   # 파레토도
POST   /api/six-sigma/statistical-tools/box_plot/                 # 상자 수염 그림
POST   /api/six-sigma/statistical-tools/correlation/              # 상관 분석
POST   /api/six-sigma/statistical-tools/t_test/                    # T-검정
POST   /api/six-sigma/statistical-tools/anova/                     # 분산분석
POST   /api/six-sigma/statistical-tools/capability_analysis/       # 공정능력 분석
POST   /api/six-sigma/statistical-tools/gage_rr/                   # Gage R&R
POST   /api/six-sigma/statistical-tools/run_chart/                 # 런 차트
POST   /api/six-sigma/statistical-tools/scatter_plot/              # 산점도
POST   /api/six-sigma/statistical-tools/save_analysis/              # 결과 저장
GET    /api/six-sigma/statistical-tools/                            # 저장된 분석 목록
```

---

## 데이터베이스 스키마

### 주요 테이블

| 테이블 | 설명 |
|--------|------|
| `dmaic_project` | DMAIC 프로젝트 |
| `dmaic_define_phase` | Define 단계 |
| `dmaic_measure_phase` | Measure 단계 |
| `dmaic_analyze_phase` | Analyze 단계 |
| `dmaic_improve_phase` | Improve 단계 |
| `dmaic_control_phase` | Control 단계 |
| `dmaic_milestone` | 마일스톤 |
| `dmaic_document` | 문서 |
| `dmaic_risk` | 리스크 |
| `dmaic_statistical_tool` | 통계 도구 실행 결과 |

---

## 사용 예시

### 1. 프로젝트 생성

```bash
curl -X POST http://localhost:8000/api/six-sigma/projects/ \
  -H "Content-Type: application/json" \
  -d '{
    "project_code": "SS-2024-001",
    "project_name": "배터리 셀 불량률 감소",
    "description": "배터리 셀 생산 공정의 불량률을 5%에서 2%로 감소",
    "phase": "DEFINE",
    "status": "NOT_STARTED",
    "priority": "HIGH",
    "start_date": "2024-01-01",
    "target_end_date": "2024-06-30",
    "problem_statement": "현재 불량률 5%로 목표치 3% 초과",
    "goal_statement": "불량률 5% → 2% 감소",
    "benefit_target": "불량률 3% 감소, 연간 5억원 절감"
  }'
```

### 2. 기술 통계 분석

```bash
curl -X POST http://localhost:8000/api/six-sigma/statistical-tools/descriptive_statistics/ \
  -H "Content-Type: application/json" \
  -d '{
    "data": [10.2, 10.5, 10.3, 10.7, 10.4, 10.6, 10.3, 10.5, 10.8, 10.4],
    "variable_name": "배터리 전압"
  }'
```

**응답 예시:**
```json
{
  "variable_name": "배터리 전압",
  "analysis_type": "Descriptive Statistics",
  "results": {
    "count": 10,
    "mean": 10.47,
    "median": 10.45,
    "std_dev": 0.188,
    "min": 10.2,
    "max": 10.8,
    "q1": 10.3,
    "q3": 10.6,
    "cv": 1.8
  }
}
```

### 3. 공정능력 분석

```bash
curl -X POST http://localhost:8000/api/six-sigma/statistical-tools/capability_analysis/ \
  -H "Content-Type: application/json" \
  -d '{
    "data": [10.1, 10.2, 10.3, 10.4, 10.5, 10.5, 10.6, 10.7, 10.8, 10.9],
    "lsl": 10.0,
    "usl": 11.0,
    "target": 10.5
  }'
```

**응답 예시:**
```json
{
  "analysis_type": "Process Capability Analysis",
  "results": {
    "statistics": {
      "mean": 10.5,
      "std_dev": 0.258
    },
    "capability_indices": {
      "cp": 1.29,
      "cpk": 1.29,
      "cpu": 1.29,
      "cpl": 1.29
    },
    "defect_rates": {
      "p_total": 0.0013,
      "dpmo": 1350,
      "yield": 99.87
    },
    "sigma_level": 4.51,
    "capability_level": "4-Sigma (Good)",
    "performance": "Good"
  }
}
```

---

## 통계 도구 기능 상세

### 1. 기술 통계 (Descriptive Statistics)

**출력 항목:**
- Count, Mean, Median, Mode
- Standard Deviation, Variance
- Min, Max, Range
- Q1, Q3, IQR
- Skewness, Kurtosis
- Coefficient of Variation (CV)

### 2. 공정능력 분석 (Process Capability)

**출력 항목:**
- Cp, Cpk, Cpu, Cpl
- 불량률 (Total, Above USL, Below LSL)
- DPMO
- Yield
- Sigma Level
- Capability Level
- 해석 및 권장사항

**등급 평가:**
- Cpk ≥ 2.0: 6-Sigma (Excellent)
- Cpk ≥ 1.5: 5-Sigma (Excellent)
- Cpk ≥ 1.33: 4-Sigma (Good)
- Cpk ≥ 1.0: 3-Sigma (Acceptable)
- Cpk ≥ 0.67: 2-Sigma (Poor)
- Cpk < 0.67: Incapable

### 3. 상관 분석 (Correlation)

**출력 항목:**
- Pearson 상관계수 및 P-value
- Spearman 순위 상관계수 및 P-value
- 선형 회귀 (기울기, 절편, R-squared)
- 해석 (weak/moderate/strong, positive/negative)

### 4. T-검정 (T-Test)

**지원하는 검정:**
- 일표본 T-검정 (One-Sample)
- 독립 표본 T-검정 (Independent Two-Sample)
- 대응표본 T-검정 (Paired)

**출력 항목:**
- T-statistic, P-value
- 유의수준 (alpha)
- 통계적 유의성 여부
- 신뢰구간
- 그룹별 통계

### 5. 분산분석 (ANOVA)

**출력 항목:**
- F-statistic, P-value
- Eta Squared (효과 크기)
- ANOVA 테이블 (SS, DF, MS)
- 그룹별 통계

---

## 주요 파일

### Backend
- `backend/apps/spc/models/six_sigma.py` (400줄)
- `backend/apps/spc/serializers/six_sigma.py` (200줄)
- `backend/apps/spc/services/six_sigma_tools.py` (600줄)
- `backend/apps/spc/views/six_sigma.py` (300줄)
- `backend/apps/spc/urls.py` (수정됨)

### Frontend
- `frontend/src/pages/SixSigmaDashboardPage.tsx` (200줄)
- `frontend/src/pages/SixSigmaToolsPage.tsx` (200줄)
- `frontend/src/services/sixSigmaApi.ts` (150줄)
- `frontend/src/App.tsx` (수정됨)

---

## 데이터베이스 마이그레이션

마이그레이션을 생성하고 적용하세요:

```bash
# 마이그레이션 생성
python manage.py makemigrations spc

# 마이그레이션 적용
python manage.py migrate
```

---

## 다음 단계

1. ✅ **데이터베이스 마이그레이션 실행**
   ```bash
   python manage.py makemigrations spc
   python manage.py migrate
   ```

2. ✅ **프론트엔드 빌드**
   ```bash
   cd frontend
   npm run build
   ```

3. ✅ **서버 시작**
   ```bash
   # Backend
   cd backend
   python manage.py runserver

   # Frontend
   cd frontend
   npm run dev
   ```

4. **Six Sigma 메뉴 접속**
   - 대시보드: http://localhost:5173/six-sigma
   - 통계 도구: http://localhost:5173/six-sigma/tools

---

## 사용법

### 1. 프로젝트 생성 및 관리

1. Six Sigma 대시보드 접속
2. "새 프로젝트 생성" 버튼 클릭
3. 프로젝트 정보 입력 (코드, 이름, 설명, Champion, 기간 등)
4. 각 Phase별로 단계 진행
5. 마일스톤, 문서, 리스크 관리

### 2. 통계 분석 도구 사용

1. 통계 도구 페이지 접속 (`/six-sigma/tools`)
2. 분석 도구 선택 (8개 중 하나)
3. 데이터 입력 (쉼표로 구분된 숫자)
4. 도구별 파라미터 입력
5. "분석 실행" 버튼 클릭
6. 결과 확인 및 해석

---

**완료일시**: 2026-01-11
**버전**: 1.0.0
