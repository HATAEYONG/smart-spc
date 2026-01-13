"""
APS 기본정보 확장 모델 - 캘린더 및 가동 시간
Phase 1: 긴급 조치
"""
from django.db import models


class PlantCalendar(models.Model):
    """
    공장 캘린더

    평일/주말/휴일 구분 및 가동 시간 관리
    APS 스케줄링 시 근무일 기준으로 작업 할당
    """
    calendar_id = models.AutoField(primary_key=True)
    work_date = models.DateField(verbose_name="일자", db_index=True)
    plant_cd = models.CharField(max_length=20, verbose_name="공장코드")

    day_type = models.CharField(
        max_length=20,
        choices=[
            ('WORK', '근무일'),
            ('HOLIDAY', '휴일'),
            ('HALF_DAY', '반일근무'),
            ('OVERTIME', '특근'),
        ],
        default='WORK',
        verbose_name="일자구분"
    )

    work_start_time = models.TimeField(default='08:00:00', verbose_name="근무시작시간")
    work_end_time = models.TimeField(default='17:00:00', verbose_name="근무종료시간")
    break_start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="휴게시작시간"
    )
    break_end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="휴게종료시간"
    )

    is_available = models.BooleanField(default=True, verbose_name="가동가능여부")
    capacity_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.00,
        verbose_name="가동률(%)"
    )
    # 평일: 100%, 주말특근: 80%, 공휴일특근: 70%

    remarks = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="비고"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "plant_calendar"
        verbose_name = "공장캘린더"
        verbose_name_plural = "공장캘린더"
        unique_together = (("work_date", "plant_cd"),)
        indexes = [
            models.Index(fields=["work_date", "plant_cd"], name="ix_cal_date_plant"),
            models.Index(fields=["plant_cd", "day_type"], name="ix_cal_plant_type"),
        ]
        ordering = ["work_date"]

    def __str__(self):
        return f"{self.work_date} - {self.plant_cd} ({self.get_day_type_display()})"

    def get_work_hours(self):
        """근무 시간 계산 (시간 단위)"""
        if not self.is_available:
            return 0

        from datetime import datetime, timedelta

        start_dt = datetime.combine(datetime.today(), self.work_start_time)
        end_dt = datetime.combine(datetime.today(), self.work_end_time)

        # 종료시간이 시작시간보다 이르면 다음날로 처리 (야간 근무)
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)

        total_hours = (end_dt - start_dt).total_seconds() / 3600

        # 휴게시간 차감
        if self.break_start_time and self.break_end_time:
            break_start = datetime.combine(datetime.today(), self.break_start_time)
            break_end = datetime.combine(datetime.today(), self.break_end_time)
            if break_end <= break_start:
                break_end += timedelta(days=1)
            break_hours = (break_end - break_start).total_seconds() / 3600
            total_hours -= break_hours

        # 가동률 반영
        return total_hours * (float(self.capacity_rate) / 100)


class MachineWorkTime(models.Model):
    """
    설비별 가동 시간

    설비별로 가동 가능한 시간대 정의
    요일별 다른 가동 시간 설정 가능
    """
    work_time_id = models.AutoField(primary_key=True)
    machine = models.ForeignKey(
        'MasterMachine',
        on_delete=models.CASCADE,
        related_name='work_times',
        verbose_name="설비"
    )

    day_of_week = models.IntegerField(
        choices=[
            (0, '월요일'),
            (1, '화요일'),
            (2, '수요일'),
            (3, '목요일'),
            (4, '금요일'),
            (5, '토요일'),
            (6, '일요일'),
        ],
        verbose_name="요일"
    )

    start_time = models.TimeField(verbose_name="시작시간")
    end_time = models.TimeField(verbose_name="종료시간")

    is_available = models.BooleanField(default=True, verbose_name="가동가능")

    # 야간 근무 여부 (종료시간이 다음날인 경우)
    is_overnight = models.BooleanField(default=False, verbose_name="야간근무여부")

    remarks = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="비고"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "machine_work_time"
        verbose_name = "설비가동시간"
        verbose_name_plural = "설비가동시간"
        unique_together = (("machine", "day_of_week"),)
        indexes = [
            models.Index(fields=["machine", "day_of_week"], name="ix_mwt_mc_dow"),
        ]
        ordering = ["machine", "day_of_week"]

    def __str__(self):
        return f"{self.machine.mc_cd} - {self.get_day_of_week_display()} ({self.start_time}-{self.end_time})"

    def get_work_hours(self):
        """가동 시간 계산 (시간 단위)"""
        if not self.is_available:
            return 0

        from datetime import datetime, timedelta

        start_dt = datetime.combine(datetime.today(), self.start_time)
        end_dt = datetime.combine(datetime.today(), self.end_time)

        # 야간 근무인 경우
        if self.is_overnight or end_dt <= start_dt:
            end_dt += timedelta(days=1)

        total_hours = (end_dt - start_dt).total_seconds() / 3600
        return total_hours


class MachineDowntime(models.Model):
    """
    설비 다운타임 (정기 점검, 고장 등)

    특정 기간 동안 설비 사용 불가 일정
    """
    downtime_id = models.AutoField(primary_key=True)
    machine = models.ForeignKey(
        'MasterMachine',
        on_delete=models.CASCADE,
        related_name='downtimes',
        verbose_name="설비"
    )

    downtime_type = models.CharField(
        max_length=20,
        choices=[
            ('MAINTENANCE', '정기점검'),
            ('REPAIR', '고장수리'),
            ('SETUP', '셋업'),
            ('OTHER', '기타'),
        ],
        verbose_name="다운타임구분"
    )

    start_dt = models.DateTimeField(verbose_name="시작일시", db_index=True)
    end_dt = models.DateTimeField(verbose_name="종료일시", db_index=True)

    planned_yn = models.CharField(
        max_length=1,
        choices=[
            ('Y', '계획'),
            ('N', '비계획'),
        ],
        default='Y',
        verbose_name="계획여부"
    )

    description = models.TextField(null=True, blank=True, verbose_name="상세설명")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "machine_downtime"
        verbose_name = "설비다운타임"
        verbose_name_plural = "설비다운타임"
        indexes = [
            models.Index(fields=["machine", "start_dt"], name="ix_downtime_mc_start"),
            models.Index(fields=["start_dt", "end_dt"], name="ix_downtime_period"),
        ]
        ordering = ["start_dt"]

    def __str__(self):
        return f"{self.machine.mc_cd} - {self.get_downtime_type_display()} ({self.start_dt}~{self.end_dt})"

    def get_duration_hours(self):
        """다운타임 시간 계산 (시간 단위)"""
        duration = self.end_dt - self.start_dt
        return duration.total_seconds() / 3600
