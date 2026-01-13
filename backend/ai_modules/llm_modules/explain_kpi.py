"""
KPI 영향 분석 자연어 설명 생성 모듈
온톨로지 추적 결과 → LLM 기반 자연어 설명 + 개선 방안
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


class KPIExplainer:
    """
    KPI 영향 분석 결과를 자연어로 설명하는 시스템
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
        return """당신은 APS(Advanced Planning and Scheduling) 시스템의 KPI 분석 전문가입니다.
온톨로지 기반으로 추적된 KPI 변화의 인과관계를 분석하고, 이해하기 쉬운 자연어로 설명합니다.

**역할**:
1. 인과 체인 분석 (근본 원인 → 중간 이벤트 → KPI 영향)
2. 문제의 심각도 평가
3. 구체적인 개선 방안 제시
4. 예상 효과 제시

**설명 스타일**:
- 명확하고 간결하게
- 숫자와 지표를 포함
- 인과관계를 단계적으로 설명
- 현장 실무자가 이해할 수 있는 언어 사용

**응답 형식** (JSON):
{
  "summary": "KPI 변화 요약 (1-2문장)",
  "causal_analysis": {
    "root_cause": "근본 원인",
    "impact_chain": ["이벤트1 → 이벤트2 → ... → KPI 변화"],
    "severity_assessment": "심각도 평가 (Critical/High/Medium/Low)"
  },
  "detailed_explanation": "상세 설명 (2-3 문단)",
  "recommendations": [
    {
      "action": "개선 조치",
      "expected_impact": "예상 효과",
      "priority": "우선순위 (High/Medium/Low)",
      "implementation_difficulty": "구현 난이도 (Easy/Medium/Hard)"
    }
  ],
  "next_steps": ["즉시 실행 가능한 단계들"]
}
"""

    def explain(
        self,
        kpi_name: str,
        kpi_current: float,
        kpi_target: float,
        causal_chains: List[Dict],
        bottlenecks: Optional[List[Dict]] = None,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        KPI 영향 분석 설명 생성

        Args:
            kpi_name: KPI 이름 (예: '생산효율', '총 지연시간')
            kpi_current: 현재 값
            kpi_target: 목표 값
            causal_chains: 인과 체인 리스트 (kpi_tracer.trace_kpi_impact() 결과)
            bottlenecks: 병목 설비 리스트 (선택사항)
            context: 추가 컨텍스트 (설비 수, 작업 수 등)

        Returns:
            설명 결과 딕셔너리
        """
        # 사용자 프롬프트 구성
        user_prompt = f"""**KPI 분석 요청**:

**KPI 정보**:
- KPI 이름: {kpi_name}
- 현재 값: {kpi_current}
- 목표 값: {kpi_target}
- 편차: {kpi_current - kpi_target:.2f} ({'초과' if kpi_current > kpi_target else '미달'})

**인과 체인**:
"""

        for i, chain in enumerate(causal_chains, 1):
            user_prompt += f"\n[체인 {i}]\n"
            user_prompt += f"  이벤트: {chain['event']}\n"
            user_prompt += f"  설명: {chain['description']}\n"
            user_prompt += f"  관계: {chain['relation']}\n"
            user_prompt += f"  심각도: {chain['severity']:.2f}\n"

            if chain.get('root_causes'):
                user_prompt += f"  근본 원인:\n"
                for cause in chain['root_causes']:
                    user_prompt += f"    → {cause['description']} (depth: {cause['depth']})\n"
                    if cause.get('sub_causes'):
                        for sub in cause['sub_causes']:
                            user_prompt += f"      → {sub['description']} (depth: {sub['depth']})\n"

        if bottlenecks:
            user_prompt += f"\n**병목 설비**:\n"
            for bottleneck in bottlenecks:
                user_prompt += f"  • {bottleneck['equipment_id']}: 가동률 {bottleneck['utilization']*100:.1f}% (심각도: {bottleneck['severity']:.2f})\n"

        if context:
            user_prompt += f"\n**현재 상황**:\n"
            for key, value in context.items():
                user_prompt += f"  - {key}: {value}\n"

        user_prompt += "\n위 정보를 바탕으로 KPI 변화를 분석하고 개선 방안을 JSON 형식으로 제시해주세요."

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
                "summary": response[:200],
                "detailed_explanation": response,
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

    def format_explanation(self, result: Dict) -> str:
        """
        설명 결과를 사람이 읽기 쉬운 형식으로 포맷팅
        """
        output = []

        output.append("=" * 80)
        output.append("📊 KPI 영향 분석 설명")
        output.append("=" * 80)

        if 'summary' in result:
            output.append(f"\n💡 요약:")
            output.append(f"   {result['summary']}")

        if 'causal_analysis' in result:
            analysis = result['causal_analysis']
            output.append(f"\n🔍 인과관계 분석:")

            if 'root_cause' in analysis:
                output.append(f"   근본 원인: {analysis['root_cause']}")

            if 'impact_chain' in analysis:
                output.append(f"   영향 체인:")
                for step in analysis['impact_chain']:
                    output.append(f"      {step}")

            if 'severity_assessment' in analysis:
                output.append(f"   심각도: {analysis['severity_assessment']}")

        if 'detailed_explanation' in result:
            output.append(f"\n📝 상세 설명:")
            for paragraph in result['detailed_explanation'].split('\n'):
                if paragraph.strip():
                    output.append(f"   {paragraph}")

        if 'recommendations' in result and result['recommendations']:
            output.append(f"\n💡 개선 방안:")
            for i, rec in enumerate(result['recommendations'], 1):
                output.append(f"\n   [{i}] {rec.get('action', 'N/A')}")
                output.append(f"       예상 효과: {rec.get('expected_impact', 'N/A')}")
                output.append(f"       우선순위: {rec.get('priority', 'N/A')}")
                output.append(f"       구현 난이도: {rec.get('implementation_difficulty', 'N/A')}")

        if 'next_steps' in result and result['next_steps']:
            output.append(f"\n🚀 다음 단계:")
            for step in result['next_steps']:
                output.append(f"   • {step}")

        output.append("\n" + "=" * 80)

        return "\n".join(output)


def demo_with_mock_response():
    """
    API 없이 데모 실행 (미리 정의된 응답 사용)
    """
    print("=" * 80)
    print("🎭 KPI 설명 데모 (Mock 응답)")
    print("=" * 80)

    # Mock 인과 체인 (kpi_tracer 예제 결과와 동일)
    causal_chains = [
        {
            'event': 'Event_E003',
            'relation': 'decreases',
            'description': '전체 생산 일정 지연',
            'severity': 0.8,
            'root_causes': [
                {
                    'cause': 'Event_E002',
                    'relation': 'leadsTo',
                    'description': '작업 대기 시간 증가 (평균 45분)',
                    'depth': 1,
                    'sub_causes': [
                        {
                            'cause': 'Event_E001',
                            'relation': 'causes',
                            'description': 'MC001 설비 과부하 발생 (가동률 95%)',
                            'depth': 2,
                            'sub_causes': []
                        }
                    ]
                }
            ]
        }
    ]

    bottlenecks = [
        {
            'equipment_id': 'MC001',
            'utilization': 0.95,
            'severity': 0.5
        }
    ]

    # Mock 응답 (실제 GPT-4 응답 예시)
    mock_response = {
        "summary": "MC001 설비의 과부하(가동률 95%)로 인해 작업 대기시간이 평균 45분 증가했고, 이로 인해 전체 생산 일정이 지연되어 생산효율 KPI가 목표(85%) 대비 13% 낮은 72%로 하락했습니다.",
        "causal_analysis": {
            "root_cause": "MC001 설비 과부하 (가동률 95%)",
            "impact_chain": [
                "MC001 과부하 발생",
                "→ 작업 대기 시간 45분 증가",
                "→ 전체 생산 일정 지연",
                "→ 생산효율 KPI 13% 하락 (85% → 72%)"
            ],
            "severity_assessment": "High"
        },
        "detailed_explanation": """MC001 설비의 과부하 상태가 전체 생산 시스템에 연쇄적인 영향을 미치고 있습니다.

첫째, MC001의 가동률이 95%로 매우 높아 새로운 작업이 할당될 때마다 긴 대기 시간이 발생합니다. 평균 45분의 대기 시간은 후속 공정에도 영향을 미쳐 전체 생산 흐름이 지연되고 있습니다.

둘째, 이러한 지연이 누적되면서 전체 생산 일정이 계획 대비 뒤처지고 있으며, 결과적으로 생산효율 KPI가 목표 85% 대비 13%p 낮은 72%를 기록하고 있습니다. 이는 심각한 수준의 성능 저하로, 즉각적인 개선 조치가 필요한 상태입니다.

현재 MC002 설비의 가동률이 65%로 여유가 있는 점을 고려하면, 작업 재배분을 통한 부하 분산이 효과적일 것으로 판단됩니다.""",
        "recommendations": [
            {
                "action": "MC001의 일부 작업을 MC002로 재배치 (부하 분산)",
                "expected_impact": "MC001 가동률 95% → 85%, 대기 시간 45분 → 20분 감소, 생산효율 72% → 80% 개선",
                "priority": "High",
                "implementation_difficulty": "Easy"
            },
            {
                "action": "MC001 예지보전 실시 (고장 리스크 감소)",
                "expected_impact": "설비 신뢰성 향상, 비계획 중단 50% 감소",
                "priority": "High",
                "implementation_difficulty": "Medium"
            },
            {
                "action": "긴급 작업에 대한 우선순위 재조정",
                "expected_impact": "중요 작업 납기 준수율 75% → 90% 개선",
                "priority": "Medium",
                "implementation_difficulty": "Easy"
            },
            {
                "action": "배치 크기 최적화 (작은 배치 통합)",
                "expected_impact": "공정 전환 횟수 30% 감소, Setup 시간 절감",
                "priority": "Medium",
                "implementation_difficulty": "Medium"
            }
        ],
        "next_steps": [
            "MC001의 현재 작업 목록 검토 및 MC002로 이전 가능한 작업 선별",
            "작업 재배치 시뮬레이션 실행 (예상 효과 검증)",
            "MC001 예지보전 일정 수립 (다음 주 내)",
            "긴급 작업 우선순위 규칙 재검토 및 수정",
            "1주 후 KPI 재측정 및 효과 평가"
        ]
    }

    # Mock 결과 출력
    explainer = KPIExplainer.__new__(KPIExplainer)
    formatted = explainer.format_explanation(mock_response)
    print(formatted)

    print("\n💾 Mock 응답 저장 중...")
    output_path = Path(__file__).parent / 'kpi_explanation_example.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(mock_response, f, indent=2, ensure_ascii=False)
    print(f"✅ 저장 완료: {output_path}")


def integrated_demo():
    """
    kpi_tracer + explain_kpi 통합 데모
    """
    print("\n" + "=" * 80)
    print("🔗 통합 데모: KPI 추적 + 설명 생성")
    print("=" * 80)

    # Step 1: KPI 추적
    print("\n[Step 1] KPI 영향 분석 (온톨로지 추적)...")
    try:
        from kpi_tracer import create_example_scenario
        tracer, causal_chains, bottlenecks = create_example_scenario()
        print("✅ 인과 체인 추적 완료")
    except Exception as e:
        print(f"⚠️  kpi_tracer 실행 실패: {e}")
        print("   Mock 데이터를 사용합니다.")
        causal_chains = [
            {
                'event': 'Event_E003',
                'description': '전체 생산 일정 지연',
                'relation': 'decreases',
                'severity': 0.8,
                'root_causes': []
            }
        ]
        bottlenecks = [{'equipment_id': 'MC001', 'utilization': 0.95, 'severity': 0.5}]

    # Step 2: LLM 설명 생성
    print("\n[Step 2] LLM 기반 자연어 설명 생성...")
    print("   (API 키가 없으므로 Mock 응답 사용)")

    demo_with_mock_response()


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'integrated':
        # 통합 데모 실행
        integrated_demo()
    else:
        # 기본 데모 실행
        print("""
사용법:
  1. Mock 응답으로 데모 실행:
     python explain_kpi.py

  2. 통합 데모 (kpi_tracer + explain_kpi):
     python explain_kpi.py integrated

  3. 실제 API 사용:
     export OPENAI_API_KEY=your-api-key  # 또는 ANTHROPIC_API_KEY
     python -c "
from explain_kpi import KPIExplainer

explainer = KPIExplainer(model='gpt-4', provider='openai')

causal_chains = [...]  # kpi_tracer 결과
bottlenecks = [...]

result = explainer.explain(
    kpi_name='생산효율',
    kpi_current=72.0,
    kpi_target=85.0,
    causal_chains=causal_chains,
    bottlenecks=bottlenecks
)

print(explainer.format_explanation(result))
"
        """)

        demo_with_mock_response()
