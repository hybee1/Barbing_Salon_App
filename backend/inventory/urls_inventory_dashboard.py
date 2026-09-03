
# ==========================================================
# urls_inventory_dashboard.py
# Levelz Cuts - Inventory URLs
# ==========================================================

from django.urls import path

from .views import (
    InventoryItemListCreateAPIView,
    InventoryItemDetailAPIView,
    InventoryItemSummaryAPIView,
    InventoryStockInAPIView,
    InventoryStockOutAPIView,
)


urlpatterns = [

    # ------------------------------------------------------
    # INVENTORY ITEMS
    # ------------------------------------------------------

    path(
        "items/",
        InventoryItemListCreateAPIView.as_view(),
        name="inventory-items"
    ),

    path(
        "items/<int:pk>/",
        InventoryItemDetailAPIView.as_view(),
        name="inventory-item-detail"
    ),

    # ------------------------------------------------------
    # INVENTORY SUMMARY
    # ------------------------------------------------------

    path(
        "items/summary/",
        InventoryItemSummaryAPIView.as_view(),
        name="inventory-item-summary"
    ),

    # ------------------------------------------------------
    # STOCK MOVEMENTS
    # ------------------------------------------------------

    path(
        "items/<int:pk>/stock-in/",
        InventoryStockInAPIView.as_view(),
        name="inventory-stock-in"
    ),

    path(
        "items/<int:pk>/stock-out/",
        InventoryStockOutAPIView.as_view(),
        name="inventory-stock-out"
    ),

]
