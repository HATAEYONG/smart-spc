"""
Run Rule 검증 로직
Western Electric Rules (8가지 규칙) 구현
"""
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class RuleType(Enum):
    """Run Rule 타입"""
    RULE_1 = "RULE_1"  # 관리 한계 벗어남
    RULE_2 = "RULE_2"  # 9개 연속 중심선 한쪽
    RULE_3 = "RULE_3"  # 6개 연속 증가/감소
    RULE_4 = "RULE_4"  # 14개 연속 교대 상승/하강
    RULE_5 = "RULE_5"  # 3개 중 2개가 2σ 벗어남
    RULE_6 = "RULE_6"  # 5개 중 4개가 1σ 벗어남
    RULE_7 = "RULE_7"  # 15개 연속 1σ 이내
    RULE_8 = "RULE_8"  # 8개 연속 1σ 벗어남


@dataclass
class RuleViolation:
    """Run Rule 위반 정보"""
    rule_type: RuleType
    index: int  # 위반이 감지된 인덱스
    description: str
    severity: int  # 1=낮음, 2=보통, 3=높음, 4=긴급
    violation_indices: List[int]  # 위반에 관련된 모든 인덱스
    violation_values: List[float]  # 위반에 관련된 값들


class RunRuleChecker:
    """Run Rule 검증기"""

    def __init__(self, ucl: float, cl: float, lcl: float):
        """
        Args:
            ucl: Upper Control Limit
            cl: Center Line
            lcl: Lower Control Limit
        """
        self.ucl = ucl
        self.cl = cl
        self.lcl = lcl

        # 시그마 구간 계산 (3σ 가정)
        self.sigma = (ucl - cl) / 3
        self.sigma_1 = self.sigma
        self.sigma_2 = 2 * self.sigma

    def check_all_rules(self, data: List[float]) -> List[RuleViolation]:
        """
        모든 Run Rule 검증

        Args:
            data: 관리도 데이터 (X-bar, R, p 등)

        Returns:
            위반 목록
        """
        violations = []

        violations.extend(self.check_rule_1(data))
        violations.extend(self.check_rule_2(data))
        violations.extend(self.check_rule_3(data))
        violations.extend(self.check_rule_4(data))
        violations.extend(self.check_rule_5(data))
        violations.extend(self.check_rule_6(data))
        violations.extend(self.check_rule_7(data))
        violations.extend(self.check_rule_8(data))

        return violations

    def check_rule_1(self, data: List[float]) -> List[RuleViolation]:
        """
        Rule 1: 1개 점이 관리 한계 (UCL 또는 LCL)를 벗어남

        심각도: 긴급 (4)
        """
        violations = []

        for i, value in enumerate(data):
            if value > self.ucl:
                violations.append(RuleViolation(
                    rule_type=RuleType.RULE_1,
                    index=i,
                    description=f"점이 상한 관리 한계(UCL={self.ucl:.3f})를 벗어남: {value:.3f}",
                    severity=4,
                    violation_indices=[i],
                    violation_values=[value]
                ))
            elif value < self.lcl:
                violations.append(RuleViolation(
                    rule_type=RuleType.RULE_1,
                    index=i,
                    description=f"점이 하한 관리 한계(LCL={self.lcl:.3f})를 벗어남: {value:.3f}",
                    severity=4,
                    violation_indices=[i],
                    violation_values=[value]
                ))

        return violations

    def check_rule_2(self, data: List[float]) -> List[RuleViolation]:
        """
        Rule 2: 9개 연속 점이 중심선 한쪽에 위치

        심각도: 높음 (3)
        """
        violations = []

        if len(data) < 9:
            return violations

        for i in range(len(data) - 8):
            window = data[i:i+9]

            if all(x > self.cl for x in window):
                violations.append(RuleViolation(
                    rule_type=RuleType.RULE_2,
                    index=i+8,
                    description=f"9개 연속 점이 중심선({self.cl:.3f}) 위에 위치",
                    severity=3,
                    violation_indices=list(range(i, i+9)),
                    violation_values=window
                ))
            elif all(x < self.cl for x in window):
                violations.append(RuleViolation(
                    rule_type=RuleType.RULE_2,
                    index=i+8,
                    description=f"9개 연속 점이 중심선({self.cl:.3f}) 아래에 위치",
                    severity=3,
                    violation_indices=list(range(i, i+9)),
                    violation_values=window
                ))

        return violations

    def check_rule_3(self, data: List[float]) -> List[RuleViolation]:
        """
        Rule 3: 6개 연속 점이 계속 증가하거나 감소

        심각도: 높음 (3)
        """
        violations = []

        if len(data) < 6:
            return violations

        for i in range(len(data) - 5):
            window = data[i:i+6]

            # 연속 증가 체크
            if all(window[j] < window[j+1] for j in range(5)):
                violations.append(RuleViolation(
                    rule_type=RuleType.RULE_3,
                    index=i+5,
                    description="6개 연속 점이 계속 증가하는 추세",
                    severity=3,
                    violation_indices=list(range(i, i+6)),
                    violation_values=window
                ))

            # 연속 감소 체크
            elif all(window[j] > window[j+1] for j in range(5)):
                violations.append(RuleViolation(
                    rule_type=RuleType.RULE_3,
                    index=i+5,
                    description="6개 연속 점이 계속 감소하는 추세",
                    severity=3,
                    violation_indices=list(range(i, i+6)),
                    violation_values=window
                ))

        return violations

    def check_rule_4(self, data: List[float]) -> List[RuleViolation]:
        """
        Rule 4: 14개 연속 점이 교대로 상승과 하강

        심각도: 보통 (2)
        """
        violations = []

        if len(data) < 14:
            return violations

        for i in range(len(data) - 13):
            window = data[i:i+14]

            # 교대 패턴 체크 (상승-하강-상승-...)
            is_alternating = True
            for j in range(12):
                if j % 2 == 0:  # 짝수 인덱스: 상승
                    if window[j] >= window[j+1]:
                        is_alternating = False
                        break
                else:  # 홀수 인덱스: 하강
                    if window[j] <= window[j+1]:
                        is_alternating = False
                        break

            if is_alternating:
                violations.append(RuleViolation(
                    rule_type=RuleType.RULE_4,
                    index=i+13,
                    description="14개 연속 점이 교대로 상승/하강",
                    severity=2,
                    violation_indices=list(range(i, i+14)),
                    violation_values=window
                ))

        return violations

    def check_rule_5(self, data: List[float]) -> List[RuleViolation]:
        """
        Rule 5: 3개 중 2개 점이 2σ를 벗어남 (같은 쪽)

        심각도: 높음 (3)
        """
        violations = []

        if len(data) < 3:
            return violations

        upper_2sigma = self.cl + self.sigma_2
        lower_2sigma = self.cl - self.sigma_2

        for i in range(len(data) - 2):
            window = data[i:i+3]

            # 상한 2σ 벗어남 체크
            above_2sigma = [x > upper_2sigma for x in window]
            if sum(above_2sigma) >= 2:
                violation_idx = [i+j for j, flag in enumerate(above_2sigma) if flag]
                violations.append(RuleViolation(
                    rule_type=RuleType.RULE_5,
                    index=i+2,
                    description=f"3개 중 2개 점이 상한 2σ({upper_2sigma:.3f})를 벗어남",
                    severity=3,
                    violation_indices=violation_idx,
                    violation_values=[window[j] for j, flag in enumerate(above_2sigma) if flag]
                ))

            # 하한 2σ 벗어남 체크
            below_2sigma = [x < lower_2sigma for x in window]
            if sum(below_2sigma) >= 2:
                violation_idx = [i+j for j, flag in enumerate(below_2sigma) if flag]
                violations.append(RuleViolation(
                    rule_type=RuleType.RULE_5,
                    index=i+2,
                    description=f"3개 중 2개 점이 하한 2σ({lower_2sigma:.3f})를 벗어남",
                    severity=3,
                    violation_indices=violation_idx,
                    violation_values=[window[j] for j, flag in enumerate(below_2sigma) if flag]
                ))

        return violations

    def check_rule_6(self, data: List[float]) -> List[RuleViolation]:
        """
        Rule 6: 5개 중 4개 점이 1σ를 벗어남 (같은 쪽)

        심각도: 보통 (2)
        """
        violations = []

        if len(data) < 5:
            return violations

        upper_1sigma = self.cl + self.sigma_1
        lower_1sigma = self.cl - self.sigma_1

        for i in range(len(data) - 4):
            window = data[i:i+5]

            # 상한 1σ 벗어남 체크
            above_1sigma = [x > upper_1sigma for x in window]
            if sum(above_1sigma) >= 4:
                violation_idx = [i+j for j, flag in enumerate(above_1sigma) if flag]
                violations.append(RuleViolation(
                    rule_type=RuleType.RULE_6,
                    index=i+4,
                    description=f"5개 중 4개 점이 상한 1σ({upper_1sigma:.3f})를 벗어남",
                    severity=2,
                    violation_indices=violation_idx,
                    violation_values=[window[j] for j, flag in enumerate(above_1sigma) if flag]
                ))

            # 하한 1σ 벗어남 체크
            below_1sigma = [x < lower_1sigma for x in window]
            if sum(below_1sigma) >= 4:
                violation_idx = [i+j for j, flag in enumerate(below_1sigma) if flag]
                violations.append(RuleViolation(
                    rule_type=RuleType.RULE_6,
                    index=i+4,
                    description=f"5개 중 4개 점이 하한 1σ({lower_1sigma:.3f})를 벗어남",
                    severity=2,
                    violation_indices=violation_idx,
                    violation_values=[window[j] for j, flag in enumerate(below_1sigma) if flag]
                ))

        return violations

    def check_rule_7(self, data: List[float]) -> List[RuleViolation]:
        """
        Rule 7: 15개 연속 점이 1σ 이내 (과소 변동)

        심각도: 낮음 (1)
        """
        violations = []

        if len(data) < 15:
            return violations

        upper_1sigma = self.cl + self.sigma_1
        lower_1sigma = self.cl - self.sigma_1

        for i in range(len(data) - 14):
            window = data[i:i+15]

            if all(lower_1sigma < x < upper_1sigma for x in window):
                violations.append(RuleViolation(
                    rule_type=RuleType.RULE_7,
                    index=i+14,
                    description=f"15개 연속 점이 1σ({lower_1sigma:.3f} ~ {upper_1sigma:.3f}) 이내 (과소 변동)",
                    severity=1,
                    violation_indices=list(range(i, i+15)),
                    violation_values=window
                ))

        return violations

    def check_rule_8(self, data: List[float]) -> List[RuleViolation]:
        """
        Rule 8: 8개 연속 점이 1σ 벗어남 (양쪽 모두)

        심각도: 보통 (2)
        """
        violations = []

        if len(data) < 8:
            return violations

        upper_1sigma = self.cl + self.sigma_1
        lower_1sigma = self.cl - self.sigma_1

        for i in range(len(data) - 7):
            window = data[i:i+8]

            if all(x > upper_1sigma or x < lower_1sigma for x in window):
                violations.append(RuleViolation(
                    rule_type=RuleType.RULE_8,
                    index=i+7,
                    description=f"8개 연속 점이 1σ를 벗어남 (과대 변동)",
                    severity=2,
                    violation_indices=list(range(i, i+8)),
                    violation_values=window
                ))

        return violations

    def visualize_violations(self, data: List[float], violations: List[RuleViolation]) -> Dict:
        """
        위반 정보를 시각화 데이터로 변환

        Returns:
            {
                'data': [...],
                'violations': [{'index': i, 'rule': 'RULE_1', 'severity': 4}, ...],
                'limits': {'ucl': ..., 'cl': ..., 'lcl': ...},
                'sigma_lines': {'1sigma_upper': ..., '1sigma_lower': ..., ...}
            }
        """
        result = {
            'data': data,
            'violations': [
                {
                    'index': v.index,
                    'rule': v.rule_type.value,
                    'description': v.description,
                    'severity': v.severity,
                    'violation_indices': v.violation_indices,
                    'violation_values': v.violation_values
                }
                for v in violations
            ],
            'limits': {
                'ucl': self.ucl,
                'cl': self.cl,
                'lcl': self.lcl
            },
            'sigma_lines': {
                '1sigma_upper': self.cl + self.sigma_1,
                '1sigma_lower': self.cl - self.sigma_1,
                '2sigma_upper': self.cl + self.sigma_2,
                '2sigma_lower': self.cl - self.sigma_2
            }
        }

        return result


# 사용 예시
if __name__ == '__main__':
    # 예제 데이터 (의도적으로 위반 포함)
    ucl, cl, lcl = 10.5, 10.0, 9.5

    # Rule 1 위반 (관리 한계 벗어남)
    data = [10.0, 10.1, 10.2, 10.6, 10.1, 10.0, 9.9, 10.0, 10.1]

    checker = RunRuleChecker(ucl, cl, lcl)
    violations = checker.check_all_rules(data)

    print(f"총 {len(violations)}개의 위반 발견:")
    for v in violations:
        print(f"- {v.rule_type.value}: {v.description} (심각도: {v.severity})")
