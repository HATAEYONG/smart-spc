"""
LLM 기반 제약조건 추천 모듈
현장 문제 설명 → AI가 제약조건 및 개선 방안 자동 추천
"""
import os
from typing import List, Dict, Optional
import json
from pathlib import Path

# OpenAI / Anthropic 선택 가능
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class ConstraintRecommender:
    """
    LLM 기반 제약조건 및 개선 방안 추천 시스템
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = 'gpt-4',
        provider: str = 'openai'
    ):
        """
        초기화

        Args:
            api_key: API 키 (None이면 환경변수에서 로드)
            model: 모델 이름 ('gpt-4', 'gpt-3.5-turbo', 'claude-3-opus-20240229' 등)
            provider: 'openai' 또는 'anthropic'
        """
        self.provider = provider
        self.model = model

        if provider == 'openai':
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI 패키지가 설치되지 않았습니다: pip install openai")
            self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        elif provider == 'anthropic':
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("Anthropic 패키지가 설치되지 않았습니다: pip install anthropic")
            self.client = Anthropic(api_key=api_key or os.getenv('ANTHROPIC_API_KEY'))
        else:
            raise ValueError(f"지원하지 않는 provider: {provider}")

        # 시스템 프롬프트
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """
        시스템 프롬프트 로드
        """
        return """당신은 APS(Advanced Planning and Scheduling) 시스템의 전문가입니다.
제조 현장의 문제를 분석하고, 최적의 제약조건(Constraints)과 개선 방안을 추천합니다.

**역할**:
1. 사용자가 설명한 현장 문제를 분석
2. 문제의 근본 원인 파악
3. 적절한 제약조건 추천 (납기 제약, 설비 제약, 시간 제약 등)
4. 구체적인 개선 방안 제시
5. 예상 효과 및 주의사항 안내

**제약조건 유형**:
- Due Date Constraint: 납기 제약
- Machine Constraint: 설비 제약 (사용 불가 시간, 능력 제한 등)
- Precedence Constraint: 선행 작업 제약
- Resource Constraint: 자원 제약 (인력, 자재 등)
- Time Window Constraint: 시간대 제약
- Setup Time Constraint: 설정 시간 제약

**응답 형식** (JSON):
{
  "problem_analysis": "문제 분석 내용",
  "root_cause": "근본 원인",
  "recommendations": [
    {
      "constraint_type": "제약조건 유형",
      "constraint_description": "제약조건 설명",
      "implementation": "구현 방법",
      "expected_impact": "예상 효과",
      "priority": "우선순위 (High/Medium/Low)"
    }
  ],
  "additional_suggestions": ["추가 제안 사항들"],
  "warnings": ["주의사항들"]
}
"""

    def recommend(
        self,
        problem_description: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        문제 설명 → 제약조건 및 개선 방안 추천

        Args:
            problem_description: 현장 문제 설명
            context: 추가 컨텍스트 (설비 수, 작업 수, 현재 KPI 등)

        Returns:
            추천 결과 딕셔너리
        """
        # 사용자 프롬프트 구성
        user_prompt = f"""**현장 문제**:
{problem_description}
"""

        if context:
            user_prompt += f"\n**현재 상황**:\n"
            for key, value in context.items():
                user_prompt += f"- {key}: {value}\n"

        user_prompt += "\n위 문제를 분석하고 제약조건 및 개선 방안을 JSON 형식으로 추천해주세요."

        # LLM 호출
        if self.provider == 'openai':
            response = self._call_openai(user_prompt)
        else:
            response = self._call_anthropic(user_prompt)

        # JSON 파싱
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 텍스트 그대로 반환
            result = {
                "problem_analysis": response,
                "recommendations": [],
                "raw_response": response
            }

        return result

    def _call_openai(self, user_prompt: str) -> str:
        """
        OpenAI API 호출
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content

    def _call_anthropic(self, user_prompt: str) -> str:
        """
        Anthropic API 호출
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.3,
            system=self.system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.content[0].text

    def format_recommendations(self, result: Dict) -> str:
        """
        추천 결과를 사람이 읽기 쉬운 형식으로 포맷팅
        """
        output = []

        output.append("=" * 80)
        output.append("🤖 AI 제약조건 및 개선 방안 추천")
        output.append("=" * 80)

        if 'problem_analysis' in result:
            output.append(f"\n📊 문제 분석:")
            output.append(f"   {result['problem_analysis']}")

        if 'root_cause' in result:
            output.append(f"\n🔍 근본 원인:")
            output.append(f"   {result['root_cause']}")

        if 'recommendations' in result and result['recommendations']:
            output.append(f"\n💡 추천 제약조건 및 개선 방안:")
            for i, rec in enumerate(result['recommendations'], 1):
                output.append(f"\n   [{i}] {rec.get('constraint_type', 'N/A')} (우선순위: {rec.get('priority', 'N/A')})")
                output.append(f"       설명: {rec.get('constraint_description', 'N/A')}")
                output.append(f"       구현: {rec.get('implementation', 'N/A')}")
                output.append(f"       예상 효과: {rec.get('expected_impact', 'N/A')}")

        if 'additional_suggestions' in result and result['additional_suggestions']:
            output.append(f"\n📝 추가 제안:")
            for suggestion in result['additional_suggestions']:
                output.append(f"   • {suggestion}")

        if 'warnings' in result and result['warnings']:
            output.append(f"\n⚠️  주의사항:")
            for warning in result['warnings']:
                output.append(f"   • {warning}")

        output.append("\n" + "=" * 80)

        return "\n".join(output)


