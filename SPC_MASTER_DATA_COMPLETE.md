# SPC Master Data & ERP/MES Integration - Complete Documentation

## 개요

SPC 품질관리 시스템에 기본정보(마스터 데이터) 관리 기능과 ERP/MES 연계 기능을 구현했습니다. APS 시스템의 기본정보 및 ERP/MES 연계 메뉴 그룹과 동일한 구조로, 품질 관리에 특화된 마스터 데이터를 관리합니다.

---

## 구현 완료 기능

### 1. 백엔드 (Backend Django)

#### 1.1 마스터 데이터 모델 (`backend/apps/spc/models/master_data.py`)

**QualityItemMaster** - 품질 품목 마스터 (ERP 연계)
- 품목 기본 정보 (코드, 명칭, 유형, 패밀리)
- 품질 등급 (A/B/C급)
- 검사 유형 (전수/샘플링/Skip/검사안함)
- 샘플링 기준 (계획, 크기, 빈도, AQL)
- 공급자 정보
- ERP 동기화 타임스탬프

**QualityProcessMaster** - 품질 공정 마스터 (MES 연계)
- 공정 기본 정보 (코드, 명칭)
- 공정 유형 (수입/공정/최종/출하검사)
- 소속 정보 (작업장, 라인)
- 공정 순서
- 관리 특성 수
- MES 동기화 타임스탬프

**QualityCharacteristicMaster** - 품질 특성 마스터
- 특성 기본 정보 (코드, 명칭)
- 품목/공정 연계
- 특성 유형 (치수/중량/전압/전류/온도/압력/외관/기능/기타)
- 데이터 유형 (연속형/이산형/속성형)
- 측정 단위
- 규격 (LSL, Target, USL)
- 공정능력 목표 (Cpk 목표, 최소)
- 관리도 유형 (Xbar-R, Xbar-S, I-MR, P, NP, C, U)
- 부분군 크기
- 측정 방법/위치

**MeasurementInstrumentMaster** - 측정기구 마스터
- 기구 기본 정보 (코드, 명칭)
- 기구 유형 (노규자/마이크로미터/CMM/저울/멀티미터 등)
- 제조사/모델/일련번호
- 측정 범위/분해능/정밀도
- 보정 정보 (주기, 최종일, 다음일, 기관)
- 상태 (사용가능/보정만료/정비중/폐기)
- Gage R&R 정보 (필수 여부, 최종일, 결과)

**MeasurementSystemMaster** - 측정 시스템 마스터
- 시스템 기본 정보 (코드, 명칭)
- 구성 기구 (다대다 연계)
- 측정 프로세스
- 환경 조건 (온도/습도 범위)
- MSA 방법 (Gage R&R, 선형성, 안정성, 편향)

**MeasurementSystemComponent** - 측정 시스템 구성
- 시스템-기구 연계
- 구성 역할 (주측정기, 보조측정기)
- 순번
- EV 기여도 (Equipment Variation)

**InspectionStandardMaster** - 검사 기준 마스터
- 기준 기본 정보 (코드, 명칭)
- 품목/특성 연계
- 기준 유형 (검사/시험/규격/합격판정)
- 검사 조건
- 합격/불합격 판정 기준
- 샘플링 방법/크기/AQL
- 시험 방법/장비
- 참조 문서/개정번호/시행일자

**QualitySyncLog** - 품질 데이터 동기화 로그
- 동기화 유형 (품목/공정/특성/기구/기준/측정)
- 데이터 원천 (ERP/MES/레거시/수동)
- 동기화 상태 (성공/실패/부분성공)
- 건수 (총/성공/실패)
- 오류 메시지/상세 정보
- 소스 시스템/파일
- 동기화 시작/종료 시각
- 소요 시간

#### 1.2 API 시리얼라이저 (`backend/apps/spc/serializers/master_data.py`)

**목록 시리얼라이저** (6개)
- QualityItemMasterListSerializer
- QualityProcessMasterListSerializer
- QualityCharacteristicMasterListSerializer
- MeasurementInstrumentMasterListSerializer
- MeasurementSystemMasterListSerializer
- InspectionStandardMasterListSerializer

**상세 시리얼라이저** (6개)
- QualityItemMasterSerializer
- QualityProcessMasterSerializer
- QualityCharacteristicMasterSerializer
- MeasurementInstrumentMasterSerializer
- MeasurementSystemMasterSerializer
- InspectionStandardMasterSerializer

**기타 시리얼라이저** (4개)
- QualitySyncLogSerializer
- ERPItemImportSerializer (ERP Import용)
- MESProcessImportSerializer (MES Import용)
- ERPItemBatchImportSerializer / MESProcessBatchImportSerializer

#### 1.3 API 뷰 (`backend/apps/spc/views/master_data.py`)

