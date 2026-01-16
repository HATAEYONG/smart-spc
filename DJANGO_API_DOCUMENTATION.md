# Django REST API 문서
# Smart SPC Backend API Documentation

## 📋 목차
1. [API 개요](#api-개요)
2. [인증](#인증)
3. [품질 이슈 API](#품질-이슈-api)
4. [설비 API](#설비-api)
5. [치공구 API](#치공구-api)
6. [작업지시 API](#작업지시-api)
7. [ERP 연계 API](#erp-연계-api)
8. [에러 처리](#에러-처리)

---

## API 개요

### 기본 정보
- **Base URL**: `http://localhost:8000/api/v1`
- **데이터 형식**: JSON
- **인증 방식**: JWT Bearer Token (선택 사항)
- **타임존**: Asia/Seoul (UTC+9)

### 응답 형식
```json
{
  "count": 100,
  "next": null,
  "previous": null,
  "results": [...]
}
```

---

## 인증

### JWT 토큰 발급
```http
POST /api-token-auth/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

### 응답
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 헤더에 토큰 포함
```http
Authorization: Bearer <access_token>
```

---

## 품질 이슈 API

### 목록 조회
```http
GET /api/v1/quality/issues/
```

**Query Parameters:**
- `status`: OPEN, INVESTIGATING, IN_PROGRESS, RESOLVED, CLOSED
- `severity`: LOW, MEDIUM, HIGH, CRITICAL
- `search`: 검색어 (issue_number, title, product_code)
- `ordering`: -reported_date, severity, status
- `page`: 페이지 번호

**예시:**
```http
GET /api/v1/quality/issues/?status=OPEN&severity=HIGH&page=1
```

### 상세 조회
```http
GET /api/v1/quality/issues/{id}/
```

### 생성
```http
POST /api/v1/quality/issues/
Content-Type: application/json

{
  "issue_number": "QI-2025-001",
  "title": "품질 이슈 제목",
  "description": "상세 설명",
  "product_code": "P-1001",
  "product_name": "제품 A",
  "defect_type": "치수 불량",
  "severity": "HIGH",
  "department": "생산부",
  "defect_quantity": 10,
  "cost_impact": 50000,
  "responsible_person": "김담당자",
  "target_resolution_date": "2025-02-01"
}
```

### 수정
```http
PUT /api/v1/quality/issues/{id}/
Content-Type: application/json

{
  "status": "RESOLVED",
  "severity": "MEDIUM",
  "completion_notes": "해결 완료"
}
```

### 삭제
```http
DELETE /api/v1/quality/issues/{id}/
```

### 4M 분석 조회
```http
GET /api/v1/quality/issues/{id}/analyses_4m/
```

### 4M 분석 설정
```http
POST /api/v1/quality/issues/{id}/set_analyses_4m/
Content-Type: application/json

{
  "analyses": [
    {
      "category": "MAN",
      "description": "작업자 숙련도 부족"
    },
    {
      "category": "MACHINE",
      "description": "설비 정밀도 저하"
    },
    {
      "category": "MATERIAL",
      "description": "원자재 품질 문제"
    },
    {
      "category": "METHOD",
      "description": "작업 절차 미준수"
    }
  ]
}
```

### 8단계 문제 해결 조회
```http
GET /api/v1/quality/issues/{id}/solving_steps/
```

### 8단계 문제 해결 설정
```http
POST /api/v1/quality/issues/{id}/set_solving_steps/
Content-Type: application/json

{
  "steps": [
    {
      "step_number": 1,
      "step_name": "문제 정의",
      "content": "문제를 명확히 정의",
      "completed": true
    },
    {
      "step_number": 2,
      "step_name": "잠시적 대책",
      "content": "즉시 적용할 대책 수립",
      "completed": false
    }
    // ... 8단계
  ]
}
```

### 단계 완료 처리
```http
POST /api/v1/quality/issues/{id}/complete_step/
Content-Type: application/json

{
  "step_number": 1
}
```

### 통계
```http
GET /api/v1/quality/issues/statistics/
```

**응답:**
```json
{
  "total": 50,
  "by_status": {
    "OPEN": 10,
    "INVESTIGATING": 15,
    "IN_PROGRESS": 10,
    "RESOLVED": 10,
    "CLOSED": 5
  },
  "by_severity": {
    "LOW": 20,
    "MEDIUM": 20,
    "HIGH": 8,
    "CRITICAL": 2
  },
  "open_issues": 35
}
```

---

## 설비 API

### 목록 조회
```http
GET /api/v1/equipment/equipment/
```

**Query Parameters:**
- `status`: OPERATIONAL, MAINTENANCE, DAMAGED, RETIRED
- `type`: 설비 유형
- `search`: 검색어 (code, name, manufacturer)
- `ordering`: code, name, health_score

### 상세 조회
```http
GET /api/v1/equipment/equipment/{id}/
```

### 건강 점수 조회
```http
GET /api/v1/equipment/equipment/{id}/health/
```

**응답:**
```json
{
  "health_score": 85,
  "predicted_failure_days": 180,
  "status": "warning"
}
```

### 부품 조회
```http
GET /api/v1/equipment/equipment/{id}/parts/
```

### 매뉴얼 조회
```http
GET /api/v1/equipment/equipment/{id}/manuals/
```

### 수리 이력 조회
```http
GET /api/v1/equipment/equipment/{id}/repair_histories/
```

### 예방 보전 작업 조회
```http
GET /api/v1/equipment/equipment/{id}/pm_tasks/
```

### 통계
```http
GET /api/v1/equipment/equipment/statistics/
```

---

## 예방 보전 API

### 목록 조회
```http
GET /api/v1/equipment/preventive-maintenance/
```

**Query Parameters:**
- `status`: PENDING, ASSIGNED, IN_PROGRESS, COMPLETED, OVERDUE
- `frequency`: DAILY, WEEKLY, MONTHLY, QUARTERLY, YEARLY
- `priority`: LOW, MEDIUM, HIGH, CRITICAL
- `equipment`: 설비 ID

### 상세 조회
```http
GET /api/v1/equipment/preventive-maintenance/{id}/
```

### 작업 완료 처리
```http
POST /api/v1/equipment/preventive-maintenance/{id}/complete/
Content-Type: application/json

{
  "completion_notes": "정기 점검 완료. 이상 없음."
}
```

### 지연된 작업 조회
```http
GET /api/v1/equipment/preventive-maintenance/overdue/
```

---

## 치공구 API

### 목록 조회
```http
GET /api/v1/tools/tools/
```

**Query Parameters:**
- `status`: AVAILABLE, IN_USE, MAINTENANCE, DAMAGED, RETIRED
- `type`: 치공구 유형
- `search`: 검색어 (code, name, manufacturer)

### 상세 조회
```http
GET /api/v1/tools/tools/{id}/
```

### 수명 예측
```http
GET /api/v1/tools/tools/{id}/prediction/
```

**응답:**
```json
{
  "tool_code": "TL-001",
  "tool_name": "절삭 공구 1형",
  "usage_percentage": 75.5,
  "predicted_remaining_days": 45,
  "risk_level": "WARNING",
  "recommendation": "교체 준비 필요",
  "optimal_replacement_date": "2025-03-01"
}
```

### 수리 이력 조회
```http
GET /api/v1/tools/tools/{id}/repair_histories/
```

### 통계
```http
GET /api/v1/tools/tools/statistics/
```

---

## 작업지시 API

### 목록 조회
```http
GET /api/v1/work-orders/work-orders/
```

**Query Parameters:**
- `status`: PENDING, ASSIGNED, IN_PROGRESS, COMPLETED, CANCELLED, ON_HOLD
- `priority`: LOW, MEDIUM, HIGH, CRITICAL
- `equipment`: 설비 ID
- `assigned_to`: 담당자 ID
- `search`: 검색어 (order_number, product_code, product_name)

### 상세 조회
```http
GET /api/v1/work-orders/work-orders/{id}/
```

### 생성
```http
POST /api/v1/work-orders/work-orders/
Content-Type: application/json

{
  "order_number": "WO-20250100-1",
  "product_code": "P-1001",
  "product_name": "제품 A",
  "quantity": 1000,
  "priority": "HIGH",
  "start_date": "2025-01-20",
  "target_end_date": "2025-02-01",
  "equipment": 1,
  "assigned_to": 1,
  "estimated_cost": 5000000,
  "notes": "긴급 생산"
}
```

### 수정
```http
PATCH /api/v1/work-orders/work-orders/{id}/
Content-Type: application/json

{
  "status": "IN_PROGRESS",
  "progress_percentage": 50,
  "completed_quantity": 500
}
```

### 위험도 분석
```http
GET /api/v1/work-orders/work-orders/{id}/analyze_risk/
```

**응답:**
```json
{
  "order_number": "WO-20250100-1",
  "predicted_completion_risk": "HIGH",
  "risk_reasons": [
    "설비 건강 점수 낮음 (60점 미만)",
    "치공구 TL-001 잔존 수명 부족"
  ]
}
```

### 진행 상황 로그 조회
```http
GET /api/v1/work-orders/work-orders/{id}/progress_logs/
```

### 진행 상황 추가
```http
POST /api/v1/work-orders/work-orders/{id}/add_progress/
Content-Type: application/json

{
  "status": "IN_PROGRESS",
  "progress_percentage": 75,
  "completed_quantity": 750,
  "notes": "진행 상황 업데이트"
}
```

### 통계
```http
GET /api/v1/work-orders/work-orders/statistics/
```

---

## ERP 연계 API

### 목록 조회
```http
GET /api/v1/integration/erp-integrations/
```

### 상세 조회
```http
GET /api/v1/integration/erp-integrations/{id}/
```

### 생성
```http
POST /api/v1/integration/erp-integrations/
Content-Type: application/json

{
  "name": "SAP ERP",
  "system_type": "ERP",
  "description": "SAP ERP 연동",
  "endpoint_url": "https://api.sap.com/v1",
  "auth_method": "API_KEY",
  "api_key": "your_api_key_here",
  "sync_frequency_minutes": 60,
  "auto_sync": true,
  "data_types": ["생산주문", "자재정보", "BOM"]
}
```

### 연결 테스트
```http
POST /api/v1/integration/erp-integrations/{id}/test_connection/
```

### 수동 동기화 실행
```http
POST /api/v1/integration/erp-integrations/{id}/sync/
```

### 동기화 이력 조회
```http
GET /api/v1/integration/erp-integrations/{id}/sync_history/
```

### 통계
```http
GET /api/v1/integration/erp-integrations/statistics/
```

---

## 자체 입력 API

### 목록 조회
```http
GET /api/v1/integration/manual-inputs/
```

**Query Parameters:**
- `inspection_type`: INCOMING, PROCESS, FINAL, OUTGOING
- `status`: PENDING, APPROVED, REJECTED
- `department`: 부서명
- `search`: 검색어 (record_number, product_code, product_name)

### 상세 조회
```http
GET /api/v1/integration/manual-inputs/{id}/
```

### 생성
```http
POST /api/v1/integration/manual-inputs/
Content-Type: application/json

{
  "record_number": "QR-20250115-001",
  "inspection_type": "FINAL",
  "inspection_date": "2025-01-15",
  "product_code": "P-1001",
  "product_name": "제품 A",
  "batch_number": "B20250115001",
  "lot_number": "L20250115001",
  "sample_size": 50,
  "defect_count": 2,
  "defect_rate": 4.0,
  "characteristics": [
    {
      "name": "길이",
      "target": 100.0,
      "tolerance": 0.5,
      "measured": 100.2,
      "status": "OK"
    }
  ],
  "defect_details": [
    {
      "type": "긁힘",
      "count": 2,
      "description": "표면 긁힘"
    }
  ],
  "department": "품질부",
  "notes": "정상 검사 완료"
}
```

### 수정
```http
PATCH /api/v1/integration/manual-inputs/{id}/
Content-Type: application/json

{
  "defect_count": 3,
  "defect_rate": 6.0,
  "notes": "수정된 불량 수"
}
```

### 승인 처리
```http
POST /api/v1/integration/manual-inputs/{id}/approve/
```

### 반려 처리
```http
POST /api/v1/integration/manual-inputs/{id}/reject/
Content-Type: application/json

{
  "notes": "검사 기준 불일치"
}
```

### 통계
```http
GET /api/v1/integration/manual-inputs/statistics/
```

---

## 에러 처리

### 에러 응답 형식
```json
{
  "detail": "에러 메시지",
  "error_code": "VALIDATION_ERROR"
}
```

### HTTP 상태 코드
- `200 OK`: 성공
- `201 Created`: 생성 성공
- `400 Bad Request`: 요청 데이터 오류
- `401 Unauthorized`: 인증 실패
- `403 Forbidden`: 권한 없음
- `404 Not Found`: 리소스 없음
- `500 Internal Server Error`: 서버 에러

---

## 헬스체크

### 서버 상태 확인
```http
GET /health/
```

**응답:**
```json
{
  "status": "healthy",
  "service": "Smart SPC API",
  "version": "1.0.0"
}
```

---

## 테스트 예시 (cURL)

### 1. 품질 이슈 목록 조회
```bash
curl -X GET "http://localhost:8000/api/v1/quality/issues/?status=OPEN"
```

### 2. 새 품질 이슈 생성
```bash
curl -X POST "http://localhost:8000/api/v1/quality/issues/" \
  -H "Content-Type: application/json" \
  -d '{
    "issue_number": "QI-2025-001",
    "title": "품질 이슈 테스트",
    "product_code": "P-1001",
    "product_name": "제품 A",
    "defect_type": "치수 불량",
    "severity": "HIGH",
    "department": "생산부",
    "defect_quantity": 5,
    "cost_impact": 100000,
    "target_resolution_date": "2025-02-01"
  }'
```

### 3. 설비 목록 조회
```bash
curl -X GET "http://localhost:8000/api/v1/equipment/equipment/?status=OPERATIONAL"
```

### 4. 설비 건강 점수 확인
```bash
curl -X GET "http://localhost:8000/api/v1/equipment/equipment/1/health/"
```

### 5. 작업지시 생성
```bash
curl -X POST "http://localhost:8000/api/v1/work-orders/work-orders/" \
  -H "Content-Type: application/json" \
  -d '{
    "order_number": "WO-TEST-001",
    "product_code": "P-1001",
    "product_name": "제품 A",
    "quantity": 100,
    "priority": "MEDIUM",
    "start_date": "2025-01-20",
    "target_end_date": "2025-01-30",
    "equipment": 1
  }'
```

### 6. 치공구 수명 예측
```bash
curl -X GET "http://localhost:8000/api/v1/tools/tools/1/prediction/"
```

### 7. ERP 연결 테스트
```bash
curl -X POST "http://localhost:8000/api/v1/integration/erp-integrations/1/test_connection/"
```

### 8. 자체 입력 생성
```bash
curl -X POST "http://localhost:8000/api/v1/integration/manual-inputs/" \
  -H "Content-Type: application/json" \
  -d '{
    "record_number": "QR-TEST-001",
    "inspection_type": "FINAL",
    "inspection_date": "2025-01-15",
    "product_code": "P-1001",
    "product_name": "제품 A",
    "sample_size": 30,
    "defect_count": 0,
    "defect_rate": 0.0,
    "department": "품질부"
  }'
```

---

## 프론트엔드 연동 예시

### React + TypeScript
```typescript
import { djangoApi, type QualityIssue } from '@/services/api';

// 품질 이슈 목록 조회
const fetchIssues = async () => {
  const data = await djangoApi.qualityIssues.list({ status: 'OPEN' });
  console.log(data.results); // QualityIssue[]
};

// 새 품질 이슈 생성
const createIssue = async () => {
  const newIssue = await djangoApi.qualityIssues.create({
    issue_number: 'QI-2025-001',
    title: '새 이슈',
    product_code: 'P-1001',
    product_name: '제품 A',
    defect_type: '치수 불량',
    severity: 'HIGH',
    department: '생산부',
    defect_quantity: 5,
    cost_impact: 100000,
    target_resolution_date: '2025-02-01'
  });
  console.log(newIssue);
};

// 설비 통계 조회
const fetchEquipmentStats = async () => {
  const stats = await djangoApi.equipment.statistics();
  console.log(stats);
};
```

---

## 데이터베이스 스키마

### 테이블 목록
1. **quality_issues**: 품질 이슈
2. **issue_analysis_4m**: 4M 분석
3. **problem_solving_steps**: 8단계 문제 해결
4. **equipment**: 설비 마스터
5. **equipment_parts**: 설비 부품
6. **equipment_manuals**: 설비 매뉴얼
7. **equipment_repair_histories**: 설비 수리 이력
8. **preventive_maintenances**: 예방 보전
9. **tools**: 치공구
10. **tool_repair_histories**: 치공구 수리 이력
11. **work_orders**: 작업지시
12. **work_order_tools**: 작업지시-치공구 연결
13. **work_order_progress**: 작업지시 진행 상황
14. **erp_integrations**: ERP 연계
15. **integration_histories**: 동기화 이력
16. **manual_quality_inputs**: 자체 입력

---

## 주의 사항

1. **날짜 형식**: 모든 날짜는 `YYYY-MM-DD` 형식
2. **날짜시간 형식**: 모든 날짜시간은 `YYYY-MM-DDTHH:MM:SS` 형식
3. **타임존**: Asia/Seoul (UTC+9)
4. **페이지 크기**: 기본 20개, 최대 100개
5. **정렬**: `-` prefix로 내림차순 (예: `-reported_date`)

---

**마지막 업데이트**: 2025-01-16
**버전**: v1.0.0
**작성자**: Claude Code
