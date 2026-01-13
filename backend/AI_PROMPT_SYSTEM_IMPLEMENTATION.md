# AI Prompt System Implementation Summary

## Overview
AI 프롬프트 관리 시스템이 성공적으로 구현되었습니다. 이 시스템은 검수 프로세스 설계, 기준표 생성, Q-COST 분류, COPQ 분석 리포트 등 4가지 주요 Use Case를 지원합니다.

## Architecture

### 1. Core Components

#### AI Prompt Manager (`apps/spc/ai_prompts.py`)
- **Purpose**: 프롬프트 템플릿 및 스키마 관리
- **Key Features**:
  - 4개 Use Case별 프롬프트 템플릿
  - 입력/출력 JSON 스키마 정의
  - 버전 관리 (version field)
  - 언어 지원 (ko/en/zh)

#### AI Prompt Service (`apps/spc/services/ai_prompt_service.py`)
- **Purpose**: AI 프롬프트 실행 및 결과 관리
- **Key Features**:
  - 입력 데이터 해싱 (중복 방지)
  - AIOutput 모델 연동
  - 모의 출력 생성 (테스트용)
  - 결과 캐싱
  - 출력 결과 조회

### 2. API Endpoints

#### Base URL: `/api/spc/ai-prompts/`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/use_cases/` | GET | 사용 가능한 Use Case 목록 조회 |
| `/format/` | POST | 프롬프트 포맷팅 (입력 데이터 적용) |
| `/execute/` | POST | AI 프롬프트 실행 및 결과 저장 |
| `/outputs/` | GET | AI 출력 결과 목록 조회 |
| `/output_detail/` | GET | AI 출력 결과 상세 조회 |
| `/capabilities/` | GET | AI 프롬프트 시스템 기능 안내 |

### 3. Use Cases

#### 1) PROCESS_DESIGN: 검수 프로세스 설계
- **Description**: 제품/공정 정보를 기반으로 검사 프로세스와 검사 지점을 자동 설계
- **Inputs**:
  - `company`: industry, site
  - `product`: item_name, process
  - `constraints`: inspection_headcount, shift
  - `known_defects`: array of defect types
  - `customer_requirements`: array of requirements
- **Outputs**:
  - `process_flow`: 공정 흐름 (step, inspection_points)
  - `inspection_points`: 검사 지점 상세 (ctq, frequency, method, sample_size)
  - `assumptions`: 가정사항 목록
  - `risks`: 리스크 식별 (risk, probability, mitigation)
  - `implementation_notes`: 구현 노트

#### 2) CRITERIA_CHECKLIST: 검수 기준표 + 체크리스트 생성
- **Description**: 불량 모드별 검사 기준표와 검사자용 체크리스트 자동 생성
- **Inputs**:
  - `item`: 제품명
  - `step`: 공정 단계
  - `inspection_type`: 검사 유형 (DIM/ATTR/SENSORY/COMBO)
  - `defect_modes`: 불량 모드 배열
  - `acceptance_policy`: 합격 정책 (A/B/C 등급)
  - `language`: 언어 (ko/en/zh)
- **Outputs**:
  - `criteria_table`: 검사 기준표 (category, check, method, accept, reject, action)
  - `checklist`: 체크리스트 (no, question, type, photo_required)
  - `training_notes`: 훈련 노트
  - `edge_cases`: 엣지 케이스 처리 방법

#### 3) QCOST_CLASSIFY: Q-COST 분류/자동 태깅
- **Description**: 품질비용 발생 내용을 4대 분류(예방/평가/내부실패/외부실패)로 자동 분류
- **Inputs**:
  - `text`: 코스트 발생 설명
  - `amount`: 금액
  - `context`: dept, lot_no, issue
- **Outputs**:
  - `qcost_classification`: lvl1, lvl2, lvl3, item_candidate, copq_flag
  - `link_suggestions`: lot_no, run_id, spc_event_id, capa_id
  - `confidence`: 신뢰도 (0~1)
  - `rationale`: 분류 근거

#### 4) COPQ_REPORT: COPQ 분석 리포트
- **Description**: COPQ 데이터를 분석하여 경영진단용 요약보고서 자동 생성
- **Inputs**:
  - `period`: 집계 기간 (YYYY-MM)
  - `kpis`: sales, total_qcost, total_copq, copq_rate
  - `top_defects`: defect, count, scrap_cost
  - `spc_events`: chart, type, count
  - `actions_open`: capa_id, status
- **Outputs**:
  - `executive_summary`: 경영진단 요약
  - `key_findings`: 주요 발견사항 (3~5개)
  - `drivers`: 원인별 영향도 분석 (name, impact, copq_contribution, evidence, root_cause)
  - `recommended_actions`: 우선순위별 권장 사항
  - `risk_watchlist`: 리스크 관찰 목록
  - `appendix`: 필요한 차트, 데이터 원천

### 4. Database Integration