**QualityItemMasterViewSet**
- CRUD 기본 기능
- 필터링 (itm_type, itm_family, quality_grade)
- `import_from_erp` 액션: ERP에서 품목 데이터 일괄 Import

**QualityProcessMasterViewSet**
- CRUD 기본 기능
- 필터링 (process_type, workcenter_cd, line_cd)
- `import_from_mes` 액션: MES에서 공정 데이터 일괄 Import

**QualityCharacteristicMasterViewSet**
- CRUD 기본 기능
- 필터링 (item_id, process_id, characteristic_type)

**MeasurementInstrumentMasterViewSet**
- CRUD 기본 기능
- 필터링 (instrument_type, status)
- `calibration_due` 액션: 보정 만료 기구 목록
- `gage_rr_due` 액션: Gage R&R 실시 필요 기구 목록

**MeasurementSystemMasterViewSet**
- CRUD 기본 기능
- `add_instrument` 액션: 시스템에 기구 추가
- `remove_instrument` 액션: 시스템에서 기구 제거

**InspectionStandardMasterViewSet**
- CRUD 기본 기능
- 필터링 (item_id, characteristic_id, standard_type)

**QualitySyncLogViewSet** (읽기 전용)
- 목록 조회
- 필터링 (sync_type, sync_source, sync_status)
- `statistics` 액션: 동기화 통계

---

## API 엔드포인트

### 품질 품목 마스터 (Quality Item Master)

```
GET    /api/spc/master-data/items/                      # 품목 목록
POST   /api/spc/master-data/items/                      # 품목 생성
GET    /api/spc/master-data/items/{itm_id}/             # 품목 상세
PUT    /api/spc/master-data/items/{itm_id}/             # 품목 수정
DELETE /api/spc/master-data/items/{itm_id}/             # 품목 삭제
POST   /api/spc/master-data/items/import_from_erp/      # ERP Import
```

### 품질 공정 마스터 (Quality Process Master)

```
GET    /api/spc/master-data/processes/                  # 공정 목록
POST   /api/spc/master-data/processes/                  # 공정 생성
GET    /api/spc/master-data/processes/{process_cd}/     # 공정 상세
PUT    /api/spc/master-data/processes/{process_cd}/     # 공정 수정
DELETE /api/spc/master-data/processes/{process_cd}/     # 공정 삭제
POST   /api/spc/master-data/processes/import_from_mes/  # MES Import
```

### 품질 특성 마스터 (Quality Characteristic Master)

```
GET    /api/spc/master-data/characteristics/                            # 특성 목록
POST   /api/spc/master-data/characteristics/                            # 특성 생성
GET    /api/spc/master-data/characteristics/{characteristic_cd}/       # 특성 상세
PUT    /api/spc/master-data/characteristics/{characteristic_cd}/       # 특성 수정
DELETE /api/spc/master-data/characteristics/{characteristic_cd}/       # 특성 삭제
```

### 측정기구 마스터 (Measurement Instrument Master)

```
GET    /api/spc/master-data/instruments/                   # 기구 목록
POST   /api/spc/master-data/instruments/                   # 기구 생성
GET    /api/spc/master-data/instruments/{instrument_cd}/  # 기구 상세
PUT    /api/spc/master-data/instruments/{instrument_cd}/  # 기구 수정
DELETE /api/spc/master-data/instruments/{instrument_cd}/  # 기구 삭제
GET    /api/spc/master-data/instruments/calibration_due/  # 보정 만료 목록
GET    /api/spc/master-data/instruments/gage_rr_due/      # Gage R&R 대상 목록
```

### 측정 시스템 마스터 (Measurement System Master)

```
GET    /api/spc/master-data/systems/                              # 시스템 목록
POST   /api/spc/master-data/systems/                              # 시스템 생성
GET    /api/spc/master-data/systems/{system_cd}/                 # 시스템 상세
PUT    /api/spc/master-data/systems/{system_cd}/                 # 시스템 수정
DELETE /api/spc/master-data/systems/{system_cd}/                 # 시스템 삭제
POST   /api/spc/master-data/systems/{system_cd}/add_instrument/  # 기구 추가
DELETE /api/spc/master-data/systems/{system_cd}/remove_instrument/  # 기구 제거
```

### 검사 기준 마스터 (Inspection Standard Master)

```
GET    /api/spc/master-data/standards/                        # 기준 목록
POST   /api/spc/master-data/standards/                        # 기준 생성
GET    /api/spc/master-data/standards/{standard_cd}/          # 기준 상세
PUT    /api/spc/master-data/standards/{standard_cd}/          # 기준 수정
DELETE /api/spc/master-data/standards/{standard_cd}/          # 기준 삭제
```

### 동기화 로그 (Quality Sync Log)

