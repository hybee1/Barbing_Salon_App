from django.db import models
from django.utils import timezone

from core_config import settings_base


# ----------------------
# Inventory models
# ---------------------
class InventoryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)


class InventoryItem(models.Model):
    class ItemType(models.TextChoices):
        EQUIPMENT = "equipment", "Equipment"
        CONSUMABLE = "consumable", "Consumable"
        SUPPLY = "supply", "Supply"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        DISCONTINUED = "discontinued", "Discontinued"

    name = models.CharField(max_length=150)

    category = models.ForeignKey(
        InventoryCategory,
        on_delete=models.PROTECT,
        related_name="items"
    )

    item_type = models.CharField(
        max_length=20,
        choices=ItemType.choices
    )

    description = models.TextField(blank=True)

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    unit = models.CharField(
        max_length=30,
        default="unit"
    )

    reorder_level = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    cost_per_unit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    supplier = models.CharField(
        max_length=150,
        blank=True
    )

    purchase_date = models.DateField(
        null=True,
        blank=True
    )

    expiry_date = models.DateField(
        null=True,
        blank=True
    )

    storage_location = models.CharField(
        max_length=150,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    notes = models.TextField(blank=True)


# ----------------------
# InventoryTransaction models
# ---------------------
class InventoryTransaction(models.Model):

    class TransactionType(models.TextChoices):
        STOCK_IN = "stock_in", "Stock In"
        STOCK_OUT = "stock_out", "Stock Out"
        ADJUSTMENT = "adjustment", "Adjustment"
        TRANSFER = "transfer", "Transfer"

    class StockOutReason(models.TextChoices):
        CONSUMED = "consumed", "Consumed"
        DAMAGED = "damaged", "Damaged"
        EXPIRED = "expired", "Expired"
        TRANSFERRED = "transferred", "Transferred"
        OTHER = "other", "Other"

    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.PROTECT,
        related_name="transactions"
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices
    )

    quantity = models.PositiveIntegerField()

    unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    reason = models.CharField(
        max_length=30,
        choices=StockOutReason.choices,
        blank=True
    )

    supplier = models.CharField(
        max_length=150,
        blank=True
    )

    reference_number = models.CharField(
        max_length=100,
        blank=True
    )

    transaction_date = models.DateTimeField(
        default=timezone.localtime
    )

    performed_by = models.ForeignKey( settings_base.AUTH_USER_MODEL, on_delete=models.PROTECT )

    notes = models.TextField(blank=True)



# ----------------------
# Equipment models
# ---------------------
class EquipmentProfile(models.Model):
    item = models.OneToOneField(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name="equipment_profile"
    )

    serial_number = models.CharField(
        max_length=150,
        blank=True
    )

    condition = models.CharField(
        max_length=100,
        blank=True
    )

    purchase_price = models.DecimalField( max_digits=12, decimal_places=2, null=True, blank=True )

    warranty_information = models.TextField(
        blank=True
    )

    assigned_staff = models.ForeignKey( settings_base.AUTH_USER_MODEL, null=True, blank=True,
                                        on_delete=models.SET_NULL )

    maintenance_status = models.CharField( max_length=100, blank=True )

    next_maintenance_date = models.DateField( null=True,  blank=True )