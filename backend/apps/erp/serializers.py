"""
ERP Integration Serializers
"""
from rest_framework import serializers
from .models import (
    MasterItem,
    MasterMachine,
    MasterWorkCenter,
    MasterBOM,
    MasterRouting,
    ERPWorkOrder,
    ERPSyncLog,
)


class MasterItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterItem
        fields = "__all__"


class MasterMachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterMachine
        fields = "__all__"


class MasterWorkCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterWorkCenter
        fields = "__all__"


class MasterBOMSerializer(serializers.ModelSerializer):
    parent_item_id = serializers.CharField(source="parent_item.itm_id", read_only=True)
    child_item_id = serializers.CharField(source="child_item.itm_id", read_only=True)

    class Meta:
        model = MasterBOM
        fields = "__all__"


class MasterRoutingSerializer(serializers.ModelSerializer):
    item_id = serializers.CharField(source="item.itm_id", read_only=True)
    wc_cd = serializers.CharField(source="workcenter.wc_cd", read_only=True)

    class Meta:
        model = MasterRouting
        fields = "__all__"


class ERPWorkOrderSerializer(serializers.ModelSerializer):
    item_id = serializers.CharField(source="item.itm_id", read_only=True)
    item_nm = serializers.CharField(source="item.itm_nm", read_only=True)

    class Meta:
        model = ERPWorkOrder
        fields = "__all__"


class ERPSyncLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ERPSyncLog
        fields = "__all__"


class ERPDataImportSerializer(serializers.Serializer):
    """ERP 데이터 일괄 Import"""

    sync_type = serializers.ChoiceField(
        choices=["ITEM", "MACHINE", "WORKCENTER", "BOM", "ROUTING", "WORKORDER"]
    )
    data = serializers.ListField(child=serializers.DictField())
    overwrite = serializers.BooleanField(default=False)