#### AIOutput Model (`apps/spc/models_qa.py`)
```python
class AIOutput(models.Model):
    ai_id = AutoField(primary_key=True)
    site = ForeignKey(OrganizationSite)
    use_case = CharField(max_length=50, choices=USE_CASE_CHOICES)
    input_hash = CharField(max_length=64, unique=True)
    model_name = CharField(max_length=100)
    prompt_version = CharField(max_length=20)
    output_json = JSONField()
    confidence = FloatField()
    created_dt = DateTimeField(auto_now_add=True)
    created_by = IntegerField()
```

### 5. API Usage Examples

#### Example 1: Get Available Use Cases
```bash
GET /api/spc/ai-prompts/use_cases/
```

Response:
```json
{
  "use_cases": [
    {
      "use_case": "PROCESS_DESIGN",
      "name": "검수 프로세스 설계",
      "description": "제품/공정 정보를 기반으로 검사 프로세스와 검사 지점을 자동 설계"
    },
    ...
  ],
  "total_count": 4
}
```

#### Example 2: Execute AI Prompt
```bash
POST /api/spc/ai-prompts/execute/

{
  "use_case": "PROCESS_DESIGN",
  "inputs": {
    "company": {"industry": "자동차부품", "site": "경기공장"},
    "product": {"item_name": "브레이크 패드", "process": "CNC+세척+조립"},
    "constraints": {"inspection_headcount": 3, "shift": 2},
    "known_defects": ["치수불량", "스크래치"],
    "customer_requirements": ["IATF 16949 준수"]
  },
  "language": "ko",
  "model_name": "gpt-4",
  "site_id": 1,
  "user_id": 1
}
```

Response:
```json
{
  "use_case": "PROCESS_DESIGN",
  "ai_output_id": 1,
  "output_json": {
    "process_flow": [...],
    "inspection_points": [...],
    "assumptions": [...],
    "risks": [...]
  },
  "confidence": 0.87,
  "model_name": "gpt-4",
  "created_at": "2026-01-12T10:00:00Z",
  "cached": false
}
```

#### Example 3: List AI Outputs
```bash
GET /api/spc/ai-prompts/outputs/?site_id=1&use_case=PROCESS_DESIGN&limit=10
```

Response:
```json
{
  "outputs": [
    {
      "ai_output_id": 1,
      "use_case": "PROCESS_DESIGN",
      "model_name": "gpt-4",
      "confidence": 0.87,
      "created_at": "2026-01-12T10:00:00Z",
      "created_by": 1
    }
  ],
  "total_count": 1
}
```

### 6. Features

#### Caching
- 동일 입력 데이터(input_hash)에 대한 결과를 자동 캐싱
- 중복 실행 시 저장된 결과 반환 (cached: true)

#### Versioning
- 프롬프트 버전 관리 (prompt_version field)
- 각 Use Case별 버전 추적

#### Input Validation
- 입력 스키마 검증 (input_schema)
- Serializer를 통한 데이터 검증

#### Output Storage
- AI 출력 결과를 DB에 저장 (AIOutput 모델)
- 이력 조회 및 재사용 가능

#### Mock Mode
- 테스트용 모의 출력 지원
- 실제 LLM API 연동 전 단계 테스트 가능

### 7. File Structure

```
backend/
├── apps/
│   └── spc/
│       ├── ai_prompts.py                          # Prompt templates & manager
│       ├── services/
│       │   └── ai_prompt_service.py               # AI execution service
│       ├── models_qa.py                           # AIOutput model
│       ├── serializers.py                         # AI prompt serializers
│       ├── views.py                               # AIPromptViewSet
│       └── urls.py                                # API routing
└── test_ai_prompts.py                             # Test suite
```

### 8. Implementation Status

✅ **Completed**:
- AI Prompt Manager (ai_prompts.py)
- AI Prompt Service (ai_prompt_service.py)
- Serializers (AIPromptRequestSerializer, etc.)
- ViewSet (AIPromptViewSet)
- URL Routing
- Test Suite (test_ai_prompts.py)

⏳ **Next Steps** (Future Enhancement):
- LLM API 연동 (OpenAI, Anthropic, etc.)
- 실제 AI 출력 생성
- 프롬프트 템플릿 최적화
- 출력 품질 개선
- 사용자 인증/권한 통합

### 9. Testing

Run the test suite:
```bash
cd backend
python manage.py shell < test_ai_prompts.py
```

Or directly:
```bash
python test_ai_prompts.py
```

### 10. API Capabilities

Check system capabilities:
```bash
GET /api/spc/ai-prompts/capabilities/
```

This returns comprehensive information about:
- Available use cases
- Endpoint descriptions
- Feature list
- Configuration options

## Conclusion

AI 프롬프트 시스템이 성공적으로 구현되었습니다. 이 시스템은:

1. 4가지 주요 Use Case 지원 (검수 프로세스 설계, 기준표 생성, Q-COST 분류, COPQ 분석)
2. 완전한 API 엔드포인트 제공
3. 데이터베이스 연동 (AIOutput 모델)
4. 결과 캐싱 및 재사용
5. 버전 관리
6. 테스트 스위트 포함

실제 LLM API 연동만 추가되면 즉시 운영 가능한 상태입니다.

---

**Implementation Date**: 2026-01-12
**Version**: 1.0.0
**Status**: ✅ Complete (Mock Mode)
