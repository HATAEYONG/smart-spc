"""
공정능력 분석 (Process Capability Analysis)
Cp, Cpk, Pp, Ppk 계산 및 정규성 검정
"""
import numpy as np
from scipy import stats
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ProcessCapabilityResult:
    """공정능력 분석 결과"""
    # 공정능력 지수
    cp: float
    cpk: float
    cpu: float
    cpl: float

    # 장기 공정능력 지수
    pp: Optional[float] = None
    ppk: Optional[float] = None

    # 통계 정보
    mean: float = 0.0
    std_dev: float = 0.0
    std_dev_within: float = 0.0  # 부분군 내 표준편차
    std_dev_overall: float = 0.0  # 전체 표준편차
    sample_size: int = 0

    # 정규성 검정
    is_normal: bool = True
    normality_test: str = 'Shapiro-Wilk'
    test_statistic: float = 0.0
    p_value: float = 1.0

    # 규격 정보
    usl: float = 0.0
    lsl: float = 0.0
    target: Optional[float] = None

    # 불량률 추정
    expected_ppm_above_usl: float = 0.0
    expected_ppm_below_lsl: float = 0.0
    expected_ppm_total: float = 0.0


class ProcessCapabilityAnalyzer:
    """공정능력 분석기"""

    def __init__(self):
        self.alpha = 0.05  # 유의수준

    def analyze(
        self,
        data: List[float],
        usl: float,
        lsl: float,
        target: Optional[float] = None,
        subgroup_data: Optional[List[List[float]]] = None
    ) -> ProcessCapabilityResult:
        """
        공정능력 분석 수행

        Args:
            data: 전체 측정 데이터
            usl: Upper Specification Limit
            lsl: Lower Specification Limit
            target: 목표값 (없으면 규격 중심값)
            subgroup_data: 부분군 데이터 (Cp/Cpk 계산용)

        Returns:
            ProcessCapabilityResult
        """
        if not data or len(data) < 2:
            raise ValueError("최소 2개의 데이터가 필요합니다")

        if usl <= lsl:
            raise ValueError("USL은 LSL보다 커야 합니다")

        # 기본 통계
        mean = np.mean(data)
        std_overall = np.std(data, ddof=1)

        # 부분군 내 표준편차 계산
        if subgroup_data is not None and len(subgroup_data) > 0:
            std_within = self._calculate_within_std(subgroup_data)
        else:
            std_within = std_overall

        # 목표값 설정
        if target is None:
            target = (usl + lsl) / 2

        # Cp, Cpk 계산 (부분군 내 변동)
        cp = (usl - lsl) / (6 * std_within)
        cpu = (usl - mean) / (3 * std_within)
        cpl = (mean - lsl) / (3 * std_within)
        cpk = min(cpu, cpl)

        # Pp, Ppk 계산 (전체 변동)
        pp = (usl - lsl) / (6 * std_overall)
        ppu = (usl - mean) / (3 * std_overall)
        ppl = (mean - lsl) / (3 * std_overall)
        ppk = min(ppu, ppl)

        # 정규성 검정
        is_normal, test_stat, p_value = self.normality_test(data)

        # 불량률 추정 (정규분포 가정)
        ppm_above, ppm_below, ppm_total = self._estimate_defect_rate(
            mean, std_within, usl, lsl
        )

        result = ProcessCapabilityResult(
            cp=cp,
            cpk=cpk,
            cpu=cpu,
            cpl=cpl,
            pp=pp,
            ppk=ppk,
            mean=mean,
            std_dev=std_within,
            std_dev_within=std_within,
            std_dev_overall=std_overall,
            sample_size=len(data),
            is_normal=is_normal,
            test_statistic=test_stat,
            p_value=p_value,
            usl=usl,
            lsl=lsl,
            target=target,
            expected_ppm_above_usl=ppm_above,
            expected_ppm_below_lsl=ppm_below,
            expected_ppm_total=ppm_total
        )

        return result

    def _calculate_within_std(self, subgroup_data: List[List[float]]) -> float:
        """
        부분군 내 표준편차 계산 (Pooled Standard Deviation)

        Args:
            subgroup_data: [[subgroup1], [subgroup2], ...]

        Returns:
            부분군 내 표준편차
        """
        # 각 부분군의 분산 계산
        variances = []
        sample_sizes = []

        for subgroup in subgroup_data:
            if len(subgroup) > 1:
                var = np.var(subgroup, ddof=1)
                variances.append(var)
                sample_sizes.append(len(subgroup))

        if not variances:
            raise ValueError("유효한 부분군 데이터가 없습니다")

        # Pooled variance 계산
        total_df = sum(n - 1 for n in sample_sizes)
        pooled_var = sum((n - 1) * var for n, var in zip(sample_sizes, variances)) / total_df

        return np.sqrt(pooled_var)

    def normality_test(
        self,
        data: List[float],
        method: str = 'shapiro'
    ) -> Tuple[bool, float, float]:
        """
        정규성 검정

        Args:
            data: 측정 데이터
            method: 'shapiro' (Shapiro-Wilk) 또는 'anderson' (Anderson-Darling)

        Returns:
            (is_normal, test_statistic, p_value)
        """
        if len(data) < 3:
            return True, 0.0, 1.0

        if method == 'shapiro':
            statistic, p_value = stats.shapiro(data)
            is_normal = p_value > self.alpha
            return is_normal, statistic, p_value

        elif method == 'anderson':
            result = stats.anderson(data, dist='norm')
            # Anderson-Darling의 경우 critical value와 비교
            # 5% 유의수준에서 critical value는 보통 result.critical_values[2]
            is_normal = result.statistic < result.critical_values[2]
            return is_normal, result.statistic, 0.0  # p-value는 직접 계산 안됨

        else:
            raise ValueError(f"Unknown normality test method: {method}")

    def _estimate_defect_rate(
        self,
        mean: float,
        std: float,
        usl: float,
        lsl: float
    ) -> Tuple[float, float, float]:
        """
        불량률 추정 (정규분포 가정)

        Returns:
            (ppm_above_usl, ppm_below_lsl, ppm_total)
        """
        # Z-score 계산
        z_upper = (usl - mean) / std
        z_lower = (mean - lsl) / std

        # 누적분포함수를 이용한 확률 계산
        prob_above_usl = 1 - stats.norm.cdf(z_upper)
        prob_below_lsl = stats.norm.cdf(-z_lower)

        # PPM (Parts Per Million) 변환
        ppm_above = prob_above_usl * 1_000_000
        ppm_below = prob_below_lsl * 1_000_000
        ppm_total = ppm_above + ppm_below

        return ppm_above, ppm_below, ppm_total

    def generate_histogram_data(
        self,
        data: List[float],
        usl: float,
        lsl: float,
        num_bins: int = 20
    ) -> Dict:
        """
        히스토그램 데이터 생성 (정규분포 곡선 포함)

        Returns:
            {
                'bins': [...],
                'counts': [...],
                'normal_curve': {'x': [...], 'y': [...]},
                'spec_limits': {'usl': ..., 'lsl': ...}
            }
        """
        # 히스토그램 계산
        counts, bin_edges = np.histogram(data, bins=num_bins)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        # 정규분포 곡선 계산
        mean = np.mean(data)
        std = np.std(data, ddof=1)

        x_range = np.linspace(min(data), max(data), 200)
        normal_curve = stats.norm.pdf(x_range, mean, std)

        # 히스토그램과 같은 스케일로 조정
        bin_width = bin_edges[1] - bin_edges[0]
        normal_curve_scaled = normal_curve * len(data) * bin_width

        return {
            'bins': bin_centers.tolist(),
            'counts': counts.tolist(),
            'normal_curve': {
                'x': x_range.tolist(),
                'y': normal_curve_scaled.tolist()
            },
            'spec_limits': {
                'usl': usl,
                'lsl': lsl,
                'mean': mean
            }
        }

    def interpret_cpk(self, cpk: float) -> Dict:
        """
        Cpk 값 해석

        Returns:
            {
                'rating': '우수' | '양호' | '보통' | '미흡' | '부적합',
                'description': '...',
                'color': 'green' | 'yellow' | 'orange' | 'red'
            }
        """
        if cpk >= 2.0:
            return {
                'rating': '우수',
                'description': 'Six Sigma 수준 (불량률 < 3.4 PPM)',
                'color': 'green',
                'action': '현재 수준 유지'
            }
        elif cpk >= 1.67:
            return {
                'rating': '양호',
                'description': '높은 공정능력 (불량률 < 0.6 PPM)',
                'color': 'green',
                'action': '현재 수준 유지, 지속적 모니터링'
            }
        elif cpk >= 1.33:
            return {
                'rating': '보통',
                'description': '허용 가능한 공정능력 (불량률 < 63 PPM)',
                'color': 'yellow',
                'action': '공정 개선 검토'
            }
        elif cpk >= 1.0:
            return {
                'rating': '미흡',
                'description': '최소 요구 수준 (불량률 < 2700 PPM)',
                'color': 'orange',
                'action': '즉각적인 공정 개선 필요'
            }
        else:
            return {
                'rating': '부적합',
                'description': '공정능력 부족 (불량률 > 2700 PPM)',
                'color': 'red',
                'action': '긴급 조치 필요 - 공정 재설계 검토'
            }

    def compare_cp_cpk(self, cp: float, cpk: float) -> Dict:
        """
        Cp와 Cpk 비교 분석

        Returns:
            {
                'centering': '우수' | '양호' | '미흡',
                'description': '...',
                'offset_ratio': float  # (Cp - Cpk) / Cp
            }
        """
        if cp == 0:
            return {
                'centering': '계산 불가',
                'description': 'Cp가 0입니다',
                'offset_ratio': 0
            }

        offset_ratio = (cp - cpk) / cp

        if offset_ratio <= 0.1:
            return {
                'centering': '우수',
                'description': '공정이 규격 중심에 잘 위치함 (편차 10% 이내)',
                'offset_ratio': offset_ratio
            }
        elif offset_ratio <= 0.25:
            return {
                'centering': '양호',
                'description': '공정 중심이 약간 치우침 (편차 25% 이내)',
                'offset_ratio': offset_ratio,
                'recommendation': '공정 중심 조정 고려'
            }
        else:
            return {
                'centering': '미흡',
                'description': '공정 중심이 크게 치우침 (편차 25% 초과)',
                'offset_ratio': offset_ratio,
                'recommendation': '공정 중심 조정 필요'
            }


