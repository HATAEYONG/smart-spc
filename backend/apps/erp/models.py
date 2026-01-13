"""
ERP Integration Models
기본정보 그룹 - ERP 시스템 데이터 연계

Phase 1 (긴급): 공장 캘린더, 설비 가동시간, 재고 관리
Phase 2 (단기): 작업조, 작업자, 숙련도
"""
from django.db import models
from decimal import Decimal


class MasterItem(models.Model):
    """품목 마스터 (ERP 연계)"""
    itm_id = models.CharField(max_length=50, primary_key=True, verbose_name="품목코드")
    itm_nm = models.CharField(max_length=200, verbose_name="품목명")
    itm_type = models.CharField(max_length=20, verbose_name="품목구분")
    itm_family = models.CharField(max_length=50, null=True, blank=True, verbose_name="품목패밀리")
    std_cycle_time = models.IntegerField(default=60, verbose_name="표준CT(분)")
    unit = models.CharField(max_length=20, default="EA", verbose_name="단위")
    active_yn = models.CharField(max_length=1, default="Y", verbose_name="사용여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "master_item"
        verbose_name = "품목마스터"
        verbose_name_plural = "품목마스터"
        indexes = [
            models.Index(fields=["itm_family"], name="ix_item_family"),
        ]

    def __str__(self):
        return f"{self.itm_id} - {self.itm_nm}"


class MasterMachine(models.Model):
    """기계 마스터 (ERP 연계)"""
    mc_cd = models.CharField(max_length=20, primary_key=True, verbose_name="기계코드")
    mc_nm = models.CharField(max_length=200, verbose_name="기계명")
    wc_cd = models.CharField(max_length=20, verbose_name="작업장코드")
    mc_type = models.CharField(max_length=50, verbose_name="기계유형")
    capacity = models.IntegerField(default=1, verbose_name="생산능력")
    cost_per_hour = models.DecimalField(
        max_digits=10, decimal_places=2, default=100.00, verbose_name="시간당비용"
    )
    active_yn = models.CharField(max_length=1, default="Y", verbose_name="사용여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "master_machine"
        verbose_name = "기계마스터"
        verbose_name_plural = "기계마스터"
        indexes = [
            models.Index(fields=["wc_cd"], name="ix_machine_wc"),
        ]

    def __str__(self):
        return f"{self.mc_cd} - {self.mc_nm}"


class MasterWorkCenter(models.Model):
    """작업장 마스터 (ERP 연계)"""
    wc_cd = models.CharField(max_length=20, primary_key=True, verbose_name="작업장코드")
    wc_nm = models.CharField(max_length=200, verbose_name="작업장명")
    plant_cd = models.CharField(max_length=20, verbose_name="공장코드")
    active_yn = models.CharField(max_length=1, default="Y", verbose_name="사용여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "master_workcenter"
        verbose_name = "작업장마스터"
        verbose_name_plural = "작업장마스터"

    def __str__(self):
        return f"{self.wc_cd} - {self.wc_nm}"


class MasterBOM(models.Model):
    """BOM 마스터 (ERP 연계)"""
    parent_item = models.ForeignKey(
        MasterItem, on_delete=models.CASCADE, related_name="bom_children", verbose_name="모품목"
    )
    child_item = models.ForeignKey(
        MasterItem, on_delete=models.CASCADE, related_name="bom_parents", verbose_name="자품목"
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="소요량")
    seq = models.IntegerField(default=1, verbose_name="순번")
    active_yn = models.CharField(max_length=1, default="Y", verbose_name="사용여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "master_bom"
        verbose_name = "BOM"
        verbose_name_plural = "BOM"
        unique_together = (("parent_item", "child_item"),)

    def __str__(self):
        return f"{self.parent_item.itm_id} > {self.child_item.itm_id}"


class MasterRouting(models.Model):
    """라우팅 마스터 (ERP 연계)"""
    item = models.ForeignKey(MasterItem, on_delete=models.CASCADE, verbose_name="품목")
    seq = models.IntegerField(verbose_name="공정순서")
    workcenter = models.ForeignKey(MasterWorkCenter, on_delete=models.CASCADE, verbose_name="작업장")
    operation_nm = models.CharField(max_length=200, verbose_name="공정명")
    std_time = models.IntegerField(verbose_name="표준시간(분)")
    setup_time = models.IntegerField(default=0, verbose_name="준비시간(분)")
    active_yn = models.CharField(max_length=1, default="Y", verbose_name="사용여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "master_routing"
        verbose_name = "라우팅"
        verbose_name_plural = "라우팅"
        unique_together = (("item", "seq"),)
        ordering = ["item", "seq"]

    def __str__(self):
        return f"{self.item.itm_id} - {self.seq:02d} - {self.operation_nm}"


class ERPWorkOrder(models.Model):
    """작업지시 (ERP 연계)"""
    wo_no = models.CharField(max_length=30, primary_key=True, verbose_name="작업지시번호")
    item = models.ForeignKey(MasterItem, on_delete=models.CASCADE, verbose_name="품목")
    order_qty = models.DecimalField(max_digits=18, decimal_places=4, verbose_name="지시수량")
    due_date = models.DateTimeField(verbose_name="납기일")
    priority = models.IntegerField(default=5, verbose_name="우선순위(1-10)")
    status = models.CharField(
        max_length=20,
        choices=[
            ("CREATED", "생성"),
            ("RELEASED", "출고"),
            ("RUNNING", "진행중"),
            ("COMPLETED", "완료"),
            ("CANCELLED", "취소"),
        ],
        default="CREATED",
        verbose_name="상태",
    )
    plant_cd = models.CharField(max_length=20, verbose_name="공장코드")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    erp_sync_ts = models.DateTimeField(null=True, blank=True, verbose_name="ERP동기화시각")

    class Meta:
        db_table = "erp_workorder"
        verbose_name = "작업지시"
        verbose_name_plural = "작업지시"
        indexes = [
            models.Index(fields=["status", "due_date"], name="ix_wo_status_due"),
        ]

    def __str__(self):
        return f"{self.wo_no} - {self.item.itm_id}"


class ERPSyncLog(models.Model):
    """ERP 동기화 로그"""
    sync_id = models.AutoField(primary_key=True)
    sync_type = models.CharField(
        max_length=50,
        choices=[
            ("ITEM", "품목마스터"),
            ("MACHINE", "기계마스터"),
            ("WORKCENTER", "작업장마스터"),
            ("BOM", "BOM"),
            ("ROUTING", "라우팅"),
            ("WORKORDER", "작업지시"),
        ],
        verbose_name="동기화유형",
    )
    sync_status = models.CharField(
        max_length=20,
        choices=[("SUCCESS", "성공"), ("FAILED", "실패"), ("PARTIAL", "부분성공")],
        verbose_name="동기화상태",
    )
    records_total = models.IntegerField(default=0, verbose_name="총건수")
    records_success = models.IntegerField(default=0, verbose_name="성공건수")
    records_failed = models.IntegerField(default=0, verbose_name="실패건수")
    error_message = models.TextField(null=True, blank=True, verbose_name="오류메시지")
    sync_ts = models.DateTimeField(auto_now_add=True, verbose_name="동기화시각")

    class Meta:
        db_table = "erp_sync_log"
        verbose_name = "ERP동기화로그"
        verbose_name_plural = "ERP동기화로그"
        ordering = ["-sync_ts"]

    def __str__(self):
        return f"[{self.sync_type}] {self.sync_status} - {self.sync_ts}"


# ============================================================================
# Phase 1: 긴급 조치 - 공장 캘린더, 설비 가동시간, 재고 관리
# ============================================================================

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


class ItemInventory(models.Model):
    """
    품목 재고

    품목별 현재고 및 가용재고 관리
    APS 스케줄링 시 자재 가용성 체크
    """
    inventory_id = models.AutoField(primary_key=True)
    item = models.ForeignKey(
        'MasterItem',
        on_delete=models.CASCADE,
        related_name='inventories',
        verbose_name="품목"
    )
    plant_cd = models.CharField(max_length=20, verbose_name="공장코드")
    warehouse_cd = models.CharField(
        max_length=20,
        default='WH01',
        verbose_name="창고코드"
    )

    # 재고 수량
    on_hand_qty = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="현재고량"
    )
    allocated_qty = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="할당량"
    )
    available_qty = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="가용재고"
    )
    # available_qty = on_hand_qty - allocated_qty

    # 안전재고
    safety_stock = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="안전재고"
    )
    min_stock = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="최소재고"
    )
    max_stock = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="최대재고"
    )

    # 재주문 정보
    reorder_point = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="재주문점"
    )
    order_qty = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="발주량"
    )

    # 비용 정보
    unit_cost = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="단위원가"
    )
    inventory_value = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name="재고금액"
    )
    # inventory_value = on_hand_qty * unit_cost

    last_receipt_dt = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="최종입고일시"
    )
    last_issue_dt = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="최종출고일시"
    )

    updated_at = models.DateTimeField(auto_now=True, verbose_name="갱신일시")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "item_inventory"
        verbose_name = "품목재고"
        verbose_name_plural = "품목재고"
        unique_together = (("item", "plant_cd", "warehouse_cd"),)
        indexes = [
            models.Index(fields=["item", "plant_cd"], name="ix_inv_item_plant"),
            models.Index(fields=["plant_cd", "warehouse_cd"], name="ix_inv_plant_wh"),
        ]

    def __str__(self):
        return f"{self.item.itm_id} - {self.plant_cd}/{self.warehouse_cd} (현재고: {self.on_hand_qty})"

    def save(self, *args, **kwargs):
        """저장 시 자동 계산"""
        # 가용재고 = 현재고 - 할당량
        self.available_qty = self.on_hand_qty - self.allocated_qty

        # 재고금액 = 현재고 * 단위원가
        self.inventory_value = self.on_hand_qty * self.unit_cost

        super().save(*args, **kwargs)

    def is_available(self, required_qty):
        """필요 수량을 충족하는지 확인"""
        return self.available_qty >= required_qty

    def is_below_safety_stock(self):
        """안전재고 미달 여부"""
        return self.on_hand_qty < self.safety_stock

    def is_reorder_needed(self):
        """재주문 필요 여부"""
        return self.on_hand_qty <= self.reorder_point

    def allocate(self, qty):
        """재고 할당"""
        if self.available_qty >= qty:
            self.allocated_qty += qty
            self.save()
            return True
        return False

    def release_allocation(self, qty):
        """할당 해제"""
        self.allocated_qty = max(Decimal('0'), self.allocated_qty - qty)
        self.save()


