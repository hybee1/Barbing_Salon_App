from django.shortcuts import render


# ==========================================================
# inventory_views.py
# Levelz Cuts - Inventory Management
# ==========================================================

from decimal import Decimal

from django.db import transaction
from django.db.models import F, Sum, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import (
    InventoryCategory,
    InventoryItem,
    InventoryTransaction,
    EquipmentProfile,
)

from .serializers import (
    InventoryCategorySerializer,
    InventoryItemSerializer,
    InventoryTransactionSerializer,
    EquipmentProfileSerializer,
)
from ..custom_permissions.permissions import Is_Authenticated_Staff_User, Is_SalonManager


# ----------------------------------------------------------
# IMPORTANT:
# Replace this with your EXISTING custom permission.
# ----------------------------------------------------------




# ==========================================================
# INVENTORY ITEMS
# ==========================================================

class InventoryItemListCreateAPIView(APIView):

    permission_classes = [Is_SalonManager]

    def get(self, request):

        queryset = (
            InventoryItem.objects
            .select_related("category")
            .all()
            .order_by("name")
        )

        serializer = InventoryItemSerializer(
            queryset,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):

        serializer = InventoryItemSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        item = serializer.save()

        return Response(
            InventoryItemSerializer(item).data,
            status=status.HTTP_201_CREATED
        )


# ==========================================================
# INVENTORY ITEM DETAIL
# ==========================================================

