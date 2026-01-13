# SPC 시스템 API 문서

## Base URL
```
개발: http://localhost:8000/api/spc/
프로덕션: https://api.yourdomain.com/api/spc/
```

## 인증
현재 인증이 필요하지 않습니다 (개발 모드).

---

## 목차
1. [Products](#1-products)
2. [Measurements](#2-measurements)
3. [Control Charts](#3-control-charts)
4. [Process Capability](#4-process-capability)
5. [Quality Alerts](#5-quality-alerts)
6. [Run Rules](#6-run-rules)
7. [Advanced Charts](#7-advanced-charts)
8. [Reports](#8-reports)
9. [Chatbot](#9-chatbot)

---

## 1. Products

### 1.1 제품 목록 조회

```http
GET /api/spc/products/
```

**Query Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| page | integer | No | 페이지 번호 |
| page_size | integer | No | 페이지당 개수 (기본값: 20) |

**Response 200**:
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "product_code": "BOLT-M10",
      "product_name": "M10 볼트",
      "description": "직경 10mm 볼트",
      "usl": 10.5,
      "lsl": 9.5,
      "target_value": 10.0,
      "unit": "mm",
      "is_active": true,
      "created_at": "2026-01-11T17:12:54Z",
      "updated_at": "2026-01-11T17:12:54Z"
    }
  ]
}
```

### 1.2 제품 상세 조회

```http
GET /api/spc/products/{id}/
```

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | integer | Yes | Product ID |

**Response 200**:
```json
{
  "id": 1,
  "product_code": "BOLT-M10",
  "product_name": "M10 볼트",
  "description": "직경 10mm 볼트",
  "usl": 10.5,
  "lsl": 9.5,
  "target_value": 10.0,
  "unit": "mm",
  "is_active": true,
  "created_at": "2026-01-11T17:12:54Z",
  "updated_at": "2026-01-11T17:12:54Z"
}
```

### 1.3 제품 요약 정보

```http
GET /api/spc/products/{id}/summary/
```

**Response 200**:
```json
{
  "product_code": "BOLT-M10",
  "product_name": "M10 볼트",
  "statistics": {
    "total_measurements": 150,
    "average": 10.0961,
    "std_dev": 0.1167,
    "min": 9.82,
    "max": 10.35,
    "out_of_spec_count": 2,
    "out_of_spec_rate": 1.33
  },
  "capability": {
    "cp": 2.131,
    "cpk": 1.703,
    "analyzed_at": "2026-01-11T17:13:00Z"
  },
  "latest_measurement": {
    "id": 150,
    "value": 10.12,
    "measured_at": "2026-01-11T19:07:25Z"
  }
}
```

### 1.4 제품 생성

```http
POST /api/spc/products/
Content-Type: application/json
```

**Request Body**:
```json
{
  "product_code": "PRODUCT-001",
  "product_name": "새 제품",
  "description": "제품 설명",
  "usl": 10.5,
  "lsl": 9.5,
  "target_value": 10.0,
  "unit": "mm"
}
```

**Response 201**:
```json
{
  "id": 4,
  "product_code": "PRODUCT-001",
  "product_name": "새 제품",
  "description": "제품 설명",
  "usl": 10.5,
  "lsl": 9.5,
  "target_value": 10.0,
  "unit": "mm",
  "is_active": true,
  "created_at": "2026-01-11T20:00:00Z",
  "updated_at": "2026-01-11T20:00:00Z"
}
```

---

## 2. Measurements

### 2.1 측정값 목록 조회

```http
GET /api/spc/measurements/
```

**Query Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| product | integer | No | Product ID |
| page | integer | No | 페이지 번호 |
| page_size | integer | No | 페이지당 개수 |

**Response 200**:
```json
{
  "count": 150,
  "results": [
    {
      "id": 1,
      "product": 1,
      "product_code": "BOLT-M10",
      "measurement_value": 10.12,
      "sample_number": 1,
      "subgroup_number": 1,
      "is_within_spec": true,
      "is_within_control": true,
      "measured_at": "2026-01-11T14:07:21Z",
      "measured_by": "inspector"
    }
  ]
}
```

### 2.2 측정값 생성

```http
POST /api/spc/measurements/
Content-Type: application/json
```

**Request Body**:
```json
{
  "product": 1,
  "measurement_value": 10.15,
  "sample_number": 151,
  "subgroup_number": 31,
  "measured_by": "inspector",
  "machine_id": "MACHINE-01",
  "lot_number": "LOT-2026-001",
  "remarks": "정상 측정"
}
```

**Response 201**:
```json
{
  "id": 151,
  "product": 1,
  "measurement_value": 10.15,
  "sample_number": 151,
  "subgroup_number": 31,
  "is_within_spec": true,
  "is_within_control": true,
  "measured_at": "2026-01-11T20:00:00Z",
  "measured_by": "inspector"
}
```

### 2.3 일괄 측정값 생성

```http
POST /api/spc/measurements/bulk_create/
Content-Type: application/json
```

**Request Body**:
```json
{
  "measurements": [
    {
      "product": 1,
      "measurement_value": 10.12,
      "sample_number": 1,
      "subgroup_number": 1,
      "measured_by": "inspector"
    },
    {
      "product": 1,
      "measurement_value": 10.08,
      "sample_number": 2,
      "subgroup_number": 1,
      "measured_by": "inspector"
    }
  ]
}
```

**Response 201**:
```json
{
  "created": 2,
  "failed": 0,
  "errors": []
}
```

---

## 3. Control Charts

### 3.1 관리도 목록 조회

```http
GET /api/spc/control-charts/
```

**Query Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| product | integer | No | Product ID |

**Response 200**:
```json
{
  "results": [
    {
      "id": 1,
      "product": 1,
      "product_code": "BOLT-M10",
      "chart_type": "XBAR_R",
      "sample_size": 5,
      "xbar_ucl": 10.1756,
      "xbar_cl": 10.0961,
      "xbar_lcl": 10.0166,
      "r_ucl": 0.4588,
      "r_cl": 0.2582,
      "r_lcl": 0.0576,
      "created_at": "2026-01-11T17:13:00Z"
    }
  ]
}
```

### 3.2 관리도 생성

```http
POST /api/spc/control-charts/generate/
Content-Type: application/json
```

**Request Body**:
```json
{
  "product_id": 1,
  "chart_type": "XBAR_R",
  "sample_size": 5
}
```

**Response 201**:
```json
{
  "id": 2,
  "product": 1,
  "chart_type": "XBAR_R",
  "xbar_ucl": 10.1756,
  "xbar_cl": 10.0961,
  "xbar_lcl": 10.0166,
  "r_ucl": 0.4588,
  "r_cl": 0.2582,
  "r_lcl": 0.0576
}
```

---

## 4. Process Capability

### 4.1 공정능력 분석 조회

```http
GET /api/spc/process-capability/
```

**Query Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| product | integer | No | Product ID |

**Response 200**:
```json
{
  "results": [
    {
      "id": 1,
      "product": 1,
      "cp": 2.131,
      "cpk": 1.703,
      "pp": null,
      "ppk": null,
      "mean": 10.0961,
      "std_deviation": 0.1167,
      "sample_size": 150,
      "is_normal": false,
      "normality_test_p_value": 0.0000,
      "analysis_start": "2026-01-10T14:07:21Z",
      "analysis_end": "2026-01-11T19:07:21Z"
    }
  ]
}
```

### 4.2 공정능력 분석 실행

```http
POST /api/spc/process-capability/analyze/
Content-Type: application/json
```

**Request Body**:
```json
{
  "product_id": 1
}
```

**Response 201**:
```json
{
  "id": 2,
  "product": 1,
  "cp": 2.131,
  "cpk": 1.703,
  "mean": 10.0961,
  "std_deviation": 0.1167,
  "sample_size": 150,
  "is_normal": false,
  "normality_test_p_value": 0.0000
}
```

---

## 5. Quality Alerts

### 5.1 품질 경고 목록 조회

```http
GET /api/spc/alerts/
```

**Query Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| product | integer | No | Product ID |
| is_resolved | boolean | No | 해결 여부 |
| priority | integer | No | 우선순위 (1-4) |

**Response 200**:
```json
{
  "results": [
    {
      "id": 1,
      "product": 1,
      "product_code": "BOLT-M10",
      "alert_type": "OUT_OF_SPEC",
      "priority": 4,
      "status": "OPEN",
      "message": "규격 이탈 감지: 9.82 (LSL: 9.5)",
      "measurement_id": 25,
      "is_resolved": false,
      "created_at": "2026-01-11T14:07:21Z"
    }
  ]
}
```

### 5.2 대시보드 경고 통계

```http
GET /api/spc/alerts/dashboard/
```

**Response 200**:
```json
{
  "total": 4,
  "by_status": {
    "open": 3,
    "resolved": 1
  },
  "by_priority": {
    "urgent": 1,
    "high": 2,
    "medium": 1,
    "low": 0
  }
}
```

---

## 6. Run Rules

### 6.1 Run Rule 위반 목록

```http
GET /api/spc/run-rule-violations/
```

**Query Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| control_chart | integer | No | Control Chart ID |
| is_resolved | boolean | No | 해결 여부 |

**Response 200**:
```json
{
  "results": [
    {
      "id": 1,
      "control_chart": 1,
      "rule_type": "RULE_1",
      "detected_at": "2026-01-11T14:07:21Z",
      "is_resolved": false,
      "description": "UCL/LCL 벗어남 - 공정 관리 상태 이탈"
    }
  ]
}
```

---

## 7. Advanced Charts

### 7.1 CUSUM/EWMA 계산

```http
POST /api/spc/advanced-charts/calculate/
Content-Type: application/json
```

**Request Body**:
```json
{
  "product_id": 1,
  "chart_type": "CUSUM",
  "k": 0.5,
  "h": 5.0,
  "lambda_param": 0.2,
  "l": 3.0
}
```

**CUSUM Response**:
```json
{
  "chart_type": "CUSUM",
  "target_value": 10.0,
  "std_dev": 0.1167,
  "k": 0.5,
  "h": 5.0,
  "ucl": 5.0,
  "lcl": -5.0,
  "ci_positive": [0.0, 0.02, 0.05, ...],
  "ci_negative": [0.0, 0.0, 0.0, ...],
  "positive_violations": [],
  "negative_violations": [],
  "total_violations": 0
}
```

**EWMA Response**:
```json
{
  "chart_type": "EWMA",
  "target_value": 10.0,
  "std_dev": 0.1167,
  "lambda": 0.2,
  "l": 3.0,
  "ucl": 10.1567,
  "lcl": 9.8433,
  "cl": 10.0,
  "ewma_values": [10.0, 10.024, 10.039, ...],
  "sigma_ewma": 0.0522,
  "violations": [],
  "total_violations": 0
}
```

### 7.2 CUSUM vs EWMA 비교

```http
POST /api/spc/advanced-charts/compare/
Content-Type: application/json
```

**Request Body**:
```json
{
  "product_id": 1
}
```

**Response**:
```json
{
  "cusum": {
    "total_violations": 0
  },
  "ewma": {
    "total_violations": 0
  },
  "recommendations": [
    "두 방식 모두 위반이 없습니다. 공정이 안정적입니다.",
    "현재 파라미터 설정이 적절합니다."
  ]
}
```

---

## 8. Reports

### 8.1 보고서 생성

```http
POST /api/spc/reports/generate/
Content-Type: application/json
```

**Request Body**:
```json
{
  "report_type": "DAILY",
  "start_date": "2026-01-11T00:00:00Z",
  "format": "json"
}
```

**Response**:
```json
{
  "report_type": "DAILY",
  "period": {
    "start": "2026-01-11T00:00:00Z",
    "end": "2026-01-11T23:59:59Z",
    "formatted": "2026년 1월 11일"
  },
  "generated_at": "2026-01-11T20:00:00Z",
  "summary": {
    "total_products": 3,
    "total_measurements": 900,
    "out_of_spec_rate": 0.22,
    "out_of_control_rate": 0.11,
    "total_alerts": 4,
    "critical_alerts": 1,
    "resolution_rate": 25.0
  },
  "product_details": [...],
  "recommendations": [...]
}
```

---

## 9. Chatbot

### 9.1 챗봇 기능 조회

```http
GET /api/spc/chatbot/capabilities/
```

**Response**:
```json
{
  "capabilities": [
    {
      "intent": "product_capability",
      "description": "제품별 공정능력 조회",
      "examples": [
        "제품 1의 공정능력은 어떤가요?",
        "BOLT-M10의 Cpk를 알려주세요"
      ]
    }
  ]
}
```

### 9.2 챗봇 질문

```http
POST /api/spc/chatbot/chat/
Content-Type: application/json
```

**Request Body**:
```json
{
  "message": "제품 1의 공정능력은 어떤가요?",
  "session_id": "session-12345"
}
```

**Response**:
```json
{
  "response": "제품 BOLT-M10의 공정능력 분석 결과입니다...",
  "suggestions": [
    "SHAFT-20 제품은 어떤가요?",
    "최근 품질 문제를 알려주세요"
  ],
  "context": {
    "product_id": 1,
    "cpk": 1.703
  }
}
```

---

## 에러 응답

### 400 Bad Request
```json
{
  "error": "Invalid input",
  "details": {
    "product": ["This field is required."]
  }
}
```

### 404 Not Found
```json
{
  "error": "Product not found",
  "details": "Product with id=999 does not exist"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "details": "An unexpected error occurred"
}
```

---

## Swagger UI

인터랙티브 API 문서:
```
http://localhost:8000/swagger/
```

---

*마지막 업데이트: 2026-01-11*
