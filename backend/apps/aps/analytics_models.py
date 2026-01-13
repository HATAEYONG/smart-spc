"""
미계획 원인 분석 모델

STEP 3: 최적화 후 누락/지연 주문에 대한 원인 자동 분류
"""
from django.db import models
from django.utils import timezone


class UnplannedReason(models.Model):
    """
    미계획 원인 분석 결과

    최적화 실행 후 스케줄에 배정되지 않았거나 납기가 지연된 주문의 원인을 자동 분류
    """

    # 원인 코드
    REASON_CODES = [
        ('CAPACITY_SHORTAGE', '자원 부족 - 가용시간 대비 작업량 초과'),
        ('CALENDAR_CONFLICT', '캘린더 충돌 - 근무시간/휴일로 배정 불가'),
        ('PRIORITY_LOSS', '우선순위 손실 - 낮은 우선순위로 후순위 배정'),
        ('DATA_MISSING', '데이터 누락 - Routing/Operation/Resource 정보 없음'),
    ]

    # 상태
    STATUS_CHOICES = [
        ('UNPLANNED', '미계획 - 스케줄에 배정되지 않음'),
        ('DELAYED', '지연 - 납기일 초과'),
    ]

    # Primary Key
    reason_id = models.AutoField(primary_key=True)

    # 시나리오 연결
    scenario = models.ForeignKey(
        'Scenario',
        on_delete=models.CASCADE,
        related_name='unplanned_reasons',
        db_index=True
    )

    # 주문 정보
    wo_no = models.CharField(max_length=30, db_index=True)
    itm_id = models.CharField(max_length=50, null=True, blank=True)
    mc_cd = models.CharField(max_length=20, null=True, blank=True)  # 배정 예정이었던 자원

    # 납기/우선순위
    due_date = models.DateTimeField(null=True, blank=True)
    priority = models.IntegerField(default=0)

    # 원인 분류
    reason_code = models.CharField(
        max_length=30,
        choices=REASON_CODES,
        db_index=True
    )

    # 상태
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='UNPLANNED'
    )

    # 분석 메트릭
    delay_hours = models.FloatField(
        default=0,
        help_text='납기 대비 지연 시간 (시간 단위)'
    )

    confidence = models.FloatField(
        default=0,
        help_text='원인 분류 신뢰도 (0~1)'
    )

    # 상세 설명
    explanation = models.TextField(
        null=True,
        blank=True,
        help_text='원인에 대한 상세 설명'
    )

    # 추가 분석 데이터 (JSON)
    analysis_data = models.JSONField(
        null=True,
        blank=True,
        help_text='추가 분석 메트릭 (capacity_ratio, avg_priority 등)'
    )

    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'aps'
        db_table = "unplanned_reason"
        ordering = ['-created_at', 'scenario', 'reason_code']
        indexes = [
            models.Index(fields=['scenario', 'reason_code'], name='ix_unplanned_scenario_code'),
            models.Index(fields=['wo_no', 'created_at'], name='ix_unplanned_wo_ts'),
            models.Index(fields=['status', 'reason_code'], name='ix_unplanned_status_code'),
        ]
        verbose_name = '미계획 원인'
        verbose_name_plural = '미계획 원인 분석'

    def __str__(self):
        return f"{self.wo_no} - {self.get_reason_code_display()} ({self.status})"

    @property
    def risk_level(self):
        """위험 수준 평가"""
        if self.delay_hours > 24:
            return 'HIGH'
        elif self.delay_hours > 8:
            return 'MEDIUM'
        elif self.status == 'UNPLANNED':
            return 'MEDIUM'
        else:
            return 'LOW'

    def get_recommendation(self):
        """원인별 권장 조치"""
        recommendations = {
            'CAPACITY_SHORTAGE': '추가 자원 확보, 작업 시간 연장, 아웃소싱 검토',
            'CALENDAR_CONFLICT': '근무 시간 조정, 휴일 근무 계획, 일정 재조정',
            'PRIORITY_LOSS': '우선순위 재조정, 긴급 작업으로 전환, 납기일 협의',
            'DATA_MISSING': 'Routing/Operation 데이터 보완, 자원 정보 업데이트',
        }
        return recommendations.get(self.reason_code, '데이터 검토 필요')
