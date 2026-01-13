"""
미계획 원인 자동 분류기

STEP 3: 최적화 후 누락/지연 주문의 원인을 자동으로 분석하고 분류
"""
import logging
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg, Sum, Count

logger = logging.getLogger(__name__)


class UnplannedClassifier:
    """
    미계획 원인 자동 분류기

    최적화 결과에서 미배정 또는 지연된 주문을 식별하고,
    4가지 원인 코드(CAPACITY_SHORTAGE, CALENDAR_CONFLICT, PRIORITY_LOSS, DATA_MISSING)로 분류
    """

    def __init__(self, scenario_id):
        """
        Args:
            scenario_id: 분석 대상 시나리오 ID
        """
        self.scenario_id = scenario_id
        self.scenario = None
        self.schedule_result = None

    def analyze(self, schedule_rows, orders):
        """
        미계획/지연 주문 분석 및 원인 분류

        Args:
            schedule_rows: 최적화 결과 스케줄 (list of dict)
                - wo_no, mc_cd, fr_ts, to_ts 포함
            orders: 전체 주문 목록 (QuerySet or list)
                - StageFactPlanOut 또는 유사 구조

        Returns:
            list[UnplannedReason]: 생성된 원인 분석 레코드
        """
        from apps.aps.scenario_models import Scenario, ScenarioResult
        from apps.aps.analytics_models import UnplannedReason

        # 1. 시나리오 및 결과 조회
        try:
            self.scenario = Scenario.objects.get(scenario_id=self.scenario_id)
            self.schedule_result = ScenarioResult.objects.filter(
                scenario=self.scenario
            ).order_by('-created_at').first()
        except Scenario.DoesNotExist:
            logger.error(f"Scenario {self.scenario_id} not found")
            return []

        if not self.schedule_result:
            logger.warning(f"No ScenarioResult found for scenario {self.scenario_id}")
            return []

        logger.info(
            f"Analyzing unplanned reasons for scenario {self.scenario_id}: "
            f"{len(schedule_rows)} scheduled, {len(orders)} total orders"
        )

        # 2. 스케줄된 작업 식별
        scheduled_wo_nos = set()
        scheduled_dict = {}  # wo_no -> schedule info

        for row in schedule_rows:
            wo_no = row.get('wo_no')
            if wo_no:
                scheduled_wo_nos.add(wo_no)
                scheduled_dict[wo_no] = row

        # 3. 미계획 작업 추출
        unplanned_orders = []
        for order in orders:
            wo_no = getattr(order, 'wo_no', None)
            if wo_no and wo_no not in scheduled_wo_nos:
                unplanned_orders.append(order)

        logger.info(f"Found {len(unplanned_orders)} unplanned orders")

        # 4. 지연 작업 추출
        delayed_orders = self._find_delayed_orders(scheduled_dict, orders)
        logger.info(f"Found {len(delayed_orders)} delayed orders")

        # 5. 원인 분류
        reasons = []

        # 미계획 작업 분류
        for order in unplanned_orders:
            reason = self._classify_unplanned(order, 'UNPLANNED', delay_hours=0)
            if reason:
                reasons.append(reason)

        # 지연 작업 분류
        for order, delay_hours in delayed_orders:
            reason = self._classify_unplanned(order, 'DELAYED', delay_hours=delay_hours)
            if reason:
                reasons.append(reason)

        # 6. DB 저장
        if reasons:
            UnplannedReason.objects.bulk_create(reasons)
            logger.info(f"Created {len(reasons)} UnplannedReason records")

            # 원인별 통계
            reason_stats = {}
            for r in reasons:
                code = r.reason_code
                reason_stats[code] = reason_stats.get(code, 0) + 1

            logger.info(f"Reason breakdown: {reason_stats}")

        return reasons

    def _classify_unplanned(self, order, status, delay_hours=0):
        """
        개별 주문의 미계획 원인 분류

        판정 우선순위:
        1. DATA_MISSING (데이터 품질 이슈)
        2. CAPACITY_SHORTAGE (용량 제약)
        3. CALENDAR_CONFLICT (캘린더 제약) - MVP에서는 제외
        4. PRIORITY_LOSS (우선순위 정책)

        Args:
            order: 주문 객체 (StageFactPlanOut 등)
            status: 'UNPLANNED' 또는 'DELAYED'
            delay_hours: 지연 시간 (시간 단위)

        Returns:
            UnplannedReason: 원인 분석 레코드 (또는 None)
        """
        from apps.aps.analytics_models import UnplannedReason

        wo_no = getattr(order, 'wo_no', None)
        if not wo_no:
            return None

        # 기본 정보 추출
        itm_id = getattr(order, 'itm_id', None)
        mc_cd = getattr(order, 'mc_cd', None)

        # 납기일 추출 (to_ts를 납기일로 간주)
        due_date = getattr(order, 'to_ts', None)

        # 우선순위 (기본값 5)
        priority = getattr(order, 'priority', 5)

        # ========================================
        # 1. DATA_MISSING 검증
        # ========================================
        if not self._has_operations(order):
            return UnplannedReason(
                scenario=self.scenario,
                wo_no=wo_no,
                itm_id=itm_id,
                mc_cd=mc_cd,
                due_date=due_date,
                priority=priority,
                reason_code='DATA_MISSING',
                status=status,
                delay_hours=delay_hours,
                confidence=1.0,
                explanation='Operation 정보 없음 - 작업 경로(Routing) 데이터 누락',
                analysis_data={'check': 'operation_missing'}
            )

        if not self._has_valid_resource(order):
            return UnplannedReason(
                scenario=self.scenario,
                wo_no=wo_no,
                itm_id=itm_id,
                mc_cd=mc_cd,
                due_date=due_date,
                priority=priority,
                reason_code='DATA_MISSING',
                status=status,
                delay_hours=delay_hours,
                confidence=1.0,
                explanation='유효한 자원(Resource) 정보 없음 - 설비 배정 불가',
                analysis_data={'check': 'resource_missing', 'mc_cd': mc_cd}
            )

        # ========================================
        # 2. CAPACITY_SHORTAGE 검증
        # ========================================
        capacity_ratio = self._calculate_capacity_ratio()

        if capacity_ratio > 0.95:
            return UnplannedReason(
                scenario=self.scenario,
                wo_no=wo_no,
                itm_id=itm_id,
                mc_cd=mc_cd,
                due_date=due_date,
                priority=priority,
                reason_code='CAPACITY_SHORTAGE',
                status=status,
                delay_hours=delay_hours,
                confidence=0.85,
                explanation=(
                    f'자원 사용률 {capacity_ratio*100:.1f}% - 가용 시간 대비 작업량 초과. '
                    f'추가 자원 확보 또는 일정 조정 필요.'
                ),
                analysis_data={
                    'capacity_ratio': round(capacity_ratio, 3),
                    'threshold': 0.95,
                    'total_machines': self.schedule_result.total_machines if self.schedule_result else 0
                }
            )

        # ========================================
        # 3. CALENDAR_CONFLICT (MVP 제외)
        # ========================================
        # TODO: PlantCalendar 통합 후 구현
        # if self._is_calendar_conflict(order):
        #     return UnplannedReason(..., reason_code='CALENDAR_CONFLICT', ...)

        # ========================================
        # 4. PRIORITY_LOSS (기본값)
        # ========================================
        avg_priority = self._get_avg_priority()

        if priority < avg_priority:
            return UnplannedReason(
                scenario=self.scenario,
                wo_no=wo_no,
                itm_id=itm_id,
                mc_cd=mc_cd,
                due_date=due_date,
                priority=priority,
                reason_code='PRIORITY_LOSS',
                status=status,
                delay_hours=delay_hours,
                confidence=0.7,
                explanation=(
                    f'우선순위 낮음 ({priority} < 평균 {avg_priority:.1f}) - '
                    f'고우선순위 작업에 밀려 배정 실패. 우선순위 재조정 검토.'
                ),
                analysis_data={
                    'priority': priority,
                    'avg_priority': round(avg_priority, 2),
                    'delta': round(avg_priority - priority, 2)
                }
            )
        else:
            # 우선순위가 평균 이상인데도 미계획/지연
            # → 용량 부족 가능성 (낮은 신뢰도)
            return UnplannedReason(
                scenario=self.scenario,
                wo_no=wo_no,
                itm_id=itm_id,
                mc_cd=mc_cd,
                due_date=due_date,
                priority=priority,
                reason_code='CAPACITY_SHORTAGE',
                status=status,
                delay_hours=delay_hours,
                confidence=0.6,
                explanation=(
                    f'우선순위 정상({priority})이나 배정 실패 - '
                    f'전체 작업량 과다로 추정. 용량 검토 필요.'
                ),
                analysis_data={
                    'priority': priority,
                    'avg_priority': round(avg_priority, 2),
                    'capacity_ratio': round(capacity_ratio, 3)
                }
            )

    def _find_delayed_orders(self, scheduled_dict, orders):
        """
        지연된 작업 찾기

        Args:
            scheduled_dict: {wo_no: schedule_info}
            orders: 전체 주문 목록

        Returns:
            list[(order, delay_hours)]: 지연된 주문과 지연 시간
        """
        delayed = []

        for order in orders:
            wo_no = getattr(order, 'wo_no', None)
            if not wo_no or wo_no not in scheduled_dict:
                continue

            schedule_info = scheduled_dict[wo_no]

            # 완료 시간
            completion_time = schedule_info.get('to_ts')
            if not completion_time:
                continue

            # 납기일 (원본 주문의 to_ts)
            due_date = getattr(order, 'to_ts', None)
            if not due_date:
                continue

            # 지연 계산
            if completion_time > due_date:
                delay_seconds = (completion_time - due_date).total_seconds()
                delay_hours = delay_seconds / 3600
                delayed.append((order, delay_hours))

        return delayed

    def _calculate_capacity_ratio(self):
        """
        자원 가용시간 대비 작업량 비율 계산

        Returns:
            float: 용량 비율 (0~1+)
                - 0.95 초과: 용량 부족 (CAPACITY_SHORTAGE)
                - 0.80~0.95: 적정
                - 0.80 미만: 여유
        """
        if not self.schedule_result:
            return 0

        # 1. 총 작업 시간 계산
        schedule = self.schedule_result.schedule or []

        total_work_hours = 0
        for row in schedule:
            fr_ts = row.get('fr_ts')
            to_ts = row.get('to_ts')

            if fr_ts and to_ts:
                # datetime 또는 string 처리
                if isinstance(fr_ts, str):
                    from dateutil import parser
                    fr_ts = parser.parse(fr_ts)
                    to_ts = parser.parse(to_ts)

                duration_hours = (to_ts - fr_ts).total_seconds() / 3600
                total_work_hours += duration_hours

        # 2. 총 가용 시간 계산
        total_machines = self.schedule_result.total_machines or 1
        work_hours_per_day = 8  # 기본 8시간 근무
        planning_days = 7  # 기본 1주일 계획

        total_available_hours = total_machines * work_hours_per_day * planning_days

        # 3. 비율 계산
        if total_available_hours > 0:
            ratio = total_work_hours / total_available_hours
            return min(ratio, 1.5)  # 최대 150%로 제한 (과부하)
        else:
            return 0

    def _get_avg_priority(self):
        """
        스케줄된 작업의 평균 우선순위

        Returns:
            float: 평균 우선순위 (기본값 5.0)
        """
        if not self.schedule_result or not self.schedule_result.schedule:
            return 5.0  # 기본값

        # 실제 구현 시 주문 테이블에서 priority 조회 필요
        # MVP에서는 기본값 사용
        return 5.0

    def _has_operations(self, order):
        """
        Operation 정보 존재 여부

        Args:
            order: 주문 객체

        Returns:
            bool: True if operation 정보 존재
        """
        # StageFactPlanOut의 경우 mc_cd가 있으면 operation 존재로 간주
        mc_cd = getattr(order, 'mc_cd', None)
        return mc_cd is not None and mc_cd != ''

    def _has_valid_resource(self, order):
        """
        유효한 자원 존재 여부

        Args:
            order: 주문 객체

        Returns:
            bool: True if 유효한 자원 정보 존재
        """
        mc_cd = getattr(order, 'mc_cd', None)

        # 자원 코드가 있고, 유효한 형식인지 검증
        if not mc_cd or mc_cd == '':
            return False

        # 실제 구현 시 Resource 테이블에서 존재 여부 확인
        # MVP에서는 mc_cd 존재 여부만 검증
        return True

    def _is_calendar_conflict(self, order):
        """
        캘린더 충돌 여부 (PlantCalendar)

        Args:
            order: 주문 객체

        Returns:
            bool: True if 캘린더 충돌
        """
        # TODO: PlantCalendar 통합 후 구현
        # - 작업 시작 시간이 비가동 시간대인지 확인
        # - 근무시간 외 배정 시도 검증
        # - 휴일/공휴일 충돌 검증

        # MVP에서는 미구현
        return False


def analyze_unplanned_reasons(scenario_id, schedule_rows, orders):
    """
    미계획 원인 분석 헬퍼 함수

    Args:
        scenario_id: 시나리오 ID
        schedule_rows: 스케줄 결과 (list of dict)
        orders: 전체 주문 목록 (QuerySet or list)

    Returns:
        list[UnplannedReason]: 생성된 원인 분석 레코드
    """
    classifier = UnplannedClassifier(scenario_id)
    return classifier.analyze(schedule_rows, orders)
