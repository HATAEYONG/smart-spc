# 와이어프레임 기반 화면 구현 완료 보고서

## 📋 구현 개요

와이어프레임(Figma용 MD) 기반으로 4개의 핵심 화면을 구현했습니다.

---

## ✅ 구현 완료 목록

### 1. 공통 컴포넌트 (4-3. 공통 컴포넌트)

#### ✅ StatusBadge (상태 배지)
**파일**: `frontend/src/components/common/StatusBadge.tsx`

지원하는 상태 타입:
- `DRAFT`: 초안 (회색)
- `ACTIVE`: 활성 (녹색)
- `HOLD`: 보류 (노란색)
- `OOS`: 규격 이탈 (빨간색)
- `OPEN`: 미해결 (주황색)
- `CLOSED`: 종료 (파란색)
- `IN_PROGRESS`: 진행중 (보라색)
- `RESOLVED`: 해결됨 (청록색)

사용 예시:
```tsx
<StatusBadge status="ACTIVE" />
<StatusBadge status="OOS" />
```

#### ✅ VersionTag (버전 태그)
**파일**: `frontend/src/components/common/VersionTag.tsx`

표시 정보:
- 리비전 번호 (예: Rev 1.0)
- 승인자 (선택)
- 승인 일자 (선택)

사용 예시:
```tsx
<VersionTag
  revNo="1.2"
  approver="김품질"
  approvedDate="2026-01-12"
/>
```

#### ✅ AIResultPanel (AI 결과 패널)
**파일**: `frontend/src/components/common/AIResultPanel.tsx`

표시 섹션:
- **근거 (Rationale)**: 체크리스트 형태
- **가정사항 (Assumptions)**: 가정 목록
- **식별된 리스크**: 확률별 색상 구분 (높음/중간/낮음)
- **신뢰도**: 0~1 사이 값, 백분율 및 레이블 표시

사용 예시:
```tsx
<AIResultPanel
  rationale={['근거1', '근거2']}
  assumptions={['가정1', '가정2']}
  risks={[{
    risk: '리스크 명',
    probability: '중간',
    mitigation: '완화 조치'
  }]}
  confidence={0.87}
/>
```

#### ✅ AuditLogButton (감사로그 버튼)
**파일**: `frontend/src/components/common/AuditLogButton.tsx`

기능:
- 감사로그 건수 배지 표시
- 다이얼로그 형태 로그 목록
- 작업자, 시간, 액션, 상세 내용 표시

사용 예시:
```tsx
<AuditLogButton
  logs={[
    {
      id: '1',
      actor: '김품질',
      timestamp: '2026-01-12T10:30:00',
      action: '항목 생성',
      details: '최초 등록'
    }
  ]}
/>
```

---

### 2. DASH-01: 통합 대시보드

**파일**: `frontend/src/pages/DashboardPage.tsx`

#### 구현된 위젯:
1. **COPQ (월간)**: ₩1,250만, 전월 대비 -0.5%
2. **COPQ Rate**: 2.4%, 목표 3.0%
3. **OOS 건수**: 23건, 전월 대비 -8건
4. **주요 불량 TOP3**: 치수불량(45), 스크래치(32), 이물(28)

#### 메인 콘텐츠:
- **Pareto 차트 미리보기**: 불량/코스트 분석 (placeholder)
- **SPC 경보 타임라인**: 최근 7일 경보 5건
  - TREND, OOS, RULE_1, RULE_2 등 표시
- **AI 인사이트 카드**: 2개
  - 치수불량 40% 차지 (신뢰도 92%)
  - 세척 공정 이물 부착률 감소 (신뢰도 87%)

#### CTA 버튼:
- 월간 리포트 생성
- 경보 상세
- CAPA 생성

---

### 3. QCOST-01: Q-COST 분류체계/항목 마스터

**파일**: `frontend/src/pages/QCostClassificationPage.tsx`

#### 화면 구조:
**좌측: 트리 구조**
- 4단계 분류 (예방/평가/내부실패/외부실패 → lvl2/lvl3)
- 드롭다운 형태 (Folder/FolderOpen 아이콘)
- 검색 기능
- 항목 선택 시 하이라이트