```
GET    /api/spc/master-data/sync-logs/           # 로그 목록
GET    /api/spc/master-data/sync-logs/{sync_id}/ # 로그 상세
GET    /api/spc/master-data/sync-logs/statistics/ # 동기화 통계
```

---

## 데이터베이스 스키마

### 주요 테이블

| 테이블 | 설명 |
|--------|------|
| `quality_item_master` | 품질 품목 마스터 |
| `quality_process_master` | 품질 공정 마스터 |
| `quality_characteristic_master` | 품질 특성 마스터 |
| `measurement_instrument_master` | 측정기구 마스터 |
| `measurement_system_master` | 측정 시스템 마스터 |
| `measurement_system_component` | 측정 시스템 구성 |
| `inspection_standard_master` | 검사 기준 마스터 |
| `quality_sync_log` | 품질 데이터 동기화 로그 |

---

## 사용 예시

### 1. ERP에서 품목 마스터 Import

```bash
curl -X POST http://localhost:8000/api/spc/master-data/items/import_from_erp/ \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "itm_id": "ERP-001",
        "itm_nm": "배터리 셀 18650",
        "itm_type": "FINISHED_GOOD",
        "itm_family": "배터리",
        "quality_grade": "A",
        "inspection_type": "SAMPLING",
        "sampling_plan": "MIL-STD-105E",
        "sample_size": 50,
        "sampling_frequency": "2시간말",
        "supplier_code": "SUP-001",
        "supplier_nm": "(주)한국배터리",
        "quality_manager": "홍길동"
      },
      {
        "itm_id": "ERP-002",
        "itm_nm": "PCB 보드",
        "itm_type": "COMPONENT",
        "itm_family": "전자부품",
        "quality_grade": "B",
        "inspection_type": "SAMPLING",
        "sampling_plan": "AQL=1.5",
        "sample_size": 32,
        "sampling_frequency": "배치별",
        "quality_manager": "김철수"
      }
    ]
  }'
```

**응답:**
```json
{
  "total": 2,
  "created": 2,
  "updated": 0,
  "failed": 0,
  "errors": []
}
```

### 2. MES에서 공정 마스터 Import

```bash
curl -X POST http://localhost:8000/api/spc/master-data/processes/import_from_mes/ \
  -H "Content-Type: application/json" \
  -d '{
    "processes": [
      {
        "process_cd": "MES-P001",
        "process_nm": "코팅 공정",
        "process_type": "PROCESS",
        "workcenter_cd": "WC-001",
        "workcenter_nm": "제1공장",
        "line_cd": "LINE-01",
        "process_seq": 1,
        "process_manager": "이영호"
      },
      {
        "process_cd": "MES-P002",
        "process_nm": "조립 공정",
        "process_type": "PROCESS",
        "workcenter_cd": "WC-001",
        "workcenter_nm": "제1공장",
        "line_cd": "LINE-01",
        "process_seq": 2,
        "process_manager": "박민수"
      }
    ]
  }'
```

### 3. 품질 특성 생성

```bash
curl -X POST http://localhost:8000/api/spc/master-data/characteristics/ \
  -H "Content-Type: application/json" \
  -d '{
    "characteristic_cd": "CHAR-001",
    "characteristic_nm": "셀 두께",
    "item": "ERP-001",
    "process": "MES-P001",
    "characteristic_type": "DIMENSION",
    "data_type": "CONTINUOUS",
    "unit": "mm",
    "lsl": 0.65,
    "target": 0.70,
    "usl": 0.75,
    "cpk_target": 1.33,
    "cpk_minimum": 1.00,
    "control_chart_type": "XBAR_R",
    "subgroup_size": 5,
    "measurement_method": "마이크로미터 측정",
    "measurement_location": "셀 중앙부",
    "quality_manager": "홍길동"
  }'
```

### 4. 측정기구 등록

```bash
curl -X POST http://localhost:8000/api/spc/master-data/instruments/ \
  -H "Content-Type: application/json" \
  -d '{
    "instrument_cd": "INST-001",
    "instrument_nm": "디지털 마이크로미터",
    "instrument_type": "MICROMETER",
    "manufacturer": "Mitutoyo",
    "model_no": "MDE-25PJ",
    "serial_no": "SN123456",
    "measurement_range_min": 0,
    "measurement_range_max": 25,
    "resolution": 0.001,
    "unit": "mm",
    "accuracy": 0.001,
    "calibration_cycle": 365,
    "last_calibration_date": "2024-01-01",
    "next_calibration_date": "2025-01-01",
    "calibration_institution": "(주)한국계량측정",
    "status": "ACTIVE",
    "location": "품질검사실 A",
    "responsible_person": "홍길동",
    "gage_rr_required": true,
    "gage_rr_result": "PASS"
  }'
```

### 5. 측정 시스템 생성 및 기구 추가

