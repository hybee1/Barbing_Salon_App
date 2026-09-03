
# ==========================================================
# inventory_serializers.py
# Levelz Cuts - Inventory Serializers
# ==========================================================

from rest_framework import serializers

from .models import (
    InventoryCategory,
    InventoryItem,
    InventoryTransaction,
    EquipmentProfile,
)


# ==========================================================
# INVENTORY CATEGORY
# ==========================================================

class InventoryCategorySerializer(
    serializers.ModelSerializer
):

    item_count = serializers.SerializerMethodField()

    class Meta:

        model = InventoryCategory

        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "item_count",
        ]

        read_only_fields = [
            "id",
            "item_count",
        ]

    def get_item_count(self, obj):

        return obj.items.count()



# class InventoryCategorySerializer(serializers.ModelSerializer):
#
#     item_count = serializers.IntegerField(
#         source="items.count",
#         read_only=True
#     )
#
#     class Meta:
#
#         model = InventoryCategory
#
#         fields = [
#             "id",
#             "name",
#             "description",
#             "is_active",
#             "item_count",
#         ]
#
#         read_only_fields = [
#             "id",
#             "item_count",
#         ]


# ==========================================================
# INVENTORY ITEM
# ==========================================================

class InventoryItemSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    item_type_display = serializers.CharField(
        source="get_item_type_display",
        read_only=True
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True
    )

    stock_value = serializers.SerializerMethodField()

    is_low_stock = serializers.SerializerMethodField()

    class Meta:

        model = InventoryItem

        fields = [
            "id",
            "name",
            "category",
            "category_name",
            "item_type",
            "item_type_display",
            "description",
            "quantity",
            "unit",
            "reorder_level",
            "cost_per_unit",
            "stock_value",
            "is_low_stock",
            "supplier",
            "purchase_date",
            "expiry_date",
            "storage_location",
            "status",
            "status_display",
            "notes",
        ]

        read_only_fields = [
            "id",
            "category_name",
            "item_type_display",
            "status_display",
            "stock_value",
            "is_low_stock",
        ]

    def get_stock_value(self, obj):

        return obj.quantity * obj.cost_per_unit

    def get_is_low_stock(self, obj):

        return (
            obj.status == InventoryItem.Status.ACTIVE
            and obj.quantity <= obj.reorder_level
        )

    def validate(self, attrs):

        quantity = attrs.get(
            "quantity",
            getattr(self.instance, "quantity", 0)
        )

        reorder_level = attrs.get(
            "reorder_level",
            getattr(self.instance, "reorder_level", 0)
        )

        cost_per_unit = attrs.get(
            "cost_per_unit",
            getattr(self.instance, "cost_per_unit", 0)
        )

        if quantity < 0:

            raise serializers.ValidationError({
                "quantity": "Quantity cannot be negative."
            })

        if reorder_level < 0:

            raise serializers.ValidationError({
                "reorder_level": "Reorder level cannot be negative."
            })

        if cost_per_unit < 0:

            raise serializers.ValidationError({
                "cost_per_unit": "Cost per unit cannot be negative."
            })

        expiry_date = attrs.get(
            "expiry_date",
            getattr(self.instance, "expiry_date", None)
        )

        purchase_date = attrs.get(
            "purchase_date",
            getattr(self.instance, "purchase_date", None)
        )

        if purchase_date and expiry_date:

            if expiry_date < purchase_date:

                raise serializers.ValidationError({
                    "expiry_date":
                        "Expiry date cannot be before purchase date."
                })

        return attrs


# ==========================================================
# INVENTORY TRANSACTION
# ==========================================================

class InventoryTransactionSerializer(serializers.ModelSerializer):

    item_name = serializers.CharField(
        source="item.name",
        read_only=True
    )

    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display",
        read_only=True
    )

    reason_display = serializers.CharField(
        source="get_reason_display",
        read_only=True
    )

    performed_by_name = serializers.SerializerMethodField()

    class Meta:

        model = InventoryTransaction

        fields = [
            "id",
            "item",
            "item_name",
            "transaction_type",
            "transaction_type_display",
            "quantity",
            "unit_cost",
            "reason",
            "reason_display",
            "supplier",
            "reference_number",
            "transaction_date",
            "performed_by",
            "performed_by_name",
            "notes",
        ]

        read_only_fields = [
            "id",
            "performed_by",
            "performed_by_name",
            "transaction_date",
        ]

    def get_performed_by_name(self, obj):

        user = obj.performed_by

        return (
            user.get_full_name()
            or user.username
        )

    def validate(self, attrs):

        quantity = attrs.get("quantity")

        if quantity is not None and quantity <= 0:

            raise serializers.ValidationError({
                "quantity":
                    "Transaction quantity must be greater than zero."
            })

        transaction_type = attrs.get("transaction_type")

        reason = attrs.get("reason", "")

        if (
            transaction_type
            == InventoryTransaction.TransactionType.STOCK_OUT
            and not reason
        ):

            raise serializers.ValidationError({
                "reason":
                    "A reason is required for stock-out transactions."
            })

        return attrs


# ==========================================================
# EQUIPMENT PROFILE
# ==========================================================

class EquipmentProfileSerializer(serializers.ModelSerializer):

    item_name = serializers.CharField(
        source="item.name",
        read_only=True
    )

    assigned_staff_name = serializers.SerializerMethodField()

    class Meta:

        model = EquipmentProfile

        fields = [
            "id",
            "item",
            "item_name",
            "serial_number",
            "condition",
            "purchase_price",
            "warranty_information",
            "assigned_staff",
            "assigned_staff_name",
            "maintenance_status",
            "next_maintenance_date",
        ]

        read_only_fields = [
            "id",
            "item_name",
            "assigned_staff_name",
        ]

    def get_assigned_staff_name(self, obj):

        if not obj.assigned_staff:
            return None

        return (
            obj.assigned_staff.get_full_name()
            or obj.assigned_staff.username
        )
