# SPC 품질관리 시스템 사용 가이드

## 목차
1. [시스템 개요](#시스템-개요)
2. [빠른 시작](#빠른-시작)
3. [주요 기능](#주요-기능)
4. [페이지별 사용법](#페이지별-사용법)
5. [API 사용법](#api-사용법)
6. [문제 해결](#문제-해결)

---

## 시스템 개요

### SPC (Statistical Process Control)란?
SPC는 통계적 공정 관리로, 제조 공정에서 데이터를 수집하고 분석하여 품질을 관리하는 방법론입니다.

### 주요 기능
- **X-bar & R 관리도**: 평균과 범위를 모니터링
- **공정능력 분석**: Cp, Cpk 지수로 공정 능력 평가
- **Run Rule 분석**: Western Electric Rules로 이상 패턴 감지
- **CUSUM & EWMA**: 작은 변동 감지를 위한 고급 관리도
- **AI 챗봇**: 품질 관련 질문 자동 응대
- **실시간 알림**: WebSocket 기반 실시간 품질 경고

---

## 빠른 시작

### 1. 서버 시작

**백엔드 서버 (Django)**
```bash
cd backend
venv\Scripts\activate
python manage.py runserver 8000
```

**프론트엔드 서버 (React)**
```bash
cd frontend
npm run dev
```

### 2. 접속
- **메인 대시보드**: http://localhost:3000
- **API 문서**: http://localhost:8000/swagger/

### 3. 샘플 데이터 생성
```bash
cd backend
venv\Scripts\activate
python generate_sample_data.py
```

---

## 주요 기능

### 📊 X-bar & R 관리도
- **목적**: 공정의 평균과 산포를 실시간 모니터링
- **UCL/LCL**: 관리 상한/하한선 자동 계산
- **규격 이탈**: USL/LSL 초과시 자동 경고

### 📈 공정능력 분석
- **Cp**: 공정이 규격 내에 들어갈 수 있는 능력
- **Cpk**: 공정이 중심에서 벗어나지 않고 규격 내에 들어갈 능력
  - Cpk ≥ 2.0: 우수 (Six Sigma 수준)
  - Cpk ≥ 1.67: 양호
  - Cpk ≥ 1.33: 보통
  - Cpk < 1.0: 부적합

### 🔍 Run Rule 분석
Western Electric 8가지 규칙으로 공정 이상 감지:
1. UCL/LCL 벗어남
2. 연속 9개 점이 중심선 한쪽
3. 연속 6개 점이 증가/감소
4. 연속 14개 점이 교대로 증감
5. 연속 3개 중 2개가 2σ 벗어남
6. 연속 5개 중 4개가 1σ 벗어남
7. 연속 15개 점이 1σ 이내
8. 연속 8개 점이 1σ 밖

---

## 페이지별 사용법

### 1. 대시보드 (Dashboard)

**URL**: http://localhost:3000/

**기능**:
- 제품 선택으로 품질 요약 확인
- 실시간 경고 알림
- 전체 제품 목록 및 통계

**사용법**:
1. 제품 선택 드롭다운에서 제품 선택
2. 제품 품질 요약에서 통계 확인
3. 최근 경고에서 우선순위별 경고 확인

### 2. 공정능력 분석 (Process Capability)

**URL**: http://localhost:3000/capability

**기능**:
- Cp, Cpk, Pp, Ppk 지수 계산
- 정규성 검정
- 공정능력 등급 평가

**사용법**:
1. 제품 선택
2. 분석 결과 확인:
   - Cp, Cpk 값
   - 평균, 표준편차
   - 정규성 만족 여부
   - 등급 및 해석

**해석 가이드**:
```
Cpk ≥ 2.0  → 우수 (Six Sigma)
Cpk ≥ 1.67 → 양호
Cpk ≥ 1.33 → 보통
Cpk ≥ 1.0  → 미흡
Cpk < 1.0   → 부적합 (즉시 개선 필요)
```

### 3. 데이터 입력 (Data Entry)

**URL**: http://localhost:3000/data-entry

**기능**:
- 수동 측정값 입력
- CSV 일괄 입력
- 실시간 규격 체크

**수동 입력**:
1. 제품 선택
2. 측정값 입력
3. 샘플 번호, 부분군 번호 입력
4. 검사자, 기계 ID 등 선택사항 입력
5. "데이터 등록" 클릭

**일괄 입력 (CSV)**:
```
형식: 측정값, 샘플번호, 부분군번호
예시:
10.2, 1, 1
10.1, 2, 1
10.3, 3, 1
```

### 4. Run Rule 분석

**URL**: http://localhost:3000/run-rules

**기능**:
- Western Electric Rules 위반 감지
- 규칙별 위반 현황
- 미해결 경고 관리

**사용법**:
1. 제품 선택
2. 위반 목록 확인
3. Western Electric Rules 참조

### 5. AI 챗봇 (Chatbot)

**URL**: http://localhost:3000/chatbot

**기능**:
- 품질 관련 질문 응대
- 제품별 공정능력 조회
- 개선 방안 제안

**질문 예시**:
- "제품 1의 공정능력은 어떤가요?"
- "최근 품질 문제를 알려주세요"
- "공정 개선 방안을 제안해주세요"

### 6. 보고서 (Reports)

**URL**: http://localhost:3000/reports

**기능**:
- 일일/주간/월간 보고서 생성
- JSON/Markdown 내보내기

**사용법**:
1. 보고서 유형 선택 (일일/주간/월간/사용자 정의)
2. 날짜 범위 설정
3. 형식 선택 (JSON/Markdown)
4. "보고서 생성" 클릭
5. 미리보기 확인 후 다운로드

### 7. 고급 관리도 (Advanced Charts)

**URL**: http://localhost:3000/advanced-charts

**기능**:
- **CUSUM**: 작은 편차 감지 (누적 합)
- **EWMA**: 지수 가중 이동 평균
- 두 방식 비교 분석

**CUSUM 파라미터**:
- **K (참조값)**: 0.5 (기본값)
- **H (결정 간격)**: 5.0 (기본값)

**EWMA 파라미터**:
- **Lambda (가중치)**: 0.2 (기본값, 0~1)
- **L (제한 계수)**: 3.0 (기본값)

**사용법**:
1. 제품 선택
2. 차트 유형 선택 (CUSUM/EWMA)
3. 파라미터 조정 (선택사항)
4. "Calculate" 클릭
5. "Compare"로 두 방식 비교

---

## API 사용법

### Base URL
```
http://localhost:8000/api/spc/
```

### 주요 엔드포인트

#### 1. 제품 목록 조회
```http
GET /api/spc/products/
```

**응답**:
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "product_code": "BOLT-M10",
      "product_name": "M10 볼트",
      "usl": 10.5,
      "lsl": 9.5,
      "target_value": 10.0,
      "unit": "mm"
    }
  ]
}
```

#### 2. 측정 데이터 생성
```http
POST /api/spc/measurements/
Content-Type: application/json

{
  "product": 1,
  "measurement_value": 10.15,
  "sample_number": 1,
  "subgroup_number": 1,
  "measured_by": "inspector"
}
```

#### 3. 공정능력 분석
```http
GET /api/spc/process-capability/?product=1
```

#### 4. 품질 경고 목록
```http
GET /api/spc/alerts/
```

#### 5. CUSUM 계산
```http
POST /api/spc/advanced-charts/calculate/

{
  "product_id": 1,
  "chart_type": "CUSUM",
  "k": 0.5,
  "h": 5.0
}
```

---

## 문제 해결

### 백엔드가 시작되지 않음

**문제**: `ModuleNotFoundError: No module named 'django'`

**해결**:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 프론트엔드가 시작되지 않음

**문제**: `command not found: npm`

**해결**:
```bash
cd frontend
npm install
npm run dev
```

### API 500 에러

**원인**: 데이터베이스 마이그레이션 안 됨

**해결**:
```bash
cd backend
python manage.py migrate
```

### CORS 에러

**문제**: 브라우저 콘솔에 CORS 에러

**해결**: `backend/config/settings/dev.py` 확인
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

### 빈 페이지가 나옴

**해결**:
1. 브라우저 개발자 도구 콘솔 확인
2. 네트워크 탭에서 API 요청 확인
3. 백엔드 서버가 실행 중인지 확인

### 데이터가 안 보임

**해결**:
```bash
cd backend
python generate_sample_data.py
```

---

## 추가 설정

### WebSocket 실시간 알림 활성화

**설정 필요**: 이미 구현되어 있음

**사용법**:
```typescript
import { connectNotifications } from './services/websocket';

// 연결 시작
const ws = connectNotifications();

// 이벤트 리스너
ws.on('alert', (data) => {
  console.log('새 경고:', data);
});
```

### AI 챗봇 LLM 연동

**현재**: 데모 모드 (랜덤 응답)

**실제 LLM 연결 방법**:
1. `backend/apps/spc/services/llm_service.py` 수정
2. OpenAI/Anthropic API 키 추가
3. 프롬프트 엔지니어링

---

## 팁 모음

### 데이터 품질 유지
- 최소 25개 샘플 (5개 × 5 subgroup)
- 정기적으로 데이터 수집
- 이상값은 즉시 조사

### 공정능력 개선
1. Cpk < 1.33: 변동 원인 파악
2. 공정 중심 조정 (평균 ↔ 목표값)
3. 산포 감소 (표준편차 축소)

### Run Rule 위반 대응
1. RULE_1 (UCL/LCL 벗어남): 즉시 조사
2. RULE_2 (9개 연속 한쪽): 공정 이동 확인
3. RULE_3 (6개 연속 증감): 트렌드 분석

---

## 지원 및 문의

**API 문서**: http://localhost:8000/swagger/
**Django Admin**: http://localhost:8000/admin/

---

## 라이선스

이 프로젝트는 상업적 및 교육적 목적으로 자유롭게 사용할 수 있습니다.

---

*마지막 업데이트: 2026-01-11*