class InventoryItemDetailAPIView(APIView):

    permission_classes = [Is_SalonManager]

    def get_object(self, pk):

        return (
            InventoryItem.objects
            .select_related("category")
            .filter(pk=pk)
            .first()
        )

    def get(self, request, pk):

        item = self.get_object(pk)

        if not item:

            return Response(
                {
                    "detail":
                        "Inventory item not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = InventoryItemSerializer(item)

        return Response(serializer.data)

    def put(self, request, pk):

        item = self.get_object(pk)

        if not item:

            return Response(
                {
                    "detail":
                        "Inventory item not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = InventoryItemSerializer(
            item,
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        item = serializer.save()

        return Response(
            InventoryItemSerializer(item).data
        )

    def patch(self, request, pk):

        item = self.get_object(pk)

        if not item:

            return Response(
                {
                    "detail":
                        "Inventory item not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = InventoryItemSerializer(
            item,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        item = serializer.save()

        return Response(
            InventoryItemSerializer(item).data
        )

    def delete(self, request, pk):

        item = self.get_object(pk)

        if not item:

            return Response(
                {
                    "detail":
                        "Inventory item not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        item.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


# ==========================================================
# INVENTORY SUMMARY
# ==========================================================

class InventoryItemSummaryAPIView(APIView):

    permission_classes = [Is_SalonManager]

    def get(self, request):

        active_items = InventoryItem.objects.filter(
            status=InventoryItem.Status.ACTIVE
        )

        low_stock_items = active_items.filter(
            quantity__lte=F("reorder_level")
        )

        total_stock_value = (
            active_items
            .annotate(
                item_value=ExpressionWrapper(
                    F("quantity") * F("cost_per_unit"),
                    output_field=DecimalField(
                        max_digits=20,
                        decimal_places=2
                    )
                )
            )
            .aggregate(
                total=Coalesce(
                    Sum("item_value"),
                    Decimal("0.00")
                )
            )
            ["total"]
        )

        return Response({

            "total_items":
                active_items.count(),

            "low_stock_items":
                low_stock_items.count(),

            "total_stock_value":
                total_stock_value,

        })


# ==========================================================
# STOCK IN
# ==========================================================

class InventoryStockInAPIView(APIView):

    permission_classes = [Is_SalonManager]

    @transaction.atomic
    def post(self, request, pk):

        item = (
            InventoryItem.objects
            .select_for_update()
            .filter(pk=pk)
            .first()
        )

        if not item:

            return Response(
                {
                    "detail":
                        "Inventory item not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        quantity = request.data.get(
            "quantity"
        )

        if quantity is None:

            return Response(
                {
                    "quantity":
                        "This field is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            quantity = Decimal(
                str(quantity)
            )

        except Exception:

            return Response(
                {
                    "quantity":
                        "Enter a valid number."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity <= 0:

            return Response(
                {
                    "quantity":
                        "Quantity must be greater than zero."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        unit_cost = request.data.get(
            "unit_cost"
        )

        if unit_cost is None:

            unit_cost = item.cost_per_unit

        else:

            try:

                unit_cost = Decimal(
                    str(unit_cost)
                )

            except Exception:

                return Response(
                    {
                        "unit_cost":
                            "Enter a valid number."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        if unit_cost < 0:

            return Response(
                {
                    "unit_cost":
                        "Unit cost cannot be negative."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        old_quantity = item.quantity

        item.quantity = (
            item.quantity + quantity
        )

        # If a new purchase cost is supplied,
        # use it as the current item cost.
        if unit_cost is not None:

            item.cost_per_unit = unit_cost

        item.save(
            update_fields=[
                "quantity",
                "cost_per_unit",
            ]
        )

        transaction_record = (
            InventoryTransaction.objects.create(

                item=item,

                transaction_type=
                    InventoryTransaction
                    .TransactionType
                    .STOCK_IN,

                quantity=quantity,

                unit_cost=unit_cost,

                supplier=request.data.get(
                    "supplier",
                    ""
                ),

                reference_number=request.data.get(
                    "reference_number",
                    ""
                ),

                performed_by=request.user,

                notes=request.data.get(
                    "notes",
                    ""
                ),

            )
        )

        return Response({

            "message":
                "Stock added successfully.",

            "item":
                InventoryItemSerializer(
                    item
                ).data,

            "transaction":
                InventoryTransactionSerializer(
                    transaction_record
                ).data,

            "previous_quantity":
                old_quantity,

            "new_quantity":
                item.quantity,

        })


# ==========================================================
# STOCK OUT
# ==========================================================

class InventoryStockOutAPIView(APIView):

    permission_classes = [Is_SalonManager]

    @transaction.atomic
    def post(self, request, pk):

        item = (
            InventoryItem.objects
            .select_for_update()
            .filter(pk=pk)
            .first()
        )

        if not item:

            return Response(
                {
                    "detail":
                        "Inventory item not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        quantity = request.data.get(
            "quantity"
        )

        if quantity is None:

            return Response(
                {
                    "quantity":
                        "This field is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            quantity = Decimal(
                str(quantity)
            )

        except Exception:

            return Response(
                {
                    "quantity":
                        "Enter a valid number."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity <= 0:

            return Response(
                {
                    "quantity":
                        "Quantity must be greater than zero."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity > item.quantity:

            return Response(
                {
                    "quantity":
                        "Stock-out quantity cannot exceed current stock."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        reason = request.data.get(
            "reason",
            ""
        )

        valid_reasons = dict(
            InventoryTransaction.StockOutReason.choices
        )

        if reason not in valid_reasons:

            return Response(
                {
                    "reason":
                        "Invalid stock-out reason."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        old_quantity = item.quantity

        item.quantity = (
            item.quantity - quantity
        )

        item.save(
            update_fields=[
                "quantity"
            ]
        )

        transaction_record = (
            InventoryTransaction.objects.create(

                item=item,

                transaction_type=
                    InventoryTransaction
                    .TransactionType
                    .STOCK_OUT,

                quantity=quantity,

                reason=reason,

                unit_cost=item.cost_per_unit,

                reference_number=request.data.get(
                    "reference_number",
                    ""
                ),

                performed_by=request.user,

                notes=request.data.get(
                    "notes",
                    ""
                ),

            )
        )

        return Response({

            "message":
                "Stock removed successfully.",

            "item":
                InventoryItemSerializer(
                    item
                ).data,

            "transaction":
                InventoryTransactionSerializer(
                    transaction_record
                ).data,

            "previous_quantity":
                old_quantity,

            "new_quantity":
                item.quantity,

        })
