# AI Service Integration Guide

Smart SPC 시스템은 다양한 AI 제공자를 지원하여 Q-COST 분류 및 근본원인분석을 수행합니다.

## 지원하는 AI 제공자

### 1. OpenAI GPT-4
- **모델**: GPT-4
- **특징**: 최고 성능, 높은 정확도
- **API 키 필요**: ✅
- **비용**: 높음
- **설정**:
  ```bash
  AI_PROVIDER=openai
  OPENAI_API_KEY=sk-...
  ```

### 2. Anthropic Claude
- **모델**: Claude 3 Opus
- **특징**: 높은 성능, 긴 컨텍스트 윈도
- **API 키 필요**: ✅
- **비용**: 높음
- **설정**:
  ```bash
  AI_PROVIDER=anthropic
  ANTHROPIC_API_KEY=sk-ant-...
  ```

### 3. Google Gemini
- **모델**: Gemini Pro
- **특징**: 무료 사용 가능, 빠른 응답
- **API 키 필요**: ✅
- **비용**: 낮음 (무료 계층 제공)
- **설정**:
  ```bash
  AI_PROVIDER=gemini
  GEMINI_API_KEY=...
  ```

### 4. Ollama (오픈소스 모델)
- **지원 모델**: Llama 2, Mistral, CodeLlama, 등
- **특징**: 로컬 실행, 무료, 개인정보 보호
- **API 키 필요**: ❌
- **비용**: 무료 (하드웨어만 필요)
- **설정**:
  ```bash
  AI_PROVIDER=ollama
  OPEN_SOURCE_MODEL=llama2  # 또는 mistral, codellama
  OLLAMA_BASE_URL=http://localhost:11434
  ```

### 5. HuggingFace
- **지원 모델**: Mistral, Llama, etc.
- **특징**: 클라우드 API, 다양한 모델
- **API 키 필요**: ✅ (일부 모델 무료)
- **비용**: 낮음~중간
- **설정**:
  ```bash
  AI_PROVIDER=huggingface
  HUGGINGFACE_API_KEY=hf_...
  OPEN_SOURCE_MODEL=mistralai/Mistral-7B-Instruct-v0.2
  ```

## 빠른 시작

### OpenAI GPT-4 사용
```bash
# .env 파일
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### Google Gemini 사용 (무료!)
```bash
# .env 파일
AI_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key-here
```

### Ollama 로컬 모델 사용 (완전 무료)
```bash
# 1. Ollama 설치
# Windows: https://ollama.com/download
# Mac: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# 2. 모델 다운로드
ollama pull llama2
# 또는
ollama pull mistral

# 3. .env 파일
AI_PROVIDER=ollama
OPEN_SOURCE_MODEL=llama2
OLLAMA_BASE_URL=http://localhost:11434
```

## 사용 예시

### Python 코드에서 AI 서비스 사용
```python
from ai_service.services import get_ai_service
import asyncio

async def classify_cost():
    # AI 서비스 인스턴스 생성 (.env의 AI_PROVIDER에 따라 자동 선택)
    ai_service = get_ai_service()

    # Q-COST 분류
    result = await ai_service.classify_qcost(
        description="검사 장비 고장으로 인한 재작업 비용",
        amount=500000,
        context="CNC 가공 공정"
    )

    print(f"카테고리: {result['suggested_category']}")
    print(f"신뢰도: {result['confidence']}")
    print(f"사유: {result['reasoning']}")

    # 서비스 종료
    await ai_service.close()

# 실행
asyncio.run(classify_cost())
```

### 근본원인분석 예시
```python
async def analyze_root_cause():
    ai_service = get_ai_service()

    result = await ai_service.analyze_root_cause(
        problem_description="내경 치수 불량 발생",
        defect_details="타겟 10.0±0.1, 실측 10.15 (OOS)",
        context="CNC 가공 공정, Shaft-002"
    )

    print(f"근본 원인: {result['root_cause']}")
    print(f"시정 조치: {result['recommended_corrective_actions']}")
    print(f"예방 조치: {result['recommended_preventive_actions']}")

    await ai_service.close()