```bash
# 시스템 생성
curl -X POST http://localhost:8000/api/spc/master-data/systems/ \
  -H "Content-Type: application/json" \
  -d '{
    "system_cd": "SYS-001",
    "system_nm": "셀 두께 측정 시스템",
    "measurement_process": "마이크로미터를 사용하여 셀 중앙부 두께 측정",
    "temperature_min": 20,
    "temperature_max": 25,
    "humidity_min": 40,
    "humidity_max": 60,
    "system_manager": "홍길동",
    "location": "품질검사실 A",
    "msa_method": "GAGE_RR"
  }'

# 기구 추가
curl -X POST http://localhost:8000/api/spc/master-data/systems/SYS-001/add_instrument/ \
  -H "Content-Type: application/json" \
  -d '{
    "instrument_cd": "INST-001",
    "component_role": "주측정기",
    "seq": 1
  }'
```

### 6. 검사 기준 등록

```bash
curl -X POST http://localhost:8000/api/spc/master-data/standards/ \
  -H "Content-Type: application/json" \
  -d '{
    "standard_cd": "STD-001",
    "standard_nm": "배터리 셀 두께 검사 기준서",
    "item": "ERP-001",
    "characteristic": "CHAR-001",
    "standard_type": "INSPECTION",
    "inspection_condition": "온도 23±2℃, 습도 50±10% RH",
    "acceptance_criteria": "0.65mm ≤ 측정값 ≤ 0.75mm",
    "rejection_criteria": "측정값 < 0.65mm 또는 > 0.75mm",
    "sampling_method": "랜덤 샘플링",
    "sample_size": 50,
    "aql": 1.5,
    "test_method": "마이크로미터로 3점 측정 후 평균값 산출",
    "test_equipment": "디지털 마이크로미터 (INST-001)",
    "reference_doc": "QS-STD-001",
    "revision": "Rev. 1.0",
    "effective_date": "2024-01-01"
  }'
```

### 7. 동기화 로그 조회

```bash
# 전체 로그
curl http://localhost:8000/api/spc/master-data/sync-logs/

# 필터링
curl "http://localhost:8000/api/spc/master-data/sync-logs/?sync_type=ITEM&sync_source=ERP"

# 동기화 통계
curl http://localhost:8000/api/spc/master-data/sync-logs/statistics/
```

---

## 주요 파일

### Backend
- `backend/apps/spc/models/master_data.py` (900+ 줄)
  - 8개 마스터 데이터 모델
- `backend/apps/spc/serializers/master_data.py` (450+ 줄)
  - 16개 시리얼라이저
- `backend/apps/spc/views/master_data.py` (400+ 줄)
  - 7개 ViewSet + 커스텀 액션
- `backend/apps/spc/urls.py` (수정됨)
  - master-data 라우터 추가
- `backend/apps/spc/models.py` (수정됨)
  - 마스터 데이터 모델 Import
- `backend/apps/spc/views/__init__.py` (신규)

---

## 다음 단계

### 1. ✅ **데이터베이스 마이그레이션 실행**
```bash
cd backend
python manage.py makemigrations spc
python manage.py migrate
```

### 2. ✅ **Backend 서버 시작**
```bash
cd backend
python manage.py runserver
```

### 3. **프론트엔드 마스터 데이터 관리 페이지 구현** (다음 작업)
- 품질 품목 마스터 관리 페이지
- 품질 공정 마스터 관리 페이지
- 품질 특성 마스터 관리 페이지
- 측정기구/시스템 관리 페이지
- 검사 기준 관리 페이지
- 동기화 로그 조회 페이지

### 4. **레거시 시스템 연동 서비스 구현** (다음 작업)
- CSV/Excel 파일 Import 기능
- FTP/SFTP 파일 수신 기능
- DB 연동 (Oracle, MSSQL 등)
- API 연동 (REST, SOAP)

---

## 특징 및 장점

### 1. ERP/MES 연동
- ERP 품목 마스터와 자동 동기화
- MES 공정 정보와 자동 동기화
- 레거시 시스템 데이터 지원

### 2. 품질 관리 특화
- 품질 등급 (A/B/C급) 관리
- 검사 유형별 샘플링 기준
- 공정능력 목표 관리
- MSA (Gage R&R) 지원

### 3. 측정 시스템 관리
- 단일 기구 및 시스템 관리
- 보정 주기 자동 관리
- 보정 만료 알림
- EV 기여도 관리

### 4. 동기화 이력 관리
- 모든 Import 이력 기록
- 성공/실패 건수 추적
- 상세 오류 메시지
- 동기화 통계

### 5. 필터링 및 검색
- 유형별 필터링
- 상태별 필터링
- 날짜 범위 검색
- 키워드 검색

---

**완료일시**: 2026-01-11
**버전**: 1.0.0