**우측: 항목 상세**
- 기본 정보: 항목 코드, 항목명, 관리 부서, GL 계정
- 분류 정보: lvl1/lvl2/lvl3 배지
- COPQ 여부: COPQ 대상/비대상 배지
- 단가 정보: 기준 단가 (규칙 기반 단가 산정용)
- 감사로그: AuditLogButton 컴포넌트
- 수정/삭제 버튼

#### 샘플 데이터:
- 예방비용: 품질시스템 설계비 (₩500,000)
- 평가비용: 검사원 인건비 (₩300,000)
- 내부 실패비용: 재세척 인건비 (₩150,000, COPQ)
- 외부 실패비용: 고객 클레임 비용 (COPQ)

---

### 4. INSP-01: 검수 프로세스 설계

**파일**: `frontend/src/pages/InspectionProcessDesignPage.tsx`

#### 화면 구조:
**상단: 품목/공정Flow 선택**
- 품목 선택 (드롭다운)
- 공정 Flow 선택 (드롭다운)
- 리비전 정보 (배지 + 수정 버튼)

**중앙: 공정 스텝 카드 (드래그 정렬)**
- 스텝 카드 3개:
  1. CNC 가공 (검사 지점 ✓)
     - 검사 포인트: 내경, 외경, 깊이
  2. 세척 (검사 지점 ✓)
     - 검사 포인트: 외관, 이물
  3. 조립 (검사 지점 ✓)
     - 검사 포인트: 조립 완성도, 간섭
- GripVertical 아이콘 (드래그 핸들)
- 선택 시 하이라이트

**우측: 검사 포인트 편집**
- 선택된 스텝 정보
- 검사 지점 (CTQ) 리스트
- 검사 빈도 선택 (LOT별/교대별/시간당)
- 검사 방법 선택 (치수/외관/기능)
- 샘플링 규칙 선택 (ISO 2859/전수/랜덤)
- 적용 버튼

**우측 상단: AI로 프로세스 초안 생성 버튼**
- 클릭 시 AIResultPanel 토글
- AI 추천 결과 표시 (근거, 가정, 리스크, 신뢰도 87%)

---

### 5. SPC-01: 관리도 화면

**파일**: `frontend/src/pages/SPCChartPage.tsx`

#### 화면 구조:
**상단: 필터 영역**
- 품목 선택
- 공정 선택
- CTQ 선택 (내경/외경/깊이)
- 기간 선택 (7일/30일/90일)

**중앙: 관리도 차트 영역**
- X-bar & R Chart (Recharts 사용)
- UCL/CL/LCL 참조선 (빨간색 점선/회색 점선/빨간색 점선)
- 데이터 포인트 (보라색 선)
- 위반 포인트 강조 (AlertTriangle 아이콘)
  - 높음: 빨간색
  - 중간: 주황색
  - 낮음: 노란색
- 범례: 측정값, 관리 한계, 위반 포인트

**우측: Run Rule 위반 리스트**
- 위반 3건:
  1. RULE_1: 관리 한계 벗어남 (Point 15) - 심각도 높음
  2. RULE_2: 9개 연속 중심선 상방 (Point 22) - 심각도 중간
  3. TREND: 추세 감지 (Point 28) - 심각도 낮음
- 각 위반별 상세/CAPA 버튼

#### CTA 버튼:
- 베이스라인 재설정
- 이상 이벤트 생성
- CAPA 연결

---

## 🎨 디자인 특징