# 사용 예시
if __name__ == '__main__':
    analyzer = ProcessCapabilityAnalyzer()

    # 예제 데이터
    data = [10.2, 10.1, 10.3, 10.0, 10.2, 10.1, 10.4, 10.0, 10.2, 10.1,
            10.3, 10.2, 10.0, 10.1, 10.2, 10.3, 10.1, 10.2, 10.0, 10.1]

    usl = 10.5
    lsl = 9.5

    # 부분군 데이터
    subgroup_data = [
        [10.2, 10.1, 10.3, 10.0, 10.2],
        [10.1, 10.4, 10.0, 10.2, 10.1],
        [10.3, 10.2, 10.0, 10.1, 10.2],
        [10.3, 10.1, 10.2, 10.0, 10.1]
    ]

    result = analyzer.analyze(data, usl, lsl, subgroup_data=subgroup_data)

    print(f"Cp: {result.cp:.3f}")
    print(f"Cpk: {result.cpk:.3f}")
    print(f"Pp: {result.pp:.3f}")
    print(f"Ppk: {result.ppk:.3f}")
    print(f"평균: {result.mean:.3f}")
    print(f"표준편차 (부분군 내): {result.std_dev_within:.3f}")
    print(f"표준편차 (전체): {result.std_dev_overall:.3f}")
    print(f"정규성: {result.is_normal} (p-value: {result.p_value:.4f})")
    print(f"예상 불량률: {result.expected_ppm_total:.2f} PPM")

    # 해석
    interpretation = analyzer.interpret_cpk(result.cpk)
    print(f"\nCpk 평가: {interpretation['rating']} - {interpretation['description']}")
    print(f"권장 조치: {interpretation['action']}")

    # Cp vs Cpk 비교
    centering = analyzer.compare_cp_cpk(result.cp, result.cpk)
    print(f"\n중심 위치: {centering['centering']} - {centering['description']}")