class InventoryTransaction(models.Model):
    """
    재고 이동 이력

    입고, 출고, 이동 등 모든 재고 변동 기록
    """
    transaction_id = models.AutoField(primary_key=True)
    item = models.ForeignKey(
        'MasterItem',
        on_delete=models.CASCADE,
        verbose_name="품목"
    )
    plant_cd = models.CharField(max_length=20, verbose_name="공장코드")
    warehouse_cd = models.CharField(max_length=20, verbose_name="창고코드")

    transaction_type = models.CharField(
        max_length=20,
        choices=[
            ('RECEIPT', '입고'),
            ('ISSUE', '출고'),
            ('ADJUSTMENT', '조정'),
            ('TRANSFER', '이동'),
            ('RETURN', '반품'),
        ],
        verbose_name="거래유형"
    )

    transaction_dt = models.DateTimeField(auto_now_add=True, verbose_name="거래일시")

    quantity = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        verbose_name="수량"
    )
    # 양수: 입고, 음수: 출고

    unit_cost = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="단위원가"
    )

    # 연관 정보
    wo_no = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name="작업지시번호"
    )
    reference_no = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="참조번호"
    )

    remarks = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="비고"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inventory_transaction"
        verbose_name = "재고이동이력"
        verbose_name_plural = "재고이동이력"
        indexes = [
            models.Index(fields=["item", "transaction_dt"], name="ix_invtx_item_dt"),
            models.Index(fields=["plant_cd", "transaction_dt"], name="ix_invtx_plant_dt"),
            models.Index(fields=["wo_no"], name="ix_invtx_wo"),
        ]
        ordering = ["-transaction_dt"]

    def __str__(self):
        return f"{self.item.itm_id} - {self.get_transaction_type_display()} ({self.quantity})"


