"""
APS 기본정보 확장 모델 - 재고 관리
Phase 1: 긴급 조치
"""
from django.db import models
from decimal import Decimal


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
