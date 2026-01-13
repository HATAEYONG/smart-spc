"""
AI Prompt System Test Script
프롬프트 시스템 기능 테스트
"""
import sys
import os

# Django setup
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.spc.services.ai_prompt_service import AIPromptService

def test_format_prompt():
    """프롬프트 포맷팅 테스트"""
    print("\n=== Test 1: Format Prompt (PROCESS_DESIGN) ===")

    inputs = {
        'company': {'industry': '자동차부품', 'site': '경기공장'},
        'product': {'item_name': '브레이크 패드', 'process': 'CNC+세척+조립'},
        'constraints': {'inspection_headcount': 3, 'shift': 2},
        'known_defects': ['치수불량', '스크래치'],
        'customer_requirements': ['IATF 16949 준수', '불량률 100ppm 이하']
    }

    try:
        result = AIPromptService.get_formatted_prompt('PROCESS_DESIGN', inputs, 'ko')
        print(f"✓ Use Case: {result['use_case']}")
        print(f"✓ Version: {result['version']}")
        print(f"✓ Prompt Name: {result['prompt_name']}")
        print(f"✓ Formatted Prompt Length: {len(result['formatted_prompt'])} characters")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_execute_prompt():
    """AI 실행 테스트 (모의 출력)"""
    print("\n=== Test 2: Execute Prompt (CRITERIA_CHECKLIST) ===")

    inputs = {
        'item': '브레이크 패드',
        'step': '최종검사',
        'inspection_type': 'DIM',
        'defect_modes': ['찍힘', '스크래치', '이물'],
        'acceptance_policy': {
            'A': '출하가능',
            'B': '재작업',
            'C': '폐기'
        },
        'language': 'ko'
    }

    try:
        result = AIPromptService.execute_prompt(
            use_case='CRITERIA_CHECKLIST',
            inputs=inputs,
            site_id=1,
            user_id=1,
            language='ko',
            model_name='gpt-4'
        )

        print(f"✓ Use Case: {result['use_case']}")
        print(f"✓ AI Output ID: {result['ai_output_id']}")
        print(f"✓ Confidence: {result['confidence']:.2f}")
        print(f"✓ Model: {result['model_name']}")
        print(f"✓ Cached: {result.get('cached', False)}")

        # Check output structure
        output = result['output_json']
        if 'criteria_table' in output and 'checklist' in output:
            print(f"✓ Output contains criteria_table and checklist")
            print(f"  - Criteria items: {len(output['criteria_table'])}")
            print(f"  - Checklist items: {len(output['checklist'])}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_qcost_classify():
    """Q-COST 분류 테스트"""
    print("\n=== Test 3: Q-COST Classify ===")

    inputs = {
        'text': '세척 불량으로 인한 재세척 비용 발생 (인건비 50만원)',
        'amount': 500000,
        'context': {
            'dept': '생산팀',
            'lot_no': 'L-2026-0112',
            'issue': '세척 불량'
        }
    }

    try:
        result = AIPromptService.execute_prompt(
            use_case='QCOST_CLASSIFY',
            inputs=inputs,
            site_id=1,
            user_id=1,
            language='ko',
            model_name='gpt-4'
        )

        print(f"✓ Use Case: {result['use_case']}")
        print(f"✓ AI Output ID: {result['ai_output_id']}")

        output = result['output_json']
        classification = output.get('qcost_classification', {})
        print(f"✓ Classification: {classification.get('lvl1')} / {classification.get('lvl2')}")
        print(f"✓ COPQ Flag: {classification.get('copq_flag')}")
        print(f"✓ Confidence: {result['confidence']:.2f}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_copq_report():
    """COPQ 리포트 테스트"""
    print("\n=== Test 4: COPQ Report ===")

    inputs = {
        'period': '2026-01',
        'kpis': {
            'sales': 500000000,
            'total_qcost': 15000000,
            'total_copq': 12000000,
            'copq_rate': 2.4
        },
        'top_defects': [
            {'defect': '치수불량', 'count': 45, 'scrap_cost': 5000000},
            {'defect': '스크래치', 'count': 32, 'scrap_cost': 3000000},
            {'defect': '이물', 'count': 28, 'scrap_cost': 2000000}
        ],
        'spc_events': [
            {'chart': '내경 Xbar-R', 'type': 'TREND', 'count': 5},
            {'chart': '외관 p-chart', 'type': 'OOS', 'count': 2}
        ],
        'actions_open': [
            {'capa_id': 'CAPA-001', 'status': 'IN_PROGRESS'},
            {'capa_id': 'CAPA-002', 'status': 'OPEN'}
        ]
    }

    try:
        result = AIPromptService.execute_prompt(
            use_case='COPQ_REPORT',
            inputs=inputs,
            site_id=1,
            user_id=1,
            language='ko',
            model_name='gpt-4'
        )

        print(f"✓ Use Case: {result['use_case']}")
        print(f"✓ AI Output ID: {result['ai_output_id']}")

        output = result['output_json']
        print(f"✓ Executive Summary: {output.get('executive_summary', '')[:100]}...")
        print(f"✓ Key Findings: {len(output.get('key_findings', []))} items")
        print(f"✓ Drivers: {len(output.get('drivers', []))} items")
        print(f"✓ Recommended Actions: {len(output.get('recommended_actions', []))} items")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_use_cases():
    """Use Case 목록 조회 테스트"""
    print("\n=== Test 5: Get Available Use Cases ===")

    try:
        use_cases = AIPromptService.get_available_use_cases()

        print(f"✓ Total Use Cases: {len(use_cases)}")
        for uc in use_cases:
            print(f"  - {uc['use_case']}: {uc['name']}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_list_outputs():
    """AI 출력 목록 조회 테스트"""
    print("\n=== Test 6: List AI Outputs ===")

    try:
        outputs = AIPromptService.list_ai_outputs(site_id=1, limit=10)

        print(f"✓ Total Outputs: {len(outputs)}")
        for output in outputs[:3]:
            print(f"  - ID {output['ai_output_id']}: {output['use_case']} ({output['model_name']})")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """모든 테스트 실행"""
    print("\n" + "="*60)
    print("AI Prompt System Test Suite")
    print("="*60)

    tests = [
        test_get_use_cases,
        test_format_prompt,
        test_execute_prompt,
        test_qcost_classify,
        test_copq_report,
        test_list_outputs,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append(False)

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")

    if passed == total:
        print("\n✓ All tests passed!")
    else:
        print(f"\n✗ {total - passed} test(s) failed")

    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