asyncio.run(analyze_root_cause())
```

## 모델별 특징 비교

| 제공자 | 모델 | 성능 | 속도 | 비용 | 오프라인 | 추천 용도 |
|--------|------|------|------|------|----------|-----------|
| OpenAI | GPT-4 | ⭐⭐⭐⭐⭐ | 빠름 | 높음 | ❌ | 프로덕션, 고정확도 필요시 |
| Anthropic | Claude 3 | ⭐⭐⭐⭐⭐ | 빠름 | 높음 | ❌ | 프로덕션, 긴 텍스트 분석 |
| Gemini | Gemini Pro | ⭐⭐⭐⭐ | 매우 빠름 | 낮음 | ❌ | 개발, 테스트, 비용 절감 |
| Ollama | Llama 2 | ⭐⭐⭐ | 느림 | 무료 | ✅ | 개인정보, 오프라인 환경 |
| Ollama | Mistral | ⭐⭐⭐⭐ | 보통 | 무료 | ✅ | 균형 잡힌 오픈소스 |
| HuggingFace | Mistral 7B | ⭐⭐⭐⭐ | 보통 | 낮음 | ❌ | 클라우드 오픈소스 |

## API 키 발급 방법

### 1. OpenAI API Key
1. https://platform.openai.com 접속
2. 로그인 후 API Keys 메뉴
3. Create new secret key
4. `.env` 파일에 `OPENAI_API_KEY=sk-...` 설정

### 2. Anthropic API Key
1. https://console.anthropic.com 접속
2. API Keys 메뉴
3. Create key
4. `.env` 파일에 `ANTHROPIC_API_KEY=sk-ant-...` 설정

### 3. Google Gemini API Key
1. https://makersuite.google.com/app/apikey 접속
2. Create API key
3. `.env` 파일에 `GEMINI_API_KEY=...` 설정
4. **Gemini는 무료 사용량이 제공됩니다!**

### 4. HuggingFace API Key
1. https://huggingface.co/settings/tokens 접속
2. New token 생성
3. `.env` 파일에 `HUGGINGFACE_API_KEY=hf_...` 설정

### 5. Ollama (API 키 불필요)
```bash
# Ollama 설치 후 모델 다운로드
ollama pull llama2
ollama pull mistral
ollama pull codellama

# 서버 시작 (자동으로 백그라운드에서 실행됨)
# Windows: 설치 후 자동 시작
# Mac/Linux: ollama serve
```

## 성능 최적화 팁

### 1. 비용 절감을 위한 모델 선택
- **개발/테스트**: Gemini (무료) 또는 Ollama (로컬 무료)
- **스테이징**: Gemini Pro (저렴)
- **프로덕션**: GPT-4 또는 Claude (고정확도)

### 2. 응답 속도 최적화
- **빠른 응답 필요**: Gemini → OpenAI → Anthropic 순
- **오픈소스**: Mistral이 Llama 2보다 빠름

### 3. 데이터 프라이버시
- **개인정보 포함**: Ollama (로컬 실행 권장)
- **일반 데이터**: 클라우드 API (OpenAI, Gemini 등)

## Troubleshooting

### Ollama 연결 오류
```bash
# Ollama 실행 중인지 확인
curl http://localhost:11434/api/tags

# 모델 목록 확인
ollama list

# Ollama 재시작
# Windows: 작업 관리자에서 Ollama 앱 재시작
# Mac/Linux: ollama serve
```

### API 키 인증 오류
```bash
# .env 파일 확인
cat .env | grep API_KEY

# Django 서버 재시작으로 환경변수 재로드
python manage.py runserver
```

### HuggingFace 모델 로딩 오류
```python
# 올바른 모델 ID 형식
# 잘못됨: mistral
# 올바름: mistralai/Mistral-7B-Instruct-v0.2

OPEN_SOURCE_MODEL=mistralai/Mistral-7B-Instruct-v0.2
```

## 추천 설정

### 개발 환경
```bash
AI_PROVIDER=gemini  # 무료이고 빠름
GEMINI_API_KEY=your-gemini-key
```

### 프로덕션 환경
```bash
AI_PROVIDER=openai  # 최고 성능
OPENAI_API_KEY=your-openai-key
```

### 오프라인/개인정보 환경
```bash
AI_PROVIDER=ollama
OPEN_SOURCE_MODEL=mistral  # 좋은 성능의 오픈소스
OLLAMA_BASE_URL=http://localhost:11434
```

---

**마지막 업데이트**: 2025-01-14
**버전**: 1.0.0
