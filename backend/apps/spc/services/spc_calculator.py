"""
SPC 통계 계산 엔진
X-bar & R Chart, X-bar & S Chart, p-Chart, c-Chart 등의 관리 한계선 계산
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ControlLimits:
    """관리 한계선 데이터 클래스"""
    ucl: float  # Upper Control Limit
    cl: float   # Center Line
    lcl: float  # Lower Control Limit


class SPCConstants:
    """SPC 상수표 (Montgomery, Statistical Quality Control 7th ed.)"""

    # X-bar Chart 계산용 A2 상수 (d2 기반)
    A2 = {
        2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483,
        7: 0.419, 8: 0.373, 9: 0.337, 10: 0.308, 11: 0.285,
        12: 0.266, 13: 0.249, 14: 0.235, 15: 0.223, 16: 0.212,
        17: 0.203, 18: 0.194, 19: 0.187, 20: 0.180, 21: 0.173,
        22: 0.167, 23: 0.162, 24: 0.157, 25: 0.153
    }

    # R Chart 계산용 D3, D4 상수
    D3 = {
        2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0.076,
        8: 0.136, 9: 0.184, 10: 0.223, 11: 0.256, 12: 0.283,
        13: 0.307, 14: 0.328, 15: 0.347, 16: 0.363, 17: 0.378,
        18: 0.391, 19: 0.403, 20: 0.415, 21: 0.425, 22: 0.434,
        23: 0.443, 24: 0.451, 25: 0.459
    }

    D4 = {
        2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114, 6: 2.004,
        7: 1.924, 8: 1.864, 9: 1.816, 10: 1.777, 11: 1.744,
        12: 1.717, 13: 1.693, 14: 1.672, 15: 1.653, 16: 1.637,
        17: 1.622, 18: 1.608, 19: 1.597, 20: 1.585, 21: 1.575,
        22: 1.566, 23: 1.557, 24: 1.548, 25: 1.541
    }

    # S Chart 계산용 B3, B4 상수
    B3 = {
        2: 0, 3: 0, 4: 0, 5: 0, 6: 0.030, 7: 0.118,
        8: 0.185, 9: 0.239, 10: 0.284, 11: 0.321, 12: 0.354,
        13: 0.382, 14: 0.406, 15: 0.428, 16: 0.448, 17: 0.466,
        18: 0.482, 19: 0.497, 20: 0.510, 21: 0.523, 22: 0.534,
        23: 0.545, 24: 0.555, 25: 0.565
    }

    B4 = {
        2: 3.267, 3: 2.568, 4: 2.266, 5: 2.089, 6: 1.970,
        7: 1.882, 8: 1.815, 9: 1.761, 10: 1.716, 11: 1.679,
        12: 1.646, 13: 1.618, 14: 1.594, 15: 1.572, 16: 1.552,
        17: 1.534, 18: 1.518, 19: 1.503, 20: 1.490, 21: 1.477,
        22: 1.466, 23: 1.455, 24: 1.445, 25: 1.435
    }

    # X-bar Chart 계산용 A3 상수 (표준편차 기반)
    A3 = {
        2: 2.659, 3: 1.954, 4: 1.628, 5: 1.427, 6: 1.287,
        7: 1.182, 8: 1.099, 9: 1.032, 10: 0.975, 11: 0.927,
        12: 0.886, 13: 0.850, 14: 0.817, 15: 0.789, 16: 0.763,
        17: 0.739, 18: 0.718, 19: 0.698, 20: 0.680, 21: 0.663,
        22: 0.647, 23: 0.633, 24: 0.619, 25: 0.606
    }

    # c4 상수 (불편 추정량)
    c4 = {
        2: 0.7979, 3: 0.8862, 4: 0.9213, 5: 0.9400, 6: 0.9515,
        7: 0.9594, 8: 0.9650, 9: 0.9693, 10: 0.9727, 11: 0.9754,
        12: 0.9776, 13: 0.9794, 14: 0.9810, 15: 0.9823, 16: 0.9835,
        17: 0.9845, 18: 0.9854, 19: 0.9862, 20: 0.9869, 21: 0.9876,
        22: 0.9882, 23: 0.9887, 24: 0.9892, 25: 0.9896
    }


class SPCCalculator:
    """SPC 관리도 계산 엔진"""

    def __init__(self):
        self.constants = SPCConstants()

    def calculate_xbar_r_limits(
        self,
        data: List[List[float]],
        subgroup_size: Optional[int] = None
    ) -> Tuple[ControlLimits, ControlLimits]:
        """
        X-bar & R Chart 관리 한계선 계산

        Args:
            data: 부분군별 측정 데이터 [[subgroup1], [subgroup2], ...]
            subgroup_size: 부분군 크기 (None이면 자동 계산)

        Returns:
            (xbar_limits, r_limits): X-bar와 R Chart의 관리 한계선
        """
        if not data or len(data) == 0:
            raise ValueError("데이터가 비어있습니다")

        # 부분군 크기 결정
        if subgroup_size is None:
            subgroup_size = len(data[0])

        if subgroup_size < 2 or subgroup_size > 25:
            raise ValueError("부분군 크기는 2-25 사이여야 합니다")

        # 각 부분군의 평균과 범위 계산
        xbars = [np.mean(subgroup) for subgroup in data]
        ranges = [max(subgroup) - min(subgroup) for subgroup in data]

        # 전체 평균 계산
        xbar_mean = np.mean(xbars)
        r_mean = np.mean(ranges)

        # 상수 조회
        A2 = self.constants.A2[subgroup_size]
        D3 = self.constants.D3[subgroup_size]
        D4 = self.constants.D4[subgroup_size]

        # X-bar Chart 한계선
        xbar_limits = ControlLimits(
            ucl=xbar_mean + A2 * r_mean,
            cl=xbar_mean,
            lcl=xbar_mean - A2 * r_mean
        )

        # R Chart 한계선
        r_limits = ControlLimits(
            ucl=D4 * r_mean,
            cl=r_mean,
            lcl=D3 * r_mean
        )

        return xbar_limits, r_limits

    def calculate_xbar_s_limits(
        self,
        data: List[List[float]],
        subgroup_size: Optional[int] = None
    ) -> Tuple[ControlLimits, ControlLimits]:
        """
        X-bar & S Chart 관리 한계선 계산 (표준편차 사용)

        Args:
            data: 부분군별 측정 데이터
            subgroup_size: 부분군 크기

        Returns:
            (xbar_limits, s_limits): X-bar와 S Chart의 관리 한계선
        """
        if not data or len(data) == 0:
            raise ValueError("데이터가 비어있습니다")

        if subgroup_size is None:
            subgroup_size = len(data[0])

        if subgroup_size < 2 or subgroup_size > 25:
            raise ValueError("부분군 크기는 2-25 사이여야 합니다")

        # 각 부분군의 평균과 표준편차 계산
        xbars = [np.mean(subgroup) for subgroup in data]
        stds = [np.std(subgroup, ddof=1) for subgroup in data]

        # 전체 평균 계산
        xbar_mean = np.mean(xbars)
        s_mean = np.mean(stds)

        # 상수 조회
        A3 = self.constants.A3[subgroup_size]
        B3 = self.constants.B3[subgroup_size]
        B4 = self.constants.B4[subgroup_size]

        # X-bar Chart 한계선
        xbar_limits = ControlLimits(
            ucl=xbar_mean + A3 * s_mean,
            cl=xbar_mean,
            lcl=xbar_mean - A3 * s_mean
        )

        # S Chart 한계선
        s_limits = ControlLimits(
            ucl=B4 * s_mean,
            cl=s_mean,
            lcl=B3 * s_mean
        )

        return xbar_limits, s_limits

    def calculate_i_mr_limits(
        self,
        data: List[float]
    ) -> Tuple[ControlLimits, ControlLimits]:
        """
        Individual & Moving Range Chart 관리 한계선 계산

        Args:
            data: 개별 측정값 리스트

        Returns:
            (i_limits, mr_limits): I Chart와 MR Chart의 관리 한계선
        """
        if not data or len(data) < 2:
            raise ValueError("최소 2개의 데이터가 필요합니다")

        # 개별값의 평균
        x_mean = np.mean(data)

        # Moving Range 계산 (연속된 두 값의 차이)
        mr_values = [abs(data[i] - data[i-1]) for i in range(1, len(data))]
        mr_mean = np.mean(mr_values)

        # Individual Chart 한계선 (d2=1.128 for n=2)
        i_limits = ControlLimits(
            ucl=x_mean + 2.66 * mr_mean,
            cl=x_mean,
            lcl=x_mean - 2.66 * mr_mean
        )

        # Moving Range Chart 한계선
        mr_limits = ControlLimits(
            ucl=3.267 * mr_mean,
            cl=mr_mean,
            lcl=0  # MR의 LCL은 0
        )

        return i_limits, mr_limits

    def calculate_p_chart_limits(
        self,
        defectives: List[int],
        sample_sizes: List[int]
    ) -> ControlLimits:
        """
        p-Chart (불량률 관리도) 한계선 계산

        Args:
            defectives: 각 샘플의 불량 개수 리스트
            sample_sizes: 각 샘플의 크기 리스트

        Returns:
            p_limits: p-Chart 관리 한계선
        """
        if len(defectives) != len(sample_sizes):
            raise ValueError("defectives와 sample_sizes의 길이가 같아야 합니다")

        # 전체 불량률 계산
        total_defectives = sum(defectives)
        total_samples = sum(sample_sizes)
        p_mean = total_defectives / total_samples

        # 평균 샘플 크기
        n_mean = np.mean(sample_sizes)

        # 관리 한계선 계산
        std_error = np.sqrt(p_mean * (1 - p_mean) / n_mean)

        p_limits = ControlLimits(
            ucl=min(p_mean + 3 * std_error, 1.0),  # 최대 1.0
            cl=p_mean,
            lcl=max(p_mean - 3 * std_error, 0.0)   # 최소 0.0
        )

        return p_limits

    def calculate_np_chart_limits(
        self,
        defectives: List[int],
        sample_size: int
    ) -> ControlLimits:
        """
        np-Chart (불량수 관리도) 한계선 계산

        Args:
            defectives: 각 샘플의 불량 개수 리스트
            sample_size: 고정된 샘플 크기

        Returns:
            np_limits: np-Chart 관리 한계선
        """
        # 평균 불량 개수
        np_mean = np.mean(defectives)

        # 불량률 p 계산
        p = np_mean / sample_size

        # 관리 한계선 계산
        std = np.sqrt(sample_size * p * (1 - p))

        np_limits = ControlLimits(
            ucl=min(np_mean + 3 * std, sample_size),
            cl=np_mean,
            lcl=max(np_mean - 3 * std, 0)
        )

        return np_limits

    def calculate_c_chart_limits(
        self,
        defects: List[int]
    ) -> ControlLimits:
        """
        c-Chart (결점수 관리도) 한계선 계산

        Args:
            defects: 각 샘플의 결점 개수 리스트

        Returns:
            c_limits: c-Chart 관리 한계선
        """
        # 평균 결점수
        c_mean = np.mean(defects)

        # 관리 한계선 계산 (포아송 분포)
        std = np.sqrt(c_mean)

        c_limits = ControlLimits(
            ucl=c_mean + 3 * std,
            cl=c_mean,
            lcl=max(c_mean - 3 * std, 0)
        )

        return c_limits

    def calculate_u_chart_limits(
        self,
        defects: List[int],
        inspection_units: List[float]
    ) -> ControlLimits:
        """
        u-Chart (단위당 결점수 관리도) 한계선 계산

        Args:
            defects: 각 샘플의 결점 개수 리스트
            inspection_units: 각 샘플의 검사 단위 수 (면적, 길이 등)

        Returns:
            u_limits: u-Chart 관리 한계선
        """
        if len(defects) != len(inspection_units):
            raise ValueError("defects와 inspection_units의 길이가 같아야 합니다")

        # 평균 단위당 결점수
        total_defects = sum(defects)
        total_units = sum(inspection_units)
        u_mean = total_defects / total_units

        # 평균 검사 단위
        n_mean = np.mean(inspection_units)

        # 관리 한계선 계산
        std = np.sqrt(u_mean / n_mean)

        u_limits = ControlLimits(
            ucl=u_mean + 3 * std,
            cl=u_mean,
            lcl=max(u_mean - 3 * std, 0)
        )

        return u_limits

    def aggregate_measurements_to_subgroups(
        self,
        measurements: List[Dict],
        subgroup_size: int = 5
    ) -> List[List[float]]:
        """
        측정 데이터를 부분군으로 집계

        Args:
            measurements: [{'value': float, 'subgroup': int}, ...]
            subgroup_size: 부분군 크기

        Returns:
            부분군별 데이터 리스트
        """
        from collections import defaultdict

        subgroups_dict = defaultdict(list)

        for m in measurements:
            subgroup_num = m.get('subgroup_number', 0)
            value = m.get('measurement_value')
            subgroups_dict[subgroup_num].append(value)

        # 부분군 번호 순으로 정렬
        subgroups = [subgroups_dict[key] for key in sorted(subgroups_dict.keys())]

        return subgroups


# 사용 예시
if __name__ == '__main__':
    calculator = SPCCalculator()

    # 예제 데이터
    data = [
        [10.2, 10.1, 10.3, 10.0, 10.2],
        [10.3, 10.2, 10.4, 10.1, 10.3],
        [10.1, 10.0, 10.2, 10.1, 10.1],
        [10.2, 10.3, 10.1, 10.2, 10.0],
        [10.0, 10.1, 10.2, 10.3, 10.1],
    ]

    xbar_limits, r_limits = calculator.calculate_xbar_r_limits(data)

    print(f"X-bar Chart: UCL={xbar_limits.ucl:.3f}, CL={xbar_limits.cl:.3f}, LCL={xbar_limits.lcl:.3f}")
    print(f"R Chart: UCL={r_limits.ucl:.3f}, CL={r_limits.cl:.3f}, LCL={r_limits.lcl:.3f}")