# 프롬프트 예제 저장
EXAMPLE_PROMPTS = {
    "bottleneck_cip": {
        "problem": "CIP(Clean In Place) 시간이 병목이 되어 전체 생산성이 저하되고 있습니다. CIP는 공정 간 설비 세척 작업으로 평균 30분 소요되며, 하루 평균 8회 발생합니다.",
        "context": {
            "설비 수": 5,
            "일일 작업 수": 25,
            "CIP 평균 시간": "30분",
            "CIP 빈도": "8회/일",
            "총 CIP 시간": "240분/일"
        }
    },
    "machine_overload": {
        "problem": "MC001 설비가 과부하 상태(가동률 95%)이며, 자주 고장이 발생합니다. 반면 MC005는 저가동(가동률 60%) 상태입니다.",
        "context": {
            "MC001 가동률": "95%",
            "MC005 가동률": "60%",
            "MC001 고장 빈도": "월 3회",
            "평균 수리 시간": "4시간"
        }
    },
    "tardiness_high": {
        "problem": "납기 지연이 자주 발생합니다. 특히 우선순위가 높은 긴급 오더의 납기 준수율이 75%에 불과합니다.",
        "context": {
            "전체 납기 준수율": "82%",
            "긴급 오더 납기 준수율": "75%",
            "평균 지연 시간": "48시간",
            "긴급 오더 비율": "20%"
        }
    },
    "quality_issue": {
        "problem": "3주차마다 품질 불량률이 급증합니다(3.5% → 4.5%). 패턴을 보면 공구 마모와 연관이 있는 것 같습니다.",
        "context": {
            "평균 불량률": "3.5%",
            "피크 불량률": "4.5%",
            "불량 주기": "3주",
            "현재 공구 교체 주기": "4주"
        }
    }
}


def save_example_prompts():
    """
    예제 프롬프트 저장
    """
    output_path = Path(__file__).parent / 'example_prompts.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(EXAMPLE_PROMPTS, f, indent=2, ensure_ascii=False)
    print(f"✅ 예제 프롬프트 저장 완료: {output_path}")


def demo_without_api():
    """
    API 없이 데모 실행 (미리 정의된 응답 사용)
    """
    print("=" * 80)
    print("🎭 LLM 제약조건 추천 데모 (Mock 응답)")
    print("=" * 80)

    # Mock 응답 (실제 GPT-4 응답 예시)
    mock_response = {
        "problem_analysis": "CIP 시간이 하루 240분(4시간)으로 전체 생산 시간의 약 20%를 차지하고 있어 병목이 발생하고 있습니다. 빈번한 CIP로 인해 설비 가동률이 저하되고 전체 Makespan이 증가하는 문제가 있습니다.",
        "root_cause": "1) 소규모 배치로 인한 빈번한 공정 전환, 2) CIP 시간 최적화 부족, 3) 설비 간 작업 배분 불균형으로 인한 CIP 중복",
        "recommendations": [
            {
                "constraint_type": "Setup Time Constraint",
                "constraint_description": "공정간 설정시간(CIP 포함) 10% 감소 제약 추가",
                "implementation": "APS 스케줄링 시 동일 품목/공정을 연속 배치하여 CIP 빈도 감소. 배치 크기를 30% 증가시켜 공정 전환 횟수 감소.",
                "expected_impact": "CIP 시간 240분 → 190분 (21% 감소), Makespan 약 50분 단축",
                "priority": "High"
            },
            {
                "constraint_type": "Machine Constraint",
                "constraint_description": "CIP 전용 시간대 지정 제약",
                "implementation": "11:30-12:00, 17:30-18:00을 CIP 전용 시간대로 지정하여 집중 처리. 해당 시간대에는 신규 작업 시작 금지.",
                "expected_impact": "CIP 대기 시간 감소, 설비 가동률 3-5% 향상",
                "priority": "Medium"
            },
            {
                "constraint_type": "Precedence Constraint",
                "constraint_description": "품목 유사성 기반 작업 순서 제약",
                "implementation": "동일 계열 품목은 연속 스케줄링. 예: 프레임 A → 프레임 B → 브라켓 순서로 배치하여 CIP 강도 완화.",
                "expected_impact": "CIP 평균 시간 30분 → 25분 (간소화된 세척)",
                "priority": "High"
            }
        ],
        "additional_suggestions": [
            "CIP 자동화 설비 도입 검토 (투자비용 vs 효과 분석 필요)",
            "배치 크기 최적화 알고리즘 적용 (RL 기반 동적 배치 조정)",
            "설비 전용화 고려 (MC001: 프레임 전용, MC002: 브라켓 전용 등)"
        ],
        "warnings": [
            "배치 크기 증가 시 재고 비용 증가 가능성 있음",
            "CIP 시간 단축 시 품질 문제 발생 위험 → 품질 모니터링 강화 필요",
            "설비 전용화 시 유연성 감소 → 긴급 오더 대응 능력 저하 가능"
        ]
    }

    # Mock 결과 출력
    recommender = ConstraintRecommender.__new__(ConstraintRecommender)
    formatted = recommender.format_recommendations(mock_response)
    print(formatted)

    print("\n💾 예제 프롬프트 저장 중...")
    save_example_prompts()


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        # API 없이 데모 실행
        demo_without_api()
    else:
        print("""
사용법:
  1. API 없이 데모 실행:
     python constraint_recommender.py demo

  2. 실제 API 사용:
     export OPENAI_API_KEY=your-api-key  # 또는 ANTHROPIC_API_KEY
     python -c "
from constraint_recommender import ConstraintRecommender

recommender = ConstraintRecommender(model='gpt-4', provider='openai')
result = recommender.recommend(
    problem_description='CIP 시간이 병목이야',
    context={'CIP 평균 시간': '30분', 'CIP 빈도': '8회/일'}
)
print(recommender.format_recommendations(result))
"
        """)
