"""
Run Rule AI Prediction Service
Western Electric Rules 기반 SPC AI 예측
"""
import numpy as np
from typing import List, Dict, Any
from apps.spc.models import Product

class RunRulePredictor:
    """Western Electric Run Rules 기반 AI 예측기"""

    def __init__(self):
        """초기화"""
        self.rules = [
            {
                'id': 'RULE_1',
                'name': '3σ 벗어남',
                'description': '1개 점이 UCL 또는 LCL을 벗어남',
                'severity': 'CRITICAL'
            },
            {
                'id': 'RULE_2',
                'name': '9개 연속 동일측',
                'description': '9개 연속 점이 중심선의 같은 쪽에 있음',
                'severity': 'HIGH'
            },
            {
                'id': 'RULE_3',
                'name': '6개 연속 증가/감소',
                'description': '6개 연속 점이 지속적으로 증가하거나 감소함',
                'severity': 'HIGH'
            },
            {
                'id': 'RULE_4',
                'name': '14개 교차 패턴',
                'description': '14개 연속 점이 상하로 교차함',
                'severity': 'MEDIUM'
            },
            {
                'id': 'RULE_5',
                'name': '4개 중 3개가 2σ 벗어남',
                'description': '연속 5개 점 중 3개가 2σ 영역 밖에 있음',
                'severity': 'MEDIUM'
            },
            {
                'id': 'RULE_6',
                'name': '6개 중 5개가 1σ 벗어남',
                'description': '연속 6개 점 중 5개가 1σ 영역 밖에 있음',
                'severity': 'LOW'
            },
        ]

    def predict_violations(self, product: Product, measurements: List[float]) -> List[Dict[str, Any]]:
        """
        AI 기반 Run Rule 위반 예측

        Args:
            product: 제품 정보
            measurements: 측정값 리스트

        Returns:
            예측 결과 리스트
        """
        if not measurements or len(measurements) < 6:
            return []

        # 통계량 계산
        values = np.array(measurements)
        mean = np.mean(values)
        std = np.std(values) if len(values) > 1 else 0.1

        # 제품 규격 정보 사용
        usl = product.usl if product.usl else mean + 3 * std
        lsl = product.lsl if product.lsl else mean - 3 * std
        target = product.target_value if product.target_value else mean

        # 관리한계 계산
        ucl = target + 3 * std
        lcl = target - 3 * std

        # 규칙별 위반 검사
        violations = []

        # Rule 1: 3σ 벗어남
        rule1_violations = self._check_rule_1(values, ucl, lcl)
        violations.extend(rule1_violations)

        # Rule 2: 9개 연속 동일측
        rule2_violations = self._check_rule_2(values, target)
        violations.extend(rule2_violations)

        # Rule 3: 6개 연속 증가/감소
        rule3_violations = self._check_rule_3(values)
        violations.extend(rule3_violations)

        # Rule 4: 14개 교차 패턴
        rule4_violations = self._check_rule_4(values)
        violations.extend(rule4_violations)

        # Rule 5: 4개 중 3개가 2σ 벗어남
        rule5_violations = self._check_rule_5(values, target, std)
        violations.extend(rule5_violations)

        # Rule 6: 6개 중 5개가 1σ 벗어남
        rule6_violations = self._check_rule_6(values, target, std)
        violations.extend(rule6_violations)

        # AI 예측 추가 정보 생성
        for violation in violations:
            violation.update({
                'ai_confidence': self._calculate_confidence(violation),
                'ai_recommendation': self._generate_recommendation(violation),
                'predicted_impact': self._assess_impact(violation),
                'suggested_actions': self._suggest_actions(violation)
            })

        return violations

    def _check_rule_1(self, values: np.ndarray, ucl: float, lcl: float) -> List[Dict]:
        """Rule 1: 점이 3σ 벗어남"""
        violations = []
        for i, val in enumerate(values):
            if val > ucl or val < lcl:
                violations.append({
                    'rule_id': 'RULE_1',
                    'rule_name': '3σ 벗어남',
                    'description': f'측정값 {val:.3f}이(가) 관리한계({lcl:.3f} ~ {ucl:.3f})를 벗어남',
                    'is_violation': True,
                    'severity': 'CRITICAL',
                    'measurement_index': i,
                    'measurement_value': float(val),
                    'ucl': float(ucl),
                    'lcl': float(lcl)
                })
        return violations

    def _check_rule_2(self, values: np.ndarray, center: float) -> List[Dict]:
        """Rule 2: 9개 연속 동일측"""
        violations = []
        if len(values) < 9:
            return violations

        for i in range(len(values) - 8):
            subset = values[i:i+9]
            if all(v > center for v in subset):
                violations.append({
                    'rule_id': 'RULE_2',
                    'rule_name': '9개 연속 동일측',
                    'description': f'{i+1}~{i+9}번 측정값이 중심선 상측에 위치',
                    'is_violation': True,
                    'severity': 'HIGH',
                    'start_index': i,
                    'end_index': i+8,
                    'side': 'above'
                })
            elif all(v < center for v in subset):
                violations.append({
                    'rule_id': 'RULE_2',
                    'rule_name': '9개 연속 동일측',
                    'description': f'{i+1}~{i+9}번 측정값이 중심선 하측에 위치',
                    'is_violation': True,
                    'severity': 'HIGH',
                    'start_index': i,
                    'end_index': i+8,
                    'side': 'below'
                })
        return violations

    def _check_rule_3(self, values: np.ndarray) -> List[Dict]:
        """Rule 3: 6개 연속 증가/감소"""
        violations = []
        if len(values) < 6:
            return violations

        for i in range(len(values) - 5):
            subset = values[i:i+6]
            increasing = all(subset[j] < subset[j+1] for j in range(5))
            decreasing = all(subset[j] > subset[j+1] for j in range(5))

            if increasing or decreasing:
                trend = "증가" if increasing else "감소"
                violations.append({
                    'rule_id': 'RULE_3',
                    'rule_name': '6개 연속 증가/감소',
                    'description': f'{i+1}~{i+6}번 측정값이 지속적으로 {trend}',
                    'is_violation': True,
                    'severity': 'HIGH',
                    'start_index': i,
                    'end_index': i+5,
                    'trend': trend.lower()
                })
        return violations

    def _check_rule_4(self, values: np.ndarray) -> List[Dict]:
        """Rule 4: 14개 교차 패턴"""
        violations = []
        if len(values) < 14:
            return violations

        for i in range(len(values) - 13):
            subset = values[i:i+14]
            # 상하 교차 패턴 확인
            alternations = 0
            for j in range(13):
                if (subset[j] - subset[j+1]) * (subset[j+1] - subset[j+2]) < 0:
                    alternations += 1

            if alternations >= 10:  # 대부분 교차
                violations.append({
                    'rule_id': 'RULE_4',
                    'rule_name': '14개 교차 패턴',
                    'description': f'{i+1}~{i+14}번 측정값이 상하 교차 패턴',
                    'is_violation': True,
                    'severity': 'MEDIUM',
                    'start_index': i,
                    'end_index': i+13,
                    'alternations': alternations
                })
        return violations

    def _check_rule_5(self, values: np.ndarray, center: float, std: float) -> List[Dict]:
        """Rule 5: 4개 중 3개가 2σ 벗어남"""
        violations = []
        if len(values) < 5:
            return violations

        sigma_2 = 2 * std
        for i in range(len(values) - 4):
            subset = values[i:i+5]
            beyond_2sigma = sum(1 for v in subset if abs(v - center) > sigma_2)

            if beyond_2sigma >= 3:
                violations.append({
                    'rule_id': 'RULE_5',
                    'rule_name': '4개 중 3개가 2σ 벗어남',
                    'description': f'{i+1}~{i+5}번 중 {beyond_2sigma}개가 2σ 영역 밖',
                    'is_violation': True,
                    'severity': 'MEDIUM',
                    'start_index': i,
                    'end_index': i+4,
                    'beyond_count': beyond_2sigma
                })
        return violations

    def _check_rule_6(self, values: np.ndarray, center: float, std: float) -> List[Dict]:
        """Rule 6: 6개 중 5개가 1σ 벗어남"""
        violations = []
        if len(values) < 6:
            return violations

        sigma_1 = std
        for i in range(len(values) - 5):
            subset = values[i:i+6]
            beyond_1sigma = sum(1 for v in subset if abs(v - center) > sigma_1)

            if beyond_1sigma >= 5:
                violations.append({
                    'rule_id': 'RULE_6',
                    'rule_name': '6개 중 5개가 1σ 벗어남',
                    'description': f'{i+1}~{i+6}번 중 {beyond_1sigma}개가 1σ 영역 밖',
                    'is_violation': True,
                    'severity': 'LOW',
                    'start_index': i,
                    'end_index': i+5,
                    'beyond_count': beyond_1sigma
                })
        return violations

    def _calculate_confidence(self, violation: Dict) -> float:
        """AI 예측 신뢰도 계산"""
        base_confidence = 0.85

        # 규칙별 신뢰도 조정
        severity_multiplier = {
            'CRITICAL': 1.0,
            'HIGH': 0.9,
            'MEDIUM': 0.8,
            'LOW': 0.7
        }

        rule_confidence = {
            'RULE_1': 0.95,
            'RULE_2': 0.88,
            'RULE_3': 0.85,
            'RULE_4': 0.75,
            'RULE_5': 0.78,
            'RULE_6': 0.70
        }

        confidence = base_confidence * severity_multiplier.get(violation['severity'], 0.8)
        confidence = confidence * rule_confidence.get(violation['rule_id'], 0.8)

        return min(confidence, 0.99)

    def _generate_recommendation(self, violation: Dict) -> str:
        """AI 추천 사항 생성"""
        recommendations = {
            'RULE_1': '⚠️ 즉시 공정 중단 및 원인 분석 필요. 규격 이탈은 심각한 품질 문제입니다.',
            'RULE_2': '📈 공정 평균이 이동하고 있습니다. 공정 조정이 필요합니다.',
            'RULE_3': '📊 공정에 트렌드가 있습니다. 원인을 파악하고 교정 조치를 취하세요.',
            'RULE_4': '🔄 측정 시스템의 교정이 필요할 수 있습니다.',
            'RULE_5': '⚠️ 공정 산포가 증가하고 있습니다. 변이 원인을 조사하세요.',
            'RULE_6': 'ℹ️ 공정 이탈 징후가 있습니다. 주의 깊게 모니터링하세요.'
        }

        return recommendations.get(violation['rule_id'], '추가 분석이 필요합니다.')

    def _assess_impact(self, violation: Dict) -> str:
        """영향도 평가"""
        impact_map = {
            'CRITICAL': '높음 - 즉시 조치 필요. 불량품 발생 우려.',
            'HIGH': '중간 - 조기 조치 권장. 공정 불안정.',
            'MEDIUM': '보통 - 모니터링 강화. 추이 확인.',
            'LOW': '낮음 - 주시 관찰. 정기 점검.'
        }
        return impact_map.get(violation['severity'], '평가 필요')

    def _suggest_actions(self, violation: Dict) -> List[str]:
        """제안 action 목록"""
        actions = {
            'RULE_1': [
                '공정 중단',
                '원인 분석 (5M1E)',
                '즉시 재교정',
                '영향받은 제품 전수 검사'
            ],
            'RULE_2': [
                '공정 평균 조정',
                '설비 파라미터 확인',
                '원재료 품질 확인',
                '환경 요인 점검'
            ],
            'RULE_3': [
                '트렌드 원인 파악',
                '공정 안정화',
                '예방 조치',
                '지속 모니터링'
            ],
            'RULE_4': [
                '측정 시스템 점검',
                '계측기 교정',
                '측정자 교육',
                '시스템 재검증'
            ],
            'RULE_5': [
                '변이 원인 분석',
                '공정 최적화',
                '환경 통제 강화',
                '정기 검사 주기 단축'
            ],
            'RULE_6': [
                '모니터링 강화',
                'SPC 차트 작성',
                '경향 분석',
                '사전 예방 조치'
            ]
        }

        return actions.get(violation['rule_id'], ['추가 분석 필요'])