### 색상 체계:
- **Primary**: Purple (#8b5cf6) - 주요 버튼, 하이라이트
- **Success**: Green - 활성 상태, 긍정적 지표
- **Warning**: Yellow/Orange - 보류, 중간 심각도
- **Error**: Red - OOS, 높은 심각도
- **Info**: Blue - 종료됨, 정보 표시

### 컴포넌트 라이브러리:
- shadcn/ui (Card, Button, Badge, Dialog, Select, Input, Tabs)
- Recharts (차트)
- Lucide React (아이콘)

### 반응형 디자인:
- Tailwind CSS Grid 사용
- `grid-cols-1 lg:grid-cols-3` 패턴
- 모바일/태블릿/데스크톱 지원

---

## 📁 파일 구조

```
frontend/src/
├── components/
│   └── common/
│       ├── StatusBadge.tsx          # 상태 배지
│       ├── VersionTag.tsx           # 버전 태그
│       ├── AIResultPanel.tsx        # AI 결과 패널
│       ├── AuditLogButton.tsx       # 감사로그 버튼
│       └── index.ts                 # 컴포넌트 export
│
├── pages/
│   ├── DashboardPage.tsx            # DASH-01 통합 대시보드
│   ├── QCostClassificationPage.tsx  # QCOST-01 분류체계 마스터
│   ├── InspectionProcessDesignPage.tsx  # INSP-01 검수 프로세스
│   ├── SPCChartPage.tsx             # SPC-01 관리도
│   ├── RunRuleAnalysisPage.tsx      # AI Run Rule 분석 (기존)
│   ├── ChatbotPage.tsx              # AI 챗봇 (기존)
│   └── ...                          # 기타 페이지
│
└── App.tsx                          # 라우팅 연결
```

---

## 🔗 라우팅 설정

| 경로 | 페이지 | 설명 |
|------|--------|------|
| `/` | DashboardPage | 통합 대시보드 (메인) |
| `/qcost-classification` | QCostClassificationPage | Q-COST 분류체계 |
| `/inspection-process` | InspectionProcessDesignPage | 검수 프로세스 설계 |
| `/spc-chart` | SPCChartPage | SPC 관리도 |
| `/run-rules` | RunRuleAnalysisPage | AI Run Rule 분석 |
| `/chatbot` | ChatbotPage | AI 챗봇 |

---

## 🚀 다음 단계 (미래 개발 사항)

### 1. INSP-02: 검수 기준표/체크리스트
- 탭1: 기준표 (표 형태, PDF/Excel 내보내기)
- 탭2: 체크리스트 (모바일 폼 미리보기)
- 탭3: 사진/증빙 규칙
- AI 생성 → 초안 → 승인 워크플로우

### 2. SAMPLE-01: 샘플링 검사 설정
- 샘플링 규칙 마스터 (ISO/ANSI/사내)
- LOT 크기 입력 → 샘플수/Ac/Re 자동 산출
- 적용 대상 매핑

### 3. QA-01: QA 진단(요구사항/GAP)
- 요구사항 트리 (ISO/IATF/사내/고객)
- 진단 결과 (적합/부적합/개선)
- Finding 상세: AS-IS/TO-BE/증빙/담당/기한
- AI GAP 요약/개선안

### 4. RPT-01: 리포트 생성기
- 리포트 유형 선택
- 데이터 범위 선택 → AI 작성
- 편집기 (문단/표/차트 자동 삽입 자리)
- 승인 후 PDF 생성 + 배포

---

## ✅ 완료 상태

| 화면 | 상태 | 파일 |
|------|------|------|
| 공통 컴포넌트 | ✅ 완료 | `components/common/*` |
| DASH-01 통합 대시보드 | ✅ 완료 | `pages/DashboardPage.tsx` |
| QCOST-01 분류체계 | ✅ 완료 | `pages/QCostClassificationPage.tsx` |
| INSP-01 검수 프로세스 | ✅ 완료 | `pages/InspectionProcessDesignPage.tsx` |
| SPC-01 관리도 | ✅ 완료 | `pages/SPCChartPage.tsx` |
| INSP-02 기준표/체크리스트 | ⏳ 예정 | - |
| SAMPLE-01 샘플링 | ⏳ 예정 | - |
| QA-01 QA 진단 | ⏳ 예정 | - |
| RPT-01 리포트 생성기 | ⏳ 예정 | - |

---

## 🎯 핵심 기능

### AI 통합
- **AIResultPanel**: 모든 AI 응답에 표준화된 UI
- **신뢰도 표시**: 0~1 사이 값 → 백분율 + 레이블
- **근거/가정/리스크**: 체계적인 정보 제공
- **AI 생성 버튼**: 프로세스 초안, 리포트 등

### 데이터 시각화
- **위젯**: COPQ, COPQ Rate, OOS 건수, TOP 불량
- **차트**: Pareto, SPC 관리도 (X-bar & R)
- **타임라인**: SPC 경보 (최근 7일)
- **트리 구조**: Q-COST 분류 (3단계)

### 상호작용
- **드래그 앤 드롭**: 공정 스텝 순서 변경
- **필터**: 품목/공정/CTQ/기간
- **검색**: 항목 검색
- **다이얼로그**: 감사로그, 상세 보기
- **토글**: AI 패널 표시/숨기기

---

**구현 일자**: 2026-01-12
**버전**: 1.0.0
**상태**: ✅ 완료 (5개 핵심 화면)
