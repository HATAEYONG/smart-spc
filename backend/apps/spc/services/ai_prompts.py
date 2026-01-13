"""
AI Prompt Service
검수 기준·리포트 자동화를 위한 AI 프롬프트 관리 시스템
"""

class AIPromptManager:
    """AI 프롬프트 관리자"""

    # Use Case별 프롬프트 템플릿
    PROMPTS = {
        "PROCESS_DESIGN": {
            "name": "검수 프로세스 설계",
            "version": "1.0",
            "prompt_template": """너는 제조 품질/검수 프로세스 컨설턴트이자 QA 엔지니어다. 결과는 반드시 JSON 스키마를 지켜라. 근거/가정/리스크를 분리해라.

# 입력 정보
- 회사/사이트: {company[industry]}, {company[site]}
- 제품: {product[item_name]}
- 공정: {product[process]}
- 제약조건: 검사 인원 {constraints[inspection_headcount]}명, 교대 {constraints[shift]}조
- 알려진 불량: {known_defects}
- 고객 요구사항: {customer_requirements}

# 요구사항
1. 각 공정 단계별 검사 지점을 설계하라
2. 품질특성(CTQ)별 규격과 판정 기준을 정의하라
3. 검사 주기와 방법을 제안하라
4. 리스크와 완화 조치를 식별하라
5. 근거(assumptions)와 가정사항을 명시하라

# 출력 JSON 스키마
```json
{{
  "process_flow": [
    {{"seq": 10, "step": "CNC가공", "inspection_points": ["내경", "외경", "깊이"]}},
    {{"seq": 20, "step": "세척", "inspection_points": ["외관", "이물"]}},
    {{"seq": 30, "step": "조립", "inspection_points": ["조립 완성도", "간섭"]}}
  ],
  "inspection_points": [
    {{
      "step": "CNC가공",
      "type": "DIM",
      "ctq": [{{"name": "내경", "lsl": 10.00, "usl": 10.02, "unit": "mm", "criticality": "C"}}],
      "frequency": "EACH_LOT",
      "method": "캘리퍼스/3차원",
      "sample_size": 5,
      "risk_notes": ["온도 보정 필요", "공구 마모 확인"]
    }}
  ],
  "assumptions": [
    "CNC 가공 공정능력 Cpk ≥ 1.33 가정",
    "세척 공정에서 외관 불량 90% 제거 가정"
  ],
  "risks": [
    {{"risk": "온도 변화로 인한 치수 불량", "probability": "중", "mitigation": "2시간마다 보정"}}
  ],
  "implementation_notes": [
    "검사원 교육: 1주간 집중 교육 필요",
    "측정기기: 캘리퍼스 교정 주기 설정 필요"
  ]
}}
```

# 주의사항
- 모든 수치는 입력 정보를 기반으로 추정하라
- 실제 구현 전에는 전문가 검토가 필요하다는 disclaimer를 포함하라
- 리스크는 확률적(높음/중간/낮음)과 완화 조치를 함께 제시하라
""",
            "input_schema": {
                "company": {
                    "industry": "string (자동차부품, 전자, 식품 등)",
                    "site": "string (공장 이름)"
                },
                "product": {
                    "item_name": "string (제품명)",
                    "process": "string (공정: CNC+세척+조립 등)"
                },
                "constraints": {
                    "inspection_headcount": "integer (검사 인원 수)",
                    "shift": "integer (교대 수)"
                },
                "known_defects": "array<string> (알려진 불량 유형)",
                "customer_requirements": "array<string> (고객 요구사항)"
            },
            "output_schema": {
                "process_flow": "array of objects (공정 흐름)",
                "inspection_points": "array of objects (검사 지점 상세)",
                "assumptions": "array of strings (가정사항)",
                "risks": "array of objects (리스크 식별)",
                "implementation_notes": "array of strings (구현 노트)"
            }
        },

        "CRITERIA_CHECKLIST": {
            "name": "검수 기준표 + 체크리스트 생성",
            "version": "1.0",
            "prompt_template": """# 입력 정보
- 제품: {item}
- 공정: {step}
- 검사 유형: {inspection_type}
- 불량 모드: {defect_modes}
- 합격 정책: {acceptance_policy}
- 언어: {language}

# 요구사항
1. 불량 모드별 검사 기준표를 작성하라
2. 각 기준별 판정 방법과 합격/불합격 기준을 명시하라
3. 조치(action) 등급을 부여하라 (A: 출하가능, B: 재작업, C: 폐기)
4. 검사자용 체크리스트를 생성하라
5. 훈련 노트와 엣지 케이스를 포함하라

# 출력 JSON 스키마
```json
{{
  "criteria_table": [
    {{
      "category": "외관",
      "check": "찍힘/스크래치",
      "method": "육안(조도 1000lx)",
      "accept": "0",
      "reject": "1 이상",
      "action": "B",
      "sample_photos": ["사진 URL 예시"]
    }},
    {{
      "category": "조립",
      "check": "토크마킹",
      "method": "마킹 확인",
      "accept": "있음",
      "reject": "없음",
      "action": "B"
    }}
  ],
  "checklist": [
    {{"no": 1, "question": "조립 토크 마킹이 있는가?", "type": "YESNO", "photo_required": true}},
    {{"no": 2, "question": "이물 부착이 없는가?", "type": "YESNO", "photo_required": true}}
  ],
  "training_notes": [
    "검사 전 조도 1000lux 확인",
    "사진 촬영 시 각도 지정"
  ],
  "edge_cases": [
    {{"case": "경계선 불량", "handling": "재검 후 결정"}},
    {{"case": "판단 불가", "handling": "품질팀 자문"}}
  ]
}}
```
""",
            "input_schema": {
                "item": "string (제품명)",
                "step": "string (공정 단계)",
                "inspection_type": "string (검사 유형: DIM/ATTR/SENSORY/COMBO)",
                "defect_modes": "array<string> (불량 모드)",
                "acceptance_policy": {
                    "A": "string (A급 조치)",
                    "B": "string (B급 조치)",
                    "C": "string (C급 조치)"
                },
                "language": "string (ko/en/zh)"
            },
            "output_schema": {
                "criteria_table": "array of objects (검사 기준표)",
                "checklist": "array of objects (체크리스트)",
                "training_notes": "array of strings (훈련 노트)",
                "edge_cases": "array of objects (엣지 케이스)"
            }
        },

        "QCOST_CLASSIFY": {
            "name": "Q-COST 분류/자동 태깅",
            "version": "1.0",
            "prompt_template": """# 입력 정보
- 텍스트: {text}
- 금액: {amount}
- 컨텍스트: {context}

# 요구사항
1. 품질코스트 4대 분류(예방/평가/내부실패/외부실패) 중 하나로 분류하라
2. 세부 항목(예: 재세척비, 재작업비, 폐기비, 보증비 등)까지 식별하라
3. COPQ(Cost of Poor Quality) 여부를 판단하라
4. confidence(0~1)와 근거(rationale)를 제시하라
5. 연결 가능한 객체(lot_no, capa_id 등)를 제안하라

# Q-COST 분류 체계
- **예방비용 (PREVENTION)**: 품질 시스템 유지, 교육, 품질 기획
- **평가비용 (APPRAISAL)**: 검사, 테스트, 감사, 프로세스 검증
- **내부 실패비용 (INTERNAL_FAILURE)**: 재작업, 재세척, 폐기, 재작업에 따른 부수품 손실
- **외부 실패비용 (EXTERNAL_FAILURE)**: 보증, 클레임, 반품, 리콜, 평판 손상

# 출력 JSON 스키마
```json
{{
  "qcost_classification": {{
    "lvl1": "INTERNAL_FAILURE",
    "lvl2": "REWORK",
    "lvl3": "재세척",
    "item_candidate": "재세척/재작업 인건비",
    "copq_flag": true,
    "confidence_score": 0.95
  }},
  "link_suggestions": {{
    "lot_no": "L-2026-0112",
    "run_id": null,
    "spc_event_id": null,
    "capa_id": null
  }},
  "confidence": 0.82,
  "rationale": [
    "세척 불량으로 인한 재세척 비용 → 내부실패비용",
    "검사 이후 발생한 불량이므로 예방/평가 비용 아님",
    "COPQ 대상: 불량으로 인한 추가 비용이므로 COPQ=True"
  ]
}}
```
""",
            "input_schema": {
                "text": "string (코스트 발생 설명)",
                "amount": "number (금액)",
                "context": {
                    "dept": "string (부서)",
                    "lot_no": "string (LOT 번호)",
                    "issue": "string (이슈 설명)"
                }
            },
            "output_schema": {
                "qcost_classification": {
                    "lvl1": "string (PREVENTION/APPRAISAL/INTERNAL_FAILURE/EXTERNAL_FAILURE)",
                    "lvl2": "string (2단계 분류)",
                    "lvl3": "string (3단계 분류)",
                    "item_candidate": "string (후보 항목)",
                    "copq_flag": "boolean (COPQ 여부)"
                },
                "link_suggestions": {
                    "lot_no": "string",
                    "run_id": "integer",
                    "spc_event_id": "integer",
                    "capa_id": "integer"
                },
                "confidence": "float (0~1, 신뢰도)",
                "rationale": "array of strings (분류 근거)"
            }
        },

        "COPQ_REPORT": {
            "name": "COPQ 분석 리포트",
            "version": "1.0",
            "prompt_template": """# 입력 정보
- 집계 기간: {period}
- KPI: {kpis}
- 주요 불량: {top_defects}
- SPC 이슈: {spc_events}
- 진행 중 조치: {actions_open}

# 요구사항
1. 경영진단용 간결된 요약(executive_summary)을 작성하라
2. 주요 발견사항(key_findings)을 3~5개로 정리하라
3. TOP 원인(driver)별 영향도와 증거를 제시하라
4. 우선순위별 권장 사항(recommended_actions)을 작성하라
5. 리스크 관찰 목록(risk_watchlist)을 식별하라
6. 필요한 차트/그래프를 제안하라

# 출력 JSON 스키마
```json
{{
  "executive_summary": "2026년 1월 COPQ율 3.42%로 전월 대비 0.5%p 개선됨. 그러나 치수불량이 주요 원인으로 지속되어 개선이 시급함.",
  "key_findings": [
    "치수불량이 전체 COPQ의 29%를 차지하여 최대 문제",
    "SPC 추세(TREND)이 5건 감지되어 공정 이상 징후 후",
    "Cpk<1.33 항목이 3개로 공정능력 개선 필요"
  ],
  "drivers": [
    {{
      "name": "치수불량",
      "impact": "높음",
      "copq_contribution": "29%",
      "evidence": [
        "스크랩비 1,200만원",
        "SPC 추세 5건 (내경 Xbar-R)",
        "재세척 건수: 월 42건"
      ],
      "root_cause": "CNC 온도 변화, 공구 마모"
    }},
    {{
      "name": "스크래치",
      "impact": "중간",
      "copq_contribution": "20%",
      "evidence": ["재작업비 800만원", "재세척 건수: 월 61건"]
    }}
  ],
  "recommended_actions": [
    {{
      "priority": 1,
      "action": "CNC 온도/보정 표준화",
      "owner": "생산기술팀",
      "due": "2026-02-10",
      "expected_effect": "치수불량 20% 감소",
      "estimated_cost": "교육 500만원 + 자재화 200만원"
    }},
    {{
      "priority": 2,
      "action": "세척 공정 파라미터 최적화",
      "owner": "품질팀",
      "due": "2026-02-28",
      "expected_effect": "스크래치 30% 감소"
    }}
  ],
  "risk_watchlist": [
    {{
      "risk": "신규 제품 출시 예정",
      "impact": "불량률 증가 가능성",
      "mitigation": "사전 검사 계획 수립"
    }}
  ],
  "appendix": {{
    "charts_needed": [
      "Pareto Chart (불량 유형별)",
      "COPQ Trend (월별 추이)",
      "SPC Violations (관리도 위반 건수)",
      "Top 10 Defects"
    ],
    "data_sources": [
      "Q-COST Entry DB",
      "Inspection Result DB",
      "SPC Event DB",
      "CAPA Case DB"
    ]
  }}
}}
```
""",
            "input_schema": {
                "period": "string (YYYY-MM)",
                "kpis": {
                    "sales": "number (매출액)",
                    "total_qcost": "number (총 품질비용)",
                    "total_copq": "number (총 COPQ)",
                    "copq_rate": "number (COPQ율)"
                },
                "top_defects": [
                    {
                        "defect": "string (불량 유형)",
                        "count": "integer (발생 건수)",
                        "scrap_cost": "number (폐기 비용)"
                    }
                ],
                "spc_events": [
                    {
                        "chart": "string (관리도 이름)",
                        "type": "string (이벤트 타입)",
                        "count": "integer (발생 건수)"
                    }
                ],
                "actions_open": [
                    {
                        "capa_id": "string (CAPA ID)",
                        "status": "string (진행 상태)"
                    }
                ]
            },
            "output_schema": {
                "executive_summary": "string (경영진단 요약)",
                "key_findings": "array of strings (주요 발견)",
                "drivers": [
                    {
                        "name": "string (원인 명)",
                        "impact": "string (영향도: 높음/중간/낮음)",
                        "copq_contribution": "string (COPQ 기여율)",
                        "evidence": "array of strings (증거)",
                        "root_cause": "string (근본 원인)"
                    }
                ],
                "recommended_actions": [
                    {
                        "priority": "integer (우선순위 1~3)",
                        "action": "string (권장 사항)",
                        "owner": "string (담당자)",
                        "due": "string (목표일)",
                        "expected_effect": "string (기대 효과)",
                        "estimated_cost": "string (예상 비용)"
                    }
                ],
                "risk_watchlist": [
                    {
                        "risk": "string (리스크 명)",
                        "impact": "string (영향)",
                        "mitigation": "string "완화 조치)"
                    }
                ],
                "appendix": {
                    "charts_needed": "array of strings (필요한 차트)",
                    "data_sources": "array of strings (데이터 원천)"
                }
            }
        }
    }

    @classmethod
    def get_prompt(cls, use_case: str, language: str = "ko") -> dict:
        """Use Case별 프롬프트 반환"""
        if use_case not in cls.PROMPTS:
            raise ValueError(f"Unknown use case: {use_case}")

        prompt_info = cls.PROMPTS[use_case]
        return {
            "use_case": use_case,
            "prompt_template": prompt_info["prompt_template"],
            "version": prompt_info["version"],
            "input_schema": prompt_info["input_schema"],
            "output_schema": prompt_info["output_schema"],
            "language": language
        }

    @classmethod
    def format_prompt(cls, use_case: str, inputs: dict) -> str:
        """입력 데이터를 프롬프트에 적용"""
        prompt_info = cls.get_prompt(use_case)
        template = prompt_info["prompt_template"]

        # 프롬프트에 입력 데이터 적용
        formatted = template.format(**inputs)

        # JSON 스키마 추가
        formatted += f"\n\n# Expected Output Schema:\n```json\n{prompt_info['output_schema']}\n```"

        return formatted