class MaterialRequirement(models.Model):
    """
    자재 소요량 (MRP 결과)

    작업지시별 필요 자재 및 소요 시점
    """
    requirement_id = models.AutoField(primary_key=True)
    wo_no = models.CharField(max_length=30, verbose_name="작업지시번호", db_index=True)
    item = models.ForeignKey(
        'MasterItem',
        on_delete=models.CASCADE,
        verbose_name="품목"
    )

    required_qty = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        verbose_name="소요량"
    )
    required_dt = models.DateTimeField(verbose_name="소요일시")

    # 충족 여부
    allocated_qty = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="할당량"
    )
    shortage_qty = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="부족량"
    )
    # shortage_qty = required_qty - allocated_qty

    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', '대기'),
            ('ALLOCATED', '할당완료'),
            ('SHORTAGE', '부족'),
            ('ISSUED', '출고완료'),
        ],
        default='PENDING',
        verbose_name="상태"
    )

    # 대체 품목
    alternative_item = models.ForeignKey(
        'MasterItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alternative_requirements',
        verbose_name="대체품목"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "material_requirement"
        verbose_name = "자재소요량"
        verbose_name_plural = "자재소요량"
        indexes = [
            models.Index(fields=["wo_no", "item"], name="ix_mrp_wo_item"),
            models.Index(fields=["required_dt"], name="ix_mrp_req_dt"),
            models.Index(fields=["status"], name="ix_mrp_status"),
        ]
        ordering = ["required_dt"]

    def __str__(self):
        return f"{self.wo_no} - {self.item.itm_id} (소요: {self.required_qty})"

    def save(self, *args, **kwargs):
        """저장 시 자동 계산"""
        self.shortage_qty = max(Decimal('0'), self.required_qty - self.allocated_qty)

        # 상태 자동 갱신
        if self.allocated_qty == 0:
            self.status = 'PENDING'
        elif self.shortage_qty > 0:
            self.status = 'SHORTAGE'
        else:
            self.status = 'ALLOCATED'

        super().save(*args, **kwargs)

    def check_availability(self):
        """재고 가용성 체크"""
        try:
            inventory = ItemInventory.objects.get(
                item=self.item,
                plant_cd='FAC01',  # TODO: 작업지시의 공장코드 사용
                warehouse_cd='WH01'
            )
            return inventory.is_available(self.required_qty)
        except ItemInventory.DoesNotExist:
            return False


# ============================================================================
# Phase 2: 단기 - 작업조, 작업자, 숙련도, 작업 할당
# ============================================================================

class MasterShift(models.Model):
    """
    작업조 마스터

    주간/야간, A조/B조/C조 등 교대 근무 관리
    """
    shift_cd = models.CharField(max_length=20, primary_key=True, verbose_name="작업조코드")
    shift_nm = models.CharField(max_length=200, verbose_name="작업조명")

    shift_type = models.CharField(
        max_length=20,
        choices=[
            ('DAY', '주간'),
            ('NIGHT', '야간'),
            ('SWING', '교대'),
        ],
        verbose_name="작업조구분"
    )

    start_time = models.TimeField(verbose_name="시작시간")
    end_time = models.TimeField(verbose_name="종료시간")
    break_time = models.IntegerField(default=60, verbose_name="휴게시간(분)")

    # 야간 근무 여부 (종료시간이 다음날인 경우)
    is_overnight = models.BooleanField(default=False, verbose_name="야간근무여부")

    active_yn = models.CharField(max_length=1, default="Y", verbose_name="사용여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "master_shift"
        verbose_name = "작업조마스터"
        verbose_name_plural = "작업조마스터"

    def __str__(self):
        return f"{self.shift_cd} - {self.shift_nm} ({self.get_shift_type_display()})"

    def get_work_hours(self):
        """근무 시간 계산 (시간 단위)"""
        from datetime import datetime, timedelta

        start_dt = datetime.combine(datetime.today(), self.start_time)
        end_dt = datetime.combine(datetime.today(), self.end_time)

        # 야간 근무인 경우
        if self.is_overnight or end_dt <= start_dt:
            end_dt += timedelta(days=1)

        total_minutes = (end_dt - start_dt).total_seconds() / 60
        total_minutes -= self.break_time

        return total_minutes / 60


class MasterWorker(models.Model):
    """
    작업자 마스터

    작업자 기본 정보 및 소속 관리
    """
    worker_cd = models.CharField(max_length=20, primary_key=True, verbose_name="작업자코드")
    worker_nm = models.CharField(max_length=200, verbose_name="작업자명")

    workcenter = models.ForeignKey(
        'MasterWorkCenter',
        on_delete=models.CASCADE,
        related_name='workers',
        verbose_name="소속작업장"
    )

    shift = models.ForeignKey(
        MasterShift,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workers',
        verbose_name="소속작업조"
    )

    worker_type = models.CharField(
        max_length=20,
        choices=[
            ('REGULAR', '정규직'),
            ('CONTRACT', '계약직'),
            ('TEMP', '임시직'),
            ('DISPATCH', '파견직'),
        ],
        default='REGULAR',
        verbose_name="작업자구분"
    )

    # 경력 정보
    hire_date = models.DateField(null=True, blank=True, verbose_name="입사일")
    experience_years = models.IntegerField(default=0, verbose_name="경력(년)")

    # 비용 정보
    cost_per_hour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('20000.00'),
        verbose_name="시간당인건비"
    )

    # 연락처
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="연락처"
    )
    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name="이메일"
    )

    active_yn = models.CharField(max_length=1, default="Y", verbose_name="사용여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "master_worker"
        verbose_name = "작업자마스터"
        verbose_name_plural = "작업자마스터"
        indexes = [
            models.Index(fields=["workcenter"], name="ix_worker_wc"),
            models.Index(fields=["shift"], name="ix_worker_shift"),
        ]

    def __str__(self):
        return f"{self.worker_cd} - {self.worker_nm} ({self.workcenter.wc_nm})"


class WorkerSkill(models.Model):
    """
    작업자 숙련도

    작업자별 공정별 숙련도 및 작업 효율
    """
    skill_id = models.AutoField(primary_key=True)

    worker = models.ForeignKey(
        MasterWorker,
        on_delete=models.CASCADE,
        related_name='skills',
        verbose_name="작업자"
    )

    operation_nm = models.CharField(max_length=200, verbose_name="공정명")

    skill_level = models.IntegerField(
        choices=[
            (1, '초급'),
            (2, '중급'),
            (3, '고급'),
            (4, '숙련'),
            (5, '전문가'),
        ],
        verbose_name="숙련도"
    )

    efficiency_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('100.00'),
        verbose_name="작업효율(%)"
    )
    # 초급(1): 70%, 중급(2): 85%, 고급(3): 100%, 숙련(4): 115%, 전문가(5): 130%

    # 자격증 정보
    certified_yn = models.CharField(max_length=1, default="N", verbose_name="자격증보유")
    certification_nm = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="자격증명"
    )
    certification_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="자격취득일"
    )

    # 교육 이수 정보
    training_hours = models.IntegerField(default=0, verbose_name="교육시간(시간)")
    last_training_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="최종교육일"
    )

    active_yn = models.CharField(max_length=1, default="Y", verbose_name="사용여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "worker_skill"
        verbose_name = "작업자숙련도"
        verbose_name_plural = "작업자숙련도"
        unique_together = (("worker", "operation_nm"),)
        indexes = [
            models.Index(fields=["operation_nm", "skill_level"], name="ix_skill_op_level"),
            models.Index(fields=["worker", "skill_level"], name="ix_skill_worker_level"),
        ]

    def __str__(self):
        return f"{self.worker.worker_nm} - {self.operation_nm} (Lv.{self.skill_level})"

    def save(self, *args, **kwargs):
        """저장 시 숙련도에 따른 효율 자동 설정"""
        if not self.efficiency_rate or self.efficiency_rate == 100:
            # 숙련도별 기본 효율
            efficiency_map = {
                1: Decimal('70.00'),   # 초급
                2: Decimal('85.00'),   # 중급
                3: Decimal('100.00'),  # 고급
                4: Decimal('115.00'),  # 숙련
                5: Decimal('130.00'),  # 전문가
            }
            self.efficiency_rate = efficiency_map.get(self.skill_level, Decimal('100.00'))

        super().save(*args, **kwargs)


class WorkAssignment(models.Model):
    """
    작업 할당

    작업지시에 작업자/작업조 할당 및 실적 관리
    """
    assignment_id = models.AutoField(primary_key=True)

    wo_no = models.CharField(max_length=30, verbose_name="작업지시번호", db_index=True)
    operation_seq = models.IntegerField(verbose_name="공정순서")
    operation_nm = models.CharField(max_length=200, verbose_name="공정명")

    worker = models.ForeignKey(
        MasterWorker,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name="담당작업자"
    )

    shift = models.ForeignKey(
        MasterShift,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name="작업조"
    )

    # 계획 시간
    assigned_start_dt = models.DateTimeField(verbose_name="할당시작시간")
    assigned_end_dt = models.DateTimeField(verbose_name="할당종료시간")
    assigned_duration = models.IntegerField(verbose_name="할당시간(분)")

    # 실제 시간
    actual_start_dt = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="실제시작시간"
    )
    actual_end_dt = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="실제종료시간"
    )
    actual_duration = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="실제시간(분)"
    )

    # 생산량
    target_qty = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="목표수량"
    )
    actual_qty = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="실제수량"
    )
    good_qty = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="양품수량"
    )
    defect_qty = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="불량수량"
    )

    # 상태
    status = models.CharField(
        max_length=20,
        choices=[
            ('ASSIGNED', '할당'),
            ('STARTED', '시작'),
            ('PAUSED', '일시중지'),
            ('COMPLETED', '완료'),
            ('CANCELLED', '취소'),
        ],
        default='ASSIGNED',
        verbose_name="상태"
    )

    # 비고
    remarks = models.TextField(null=True, blank=True, verbose_name="비고")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "work_assignment"
        verbose_name = "작업할당"
        verbose_name_plural = "작업할당"
        indexes = [
            models.Index(fields=["wo_no", "operation_seq"], name="ix_assign_wo_seq"),
            models.Index(fields=["worker", "assigned_start_dt"], name="ix_assign_worker_dt"),
            models.Index(fields=["shift", "assigned_start_dt"], name="ix_assign_shift_dt"),
            models.Index(fields=["status"], name="ix_assign_status"),
        ]
        ordering = ["assigned_start_dt"]

    def __str__(self):
        return f"{self.wo_no}-{self.operation_seq} → {self.worker.worker_nm} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """저장 시 자동 계산"""
        # 할당 시간 계산
        if self.assigned_start_dt and self.assigned_end_dt:
            duration = (self.assigned_end_dt - self.assigned_start_dt).total_seconds() / 60
            self.assigned_duration = int(duration)

        # 실제 시간 계산
        if self.actual_start_dt and self.actual_end_dt:
            duration = (self.actual_end_dt - self.actual_start_dt).total_seconds() / 60
            self.actual_duration = int(duration)

        super().save(*args, **kwargs)

    def start_work(self):
        """작업 시작"""
        from django.utils import timezone
        self.status = 'STARTED'
        self.actual_start_dt = timezone.now()
        self.save()

    def complete_work(self, good_qty, defect_qty=0):
        """작업 완료"""
        from django.utils import timezone
        self.status = 'COMPLETED'
        self.actual_end_dt = timezone.now()
        self.good_qty = good_qty
        self.defect_qty = defect_qty
        self.actual_qty = good_qty + defect_qty
        self.save()


# ============================================================================
# Phase 4-6: Setup Time, Batch 최적화 (CP-SAT Repair Engine 확장)
# ============================================================================
from .models_setup import ItemSetupTime, ItemFamily, BatchConfig
