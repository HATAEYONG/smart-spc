"""
AI Prompt Service
AI 프롬프트 실행 및 결과 관리 서비스
"""

import hashlib
import json
from typing import Dict, Any, Optional
from django.utils import timezone
from apps.spc.ai_prompts import AIPromptManager
from apps.spc.models_qa import AIOutput


class AIPromptService:
    """AI 프롬프트 실행 서비스"""

    @staticmethod
    def get_input_hash(inputs: Dict[str, Any]) -> str:
        """입력 데이터 해시 생성 (중복 방지)"""
        inputs_str = json.dumps(inputs, sort_keys=True)
        return hashlib.sha256(inputs_str.encode()).hexdigest()

    @staticmethod
    def get_formatted_prompt(use_case: str, inputs: Dict[str, Any], language: str = 'ko') -> Dict[str, Any]:
        """
        포맷된 프롬프트 반환

        Args:
            use_case: 사용 케이스 (PROCESS_DESIGN, CRITERIA_CHECKLIST, QCOST_CLASSIFY, COPQ_REPORT)
            inputs: 입력 데이터
            language: 언어 (ko/en/zh)

        Returns:
            {
                'use_case': str,
                'prompt_name': str,
                'version': str,
                'formatted_prompt': str,
                'input_schema': dict,
                'output_schema': dict
            }
        """
        try:
            prompt_info = AIPromptManager.get_prompt(use_case, language)
            formatted_prompt = AIPromptManager.format_prompt(use_case, inputs)

            return {
                'use_case': use_case,
                'prompt_name': prompt_info['prompt_template'].split('\n')[0].replace('"""', '').strip(),
                'version': prompt_info['version'],
                'formatted_prompt': formatted_prompt,
                'input_schema': prompt_info['input_schema'],
                'output_schema': prompt_info['output_schema'],
            }
        except ValueError as e:
            raise ValueError(f"Invalid use case: {e}")

    @staticmethod
    def execute_prompt(
        use_case: str,
        inputs: Dict[str, Any],
        site_id: int,
        user_id: int,
        language: str = 'ko',
        model_name: str = 'gpt-4',
        mock_output: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        AI 프롬프트 실행 및 결과 저장

        Args:
            use_case: 사용 케이스
            inputs: 입력 데이터
            site_id: 사이트 ID
            user_id: 사용자 ID
            language: 언어
            model_name: AI 모델 이름
            mock_output: 모의 출력 (테스트용, 실제로는 LLM API 호출 필요)

        Returns:
            {
                'use_case': str,
                'ai_output_id': int,
                'output_json': dict,
                'confidence': float,
                'model_name': str,
                'created_at': datetime
            }
        """
        # 중복 체크
        input_hash = AIPromptService.get_input_hash(inputs)

        existing = AIOutput.objects.filter(
            input_hash=input_hash,
            use_case=use_case
        ).first()

        if existing:
            return {
                'use_case': use_case,
                'ai_output_id': existing.ai_id,
                'output_json': existing.output_json,
                'confidence': existing.confidence,
                'model_name': existing.model_name,
                'created_at': existing.created_dt,
                'cached': True
            }

        # 프롬프트 생성
        prompt_info = AIPromptManager.get_prompt(use_case, language)

        # 실제 구현에서는 여기서 LLM API 호출
        # 예: openai.ChatCompletion.create(...) 또는 anthropic.Anthropic().messages.create(...)
        # 현재는 모의 출력 사용
        if mock_output is None:
            mock_output = AIPromptService._generate_mock_output(use_case, inputs)

        # AI Output 저장
        ai_output = AIOutput.objects.create(
            site_id=site_id,
            use_case=use_case,
            input_hash=input_hash,
            model_name=model_name,
            prompt_version=prompt_info['version'],
            output_json=mock_output,
            confidence=mock_output.get('confidence', 0.85),
            created_dt=timezone.now(),
            created_by=user_id
        )

        return {
            'use_case': use_case,
            'ai_output_id': ai_output.ai_id,
            'output_json': ai_output.output_json,
            'confidence': ai_output.confidence,
            'model_name': ai_output.model_name,
            'created_at': ai_output.created_dt,
            'cached': False
        }

    @staticmethod
    def _generate_mock_output(use_case: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """모의 출력 생성 (테스트용)"""
        if use_case == 'PROCESS_DESIGN':
            return {
                'process_flow': [
                    {'seq': 10, 'step': 'CNC가공', 'inspection_points': ['내경', '외경', '깊이']},
                    {'seq': 20, 'step': '세척', 'inspection_points': ['외관', '이물']},
                    {'seq': 30, 'step': '조립', 'inspection_points': ['조립 완성도', '간섭']}
                ],
                'inspection_points': [
                    {
                        'step': 'CNC가공',
                        'type': 'DIM',
                        'ctq': [{'name': '내경', 'lsl': 10.00, 'usl': 10.02, 'unit': 'mm', 'criticality': 'C'}],
                        'frequency': 'EACH_LOT',
                        'method': '캘리퍼스/3차원',
                        'sample_size': 5,
                        'risk_notes': ['온도 보정 필요', '공구 마모 확인']
                    }
                ],
                'assumptions': [
                    'CNC 가공 공정능력 Cpk ≥ 1.33 가정',
                    '세척 공정에서 외관 불량 90% 제거 가정'
                ],
                'risks': [
                    {'risk': '온도 변화로 인한 치수 불량', 'probability': '중', 'mitigation': '2시간마다 보정'}
                ],
                'implementation_notes': [
                    '검사원 교육: 1주간 집중 교육 필요',
                    '측정기기: 캘리퍼스 교정 주기 설정 필요'
                ],
                'confidence': 0.87
            }

        elif use_case == 'CRITERIA_CHECKLIST':
            return {
                'criteria_table': [
                    {
                        'category': '외관',
                        'check': '찍힘/스크래치',
                        'method': '육안(조도 1000lx)',
                        'accept': '0',
                        'reject': '1 이상',
                        'action': 'B',
                        'sample_photos': ['https://example.com/photo1.jpg']
                    },
                    {
                        'category': '조립',
                        'check': '토크마킹',
                        'method': '마킹 확인',
                        'accept': '있음',
                        'reject': '없음',
                        'action': 'B'
                    }
                ],
                'checklist': [
                    {'no': 1, 'question': '조립 토크 마킹이 있는가?', 'type': 'YESNO', 'photo_required': True},
                    {'no': 2, 'question': '이물 부착이 없는가?', 'type': 'YESNO', 'photo_required': True}
                ],
                'training_notes': [
                    '검사 전 조도 1000lux 확인',
                    '사진 촬영 시 각도 지정'
                ],
                'edge_cases': [
                    {'case': '경계선 불량', 'handling': '재검 후 결정'},
                    {'case': '판단 불가', 'handling': '품질팀 자문'}
                ],
                'confidence': 0.92
            }

        elif use_case == 'QCOST_CLASSIFY':
            return {
                'qcost_classification': {
                    'lvl1': 'INTERNAL_FAILURE',
                    'lvl2': 'REWORK',
                    'lvl3': '재세척',
                    'item_candidate': '재세척/재작업 인건비',
                    'copq_flag': True,
                    'confidence_score': 0.95
                },
                'link_suggestions': {
                    'lot_no': 'L-2026-0112',
                    'run_id': None,
                    'spc_event_id': None,
                    'capa_id': None
                },
                'confidence': 0.82,
                'rationale': [
                    '세척 불량으로 인한 재세척 비용 → 내부실패비용',
                    '검사 이후 발생한 불량이므로 예방/평가 비용 아님',
                    'COPQ 대상: 불량으로 인한 추가 비용이므로 COPQ=True'
                ]
            }

        elif use_case == 'COPQ_REPORT':
            return {
                'executive_summary': '2026년 1월 COPQ율 3.42%로 전월 대비 0.5%p 개선됨. 그러나 치수불량이 주요 원인으로 지속되어 개선이 시급함.',
                'key_findings': [
                    '치수불량이 전체 COPQ의 29%를 차지하여 최대 문제',
                    'SPC 추세(TREND)이 5건 감지되어 공정 이상 징후 있음',
                    'Cpk<1.33 항목이 3개로 공정능력 개선 필요'
                ],
                'drivers': [
                    {
                        'name': '치수불량',
                        'impact': '높음',
                        'copq_contribution': '29%',
                        'evidence': ['스크랩비 1,200만원', 'SPC 추세 5건 (내경 Xbar-R)', '재세척 건수: 월 42건'],
                        'root_cause': 'CNC 온도 변화, 공구 마모'
                    },
                    {
                        'name': '스크래치',
                        'impact': '중간',
                        'copq_contribution': '20%',
                        'evidence': ['재작업비 800만원', '재세척 건수: 월 61건']
                    }
                ],
                'recommended_actions': [
                    {
                        'priority': 1,
                        'action': 'CNC 온도/보정 표준화',
                        'owner': '생산기술팀',
                        'due': '2026-02-10',
                        'expected_effect': '치수불량 20% 감소',
                        'estimated_cost': '교육 500만원 + 자재화 200만원'
                    },
                    {
                        'priority': 2,
                        'action': '세척 공정 파라미터 최적화',
                        'owner': '품질팀',
                        'due': '2026-02-28',
                        'expected_effect': '스크래치 30% 감소'
                    }
                ],
                'risk_watchlist': [
                    {
                        'risk': '신규 제품 출시 예정',
                        'impact': '불량률 증가 가능성',
                        'mitigation': '사전 검사 계획 수립'
                    }
                ],
                'appendix': {
                    'charts_needed': [
                        'Pareto Chart (불량 유형별)',
                        'COPQ Trend (월별 추이)',
                        'SPC Violations (관리도 위반 건수)',
                        'Top 10 Defects'
                    ],
                    'data_sources': [
                        'Q-COST Entry DB',
                        'Inspection Result DB',
                        'SPC Event DB',
                        'CAPA Case DB'
                    ]
                },
                'confidence': 0.88
            }

        return {'error': 'Unknown use case'}

    @staticmethod
    def get_available_use_cases() -> list:
        """사용 가능한 Use Case 목록 반환"""
        return [
            {
                'use_case': 'PROCESS_DESIGN',
                'name': '검수 프로세스 설계',
                'description': '제품/공정 정보를 기반으로 검사 프로세스와 검사 지점을 자동 설계'
            },
            {
                'use_case': 'CRITERIA_CHECKLIST',
                'name': '검수 기준표 + 체크리스트 생성',
                'description': '불량 모드별 검사 기준표와 검사자용 체크리스트 자동 생성'
            },
            {
                'use_case': 'QCOST_CLASSIFY',
                'name': 'Q-COST 분류/자동 태깅',
                'description': '품질비용 발생 내용을 4대 분류(예방/평가/내부실패/외부실패)로 자동 분류'
            },
            {
                'use_case': 'COPQ_REPORT',
                'name': 'COPQ 분석 리포트',
                'description': 'COPQ 데이터를 분석하여 경영진단용 요약보고서 자동 생성'
            }
        ]

    @staticmethod
    def get_ai_output(ai_output_id: int) -> Optional[Dict[str, Any]]:
        """AI 출력 결과 조회"""
        try:
            ai_output = AIOutput.objects.get(ai_id=ai_output_id)
            return {
                'ai_output_id': ai_output.ai_id,
                'use_case': ai_output.use_case,
                'output_json': ai_output.output_json,
                'confidence': ai_output.confidence,
                'model_name': ai_output.model_name,
                'prompt_version': ai_output.prompt_version,
                'created_at': ai_output.created_dt,
                'created_by': ai_output.created_by
            }
        except AIOutput.DoesNotExist:
            return None

    @staticmethod
    def list_ai_outputs(site_id: int, use_case: Optional[str] = None, limit: int = 50) -> list:
        """AI 출력 결과 목록 조회"""
        queryset = AIOutput.objects.filter(site_id=site_id)

        if use_case:
            queryset = queryset.filter(use_case=use_case)

        outputs = queryset.order_by('-created_dt')[:limit]

        return [
            {
                'ai_output_id': output.ai_id,
                'use_case': output.use_case,
                'model_name': output.model_name,
                'confidence': output.confidence,
                'created_at': output.created_dt,
                'created_by': output.created_by
            }
            for output in outputs
        ]
