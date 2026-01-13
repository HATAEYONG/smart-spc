# 🚀 Smart SPC System - Quick Start Guide

## 📦 설치된 의존성 확인

```bash
cd frontend
npm install
```

핵심 라이브러리:
- ✅ react ^18.3.1
- ✅ typescript ~5.6.2
- ✅ recharts ^2.10.0
- ✅ axios ^1.7.9
- ✅ tailwindcss ^3.4.17
- ✅ lucide-react ^0.468.0

## 🎯 빠른 시작

### 1. 개발 서버 시작

```bash
npm run dev
```

### 2. API 연결 설정

`.env` 파일 생성 (선택사항 - 기본값은 `/api/v1`):

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 3. 첫 번째 API 호출 예시

```typescript
import { dashboardService } from './services';
import { DashboardSummaryDTO } from './types';

const App = () => {
  const [data, setData] = useState<DashboardSummaryDTO | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const response = await dashboardService.getSummary('2026-01');
      if (response.ok) {
        setData(response.data);
      } else {
        console.error('API Error:', response.error);
      }
    };
    fetchData();
  }, []);

  return (
    <div>
      <h1>COPQ Rate: {data?.kpis.copq_rate}</h1>
      {/* 차트는 이미 구현되어 있음 ✅ */}
    </div>
  );
};
```

## 📁 주요 파일 위치

### 타입 정의
```
frontend/src/types/
├── dashboard.ts      # 대시보드 타입
├── qcost.ts          # 품질비용 타입
├── inspection.ts     # 검사 타입
├── spc.ts            # SPC 타입
└── qa.ts             # QA/CAPA 타입
```

### API 서비스
```
frontend/src/services/
├── apiV1.ts              # API 클라이언트 베이스
├── dashboardService.ts   # 대시보드 API
├── qcostService.ts       # 품질비용 API
├── inspectionService.ts  # 검사 API
├── spcService.ts         # SPC API
└── qaService.ts          # QA/CAPA API
```

### 페이지 (차트 구현 완료 ✅)
```
frontend/src/pages/
├── DashboardPage.tsx           # Pareto Chart
├── QCostDashboardPage.tsx      # Trend Line Chart
├── COPQAnalysisPage.tsx        # Pareto Chart
├── ProcessCapabilityPage.tsx   # Histogram
├── SPCChartPage.tsx            # Control Chart
└── AdvancedChartsPage.tsx      # Advanced Control Chart
```

## 🔌 API 사용 예시

### Q-COST 입출내역 조회

```typescript
import { qcostService } from './services';

const entries = await qcostService.getEntries('2026-01-01', '2026-01-31');
if (entries.ok) {
  console.log(entries.data.results); // QCostEntryDTO[]
}
```

### 검사 실행 생성

```typescript
import { inspectionService } from './services';

const run = await inspectionService.createRun({
  lot_id: 'lot-123',
  plan_id: 'plan-456',
  step_id: 'step-789',
  sample_n: 5,
  environment: { temp: 23.5, humidity: 45 },
});

if (run.ok) {
  console.log(run.data.run_id);
}
```

### SPC 차트 생성

```typescript
import { spcService } from './services';

const chart = await spcService.createChart({
  char_id: 'char-123',
  chart_type: 'XBAR_R',
  subgroup_size: 5,
  rule_set: { nelson: [1, 2, 3] },
  status: 'ACTIVE',
});

if (chart.ok) {
  console.log(chart.data.chart_def_id);
}
```

## 🎨 차트 사용법

### 기본 Pareto Chart (이미 구현됨)

```typescript
import { BarChart, Bar, Line, XAxis, YAxis, ResponsiveContainer } from 'recharts';

// DashboardPage.tsx:318-330에서 이미 구현됨
// 데이터 형식:
const paretoData = [
  { name: '치수불량', cost: 5000000, cumulative: 40.3 },
  { name: '스크래치', cost: 3000000, cumulative: 64.5 },
  // ...
];
```

### Control Chart (이미 구현됨)

```typescript
// SPCChartPage.tsx:191-229에서 이미 구현됨
// UCL, CL, LCL ReferenceLine 포함
// 위반 포인트 AlertTriangle 아이콘으로 표시
```

## 📊 데이터 타입 예시

### DashboardSummaryDTO

```typescript
{
  period: "2026-01",
  kpis: {
    copq_rate: 0.0342,
    total_copq: 41000000,
    total_qcost: 62000000,
    oos_count: 18,
    spc_open_events: 6
  },
  top_defects: [
    { defect: "스크래치", count: 61, cost: 8000000 }
  ],
  alerts: [
    { event_id: "...", type: "TREND", severity: 4, title: "내경 추세 발생" }
  ],
  ai_insights: [
    { ai_id: "...", title: "COPQ 주요 원인", summary: "...", confidence: 0.86 }
  ]
}
```

## 🛠️ 다음 단계

### 1. 백엔드 API 구현
PostgreSQL DDL을 참조하여 FastAPI/Django/Express 등으로 API 구현

### 2. 인증 구현
```typescript
// 로그인 후 토큰 저장
localStorage.setItem('auth_token', token);

// API 클라이언트가 자동으로 토큰을 사용함 (apiV1.ts 이미 구현됨)
```

### 3. React Query 통합 (권장)
```bash
npm install @tanstack/react-query
```

```typescript
import { useQuery } from '@tanstack/react-query';
import { dashboardService } from './services';

const useDashboardSummary = (period: string) => {
  return useQuery({
    queryKey: ['dashboard', period],
    queryFn: () => dashboardService.getSummary(period),
  });
};
```

## ✅ 구현 완료 체크리스트

- [x] TypeScript 인터페이스 (5개 도메인)
- [x] API 서비스 레이어 (5개 서비스)
- [x] 차트 구현 (6개 페이지)
- [x] API 클라이언트 (Axios 래퍼)
- [x] 타입 안전성 보장
- [ ] 백엔드 API 구현
- [ ] 인증/권한 구현
- [ ] React Query 통합
- [ ] 테스트 코드

## 📞 문의 사항

추가 구현이 필요하시면:
1. SPC 재계산 로직 (의사코드)
2. Excel 업로드 기능
3. 권한 관리 (Role별 매트릭스)
4. 각 화면별 상세 구현 가이드

---

**개발 바로 시작 가능! 🎉**
