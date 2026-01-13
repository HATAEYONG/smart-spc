"""
고급 관리도 계산 서비스
CUSUM (Cumulative Sum) Control Chart
EWMA (Exponentially Weighted Moving Average) Control Chart
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime


class CUSUMChart:
    """
    CUSUM (Cumulative Sum) 관리도
    작은 변동을 감지하는 데 효과적인 관리도
    """

    def __init__(self, target_value: float, std_dev: float, k: float = 0.5, h: float = 5.0):
        """
        CUSUM 관리도 초기화

        Args:
            target_value: 목표값 (μ0)
            std_dev: 표준편차 (σ)
            k: 참조값 (일반적으로 0.5, 반사계수 K = kσ)
            h: 결정한계 (일반적으로 5, H = hσ)
        """
        self.target_value = target_value
        self.std_dev = std_dev
        self.k = k  # 참조값
        self.h = h  # 결정한계

    def calculate(self, measurements: List[float]) -> Dict[str, any]:
        """
        CUSUM 계산

        Returns:
            Dictionary with CUSUM statistics and control limits
        """
        if len(measurements) < 2:
            raise ValueError("CUSUM 계산에는 최소 2개 이상의 데이터가 필요합니다")

        # CUSUM 계산
        ci_positive = [0.0]  # 상방 CUSUM (C+)
        ci_negative = [0.0]  # 하방 CUSUM (C-)

        for i, x in enumerate(measurements):
            if i == 0:
                ci_positive.append(0)
                ci_negative.append(0)
                continue

            # 상방 CUSUM: 목표값보다 큰 편차 누적
            ci_plus = max(0, ci_positive[-1] + (x - self.target_value) / self.std_dev - self.k)

            # 하방 CUSUM: 목표값보다 작은 편차 누적
            ci_minus = max(0, ci_negative[-1] - (x - self.target_value) / self.std_dev - self.k)

            ci_positive.append(ci_plus)
            ci_negative.append(ci_minus)

        # 관리 한계선
        ucl = self.h * self.std_dev  # 상한 (H)
        lcl = -self.h * self.std_dev  # 하한 (-H)

        # 위반 지점 감지
        positive_violations = []
        negative_violations = []

        for i, (cp, cn) in enumerate(zip(ci_positive[1:], ci_negative[1:]), 1):
            if cp > self.h:
                positive_violations.append({
                    'index': i,
                    'value': cp,
                    'measurement': measurements[i-1] if i <= len(measurements) else None
                })
            if cn > self.h:
                negative_violations.append({
                    'index': i,
                    'value': cn,
                    'measurement': measurements[i-1] if i <= len(measurements) else None
                })

        return {
            'chart_type': 'CUSUM',
            'target_value': self.target_value,
            'std_dev': self.std_dev,
            'k': self.k,
            'h': self.h,
            'ucl': ucl,
            'lcl': lcl,
            'ci_positive': ci_positive[1:],  # 초기값 제외
            'ci_negative': ci_negative[1:],  # 초기값 제외
            'positive_violations': positive_violations,
            'negative_violations': negative_violations,
            'total_violations': len(positive_violations) + len(negative_violations)
        }


class EWMAChart:
    """
    EWMA (Exponentially Weighted Moving Average) 관리도
    최근 데이터에 더 많은 가중치를 부여하는 관리도
    """

    def __init__(self, target_value: float, std_dev: float, lambda_param: float = 0.2, l: float = 3.0):
        """
        EWMA 관리도 초기화

        Args:
            target_value: 목표값 (μ0)
            std_dev: 표준편차 (σ)
            lambda_param: 스무딩 파라미터 λ (0 < λ ≤ 1, 일반적으로 0.2)
            l: 관리한계 계수 (일반적으로 3)
        """
        self.target_value = target_value
        self.std_dev = std_dev
        self.lambda_param = lambda_param
        self.l = l

    def calculate(self, measurements: List[float]) -> Dict[str, any]:
        """
        EWMA 계산

        Returns:
            Dictionary with EWMA statistics and control limits
        """
        if len(measurements) < 2:
            raise ValueError("EWMA 계산에는 최소 2개 이상의 데이터가 필요합니다")

        # EWMA 계산: Z_i = λX_i + (1-λ)Z_{i-1}
        ewma_values = []
        zi = self.target_value  # 초기값 Z_0 = μ0

        for i, x in enumerate(measurements):
            zi = self.lambda_param * x + (1 - self.lambda_param) * zi
            ewma_values.append(zi)

        # 관리 한계선 계산
        # σ_Zi = σ * sqrt(λ(2-λ) * (1 - (1-λ)^{2i})) / (2-λ)
        # 안정 상태에서: σ_Z = σ * sqrt(λ / (2-λ))
        sigma_ewma = self.std_dev * np.sqrt(self.lambda_param / (2 - self.lambda_param))

        ucl = self.target_value + self.l * sigma_ewma
        lcl = self.target_value - self.l * sigma_ewma

        # 위반 지점 감지
        violations = []
        for i, (zi_val, measurement) in enumerate(zip(ewma_values, measurements)):
            if zi_val > ucl or zi_val < lcl:
                violations.append({
                    'index': i,
                    'ewma_value': zi_val,
                    'measurement': measurement,
                    'violation_type': 'above' if zi_val > ucl else 'below'
                })

        return {
            'chart_type': 'EWMA',
            'target_value': self.target_value,
            'std_dev': self.std_dev,
            'lambda': self.lambda_param,
            'l': self.l,
            'ucl': ucl,
            'lcl': lcl,
            'cl': self.target_value,
            'ewma_values': ewma_values,
            'sigma_ewma': sigma_ewma,
            'violations': violations,
            'total_violations': len(violations)
        }


class AdvancedControlChartService:
    """고급 관리도 서비스"""

    @staticmethod
    def calculate_cusum(
        measurements: List[float],
        target_value: float,
        std_dev: float,
        k: float = 0.5,
        h: float = 5.0
    ) -> Dict[str, any]:
        """
        CUSUM 관리도 계산

        Args:
            measurements: 측정값 리스트
            target_value: 목표값
            std_dev: 표준편차
            k: 참조값 (기본값 0.5)
            h: 결정한계 (기본값 5.0)
        """
        cusum = CUSUMChart(target_value, std_dev, k, h)
        return cusum.calculate(measurements)

    @staticmethod
    def calculate_ewma(
        measurements: List[float],
        target_value: float,
        std_dev: float,
        lambda_param: float = 0.2,
        l: float = 3.0
    ) -> Dict[str, any]:
        """
        EWMA 관리도 계산

        Args:
            measurements: 측정값 리스트
            target_value: 목표값
            std_dev: 표준편차
            lambda_param: 스무딩 파라미터 (기본값 0.2)
            l: 관리한계 계수 (기본값 3.0)
        """
        ewma = EWMAChart(target_value, std_dev, lambda_param, l)
        return ewma.calculate(measurements)

    @staticmethod
    def calculate_from_measurements(
        measurements_data: List[Dict],
        target_value: float,
        std_dev: float,
        chart_type: str = 'CUSUM',
        **params
    ) -> Dict[str, any]:
        """
        측정 데이터에서 관리도 계산

        Args:
            measurements_data: 측정 데이터 리스트 (measurement_value 포함)
            target_value: 목표값
            std_dev: 표준편차
            chart_type: 'CUSUM' 또는 'EWMA'
            **params: 추가 파라미터 (k, h, lambda, l 등)
        """
        measurements = [m['measurement_value'] for m in measurements_data]

        if chart_type == 'CUSUM':
            return AdvancedControlChartService.calculate_cusum(
                measurements,
                target_value,
                std_dev,
                k=params.get('k', 0.5),
                h=params.get('h', 5.0)
            )
        elif chart_type == 'EWMA':
            return AdvancedControlChartService.calculate_ewma(
                measurements,
                target_value,
                std_dev,
                lambda_param=params.get('lambda_param', 0.2),
                l=params.get('l', 3.0)
            )
        else:
            raise ValueError(f"Unknown chart type: {chart_type}")

    @staticmethod
    def get_recommendations(cusum_result: Dict, ewma_result: Dict) -> List[str]:
        """
        CUSUM과 EWMA 결과를 기반으로 개선 권장사항 생성

        Returns:
            권장사항 리스트
        """
        recommendations = []

        # CUSUM 분석
        if cusum_result['total_violations'] > 0:
            recommendations.append(
                f"CUSUM: {cusum_result['total_violations']}개의 위반이 감지되었습니다. "
                "공정 평균이 목표값에서 이동했을 가능성이 높습니다. "
                "공정을 목표값으로 재조정하세요."
            )

        # EWMA 분석
        if ewma_result['total_violations'] > 0:
            recommendations.append(
                f"EWMA: {ewma_result['total_violations']}개의 위반이 감지되었습니다. "
                "작은 변동이 지속되고 있습니다. 원인을 분석하고 조치하세요."
            )

        # 두 관리도 모두 위반이 있는 경우
        if cusum_result['total_violations'] > 0 and ewma_result['total_violations'] > 0:
            recommendations.append(
                "CUSUM과 EWMA 모두에서 위반이 감지되었습니다. "
                "공정에 중대한 이상이 발생했을 가능성이 높습니다. "
                "즉시 공정을 중지하고 원인을 조사하세요."
            )

        # 위반이 없는 경우
        if cusum_result['total_violations'] == 0 and ewma_result['total_violations'] == 0:
            recommendations.append(
                "CUSUM과 EWMA 모두 정상 범위 내입니다. "
                "공정이 안정적이며 목표값을 유지하고 있습니다."
            )

        return recommendations
