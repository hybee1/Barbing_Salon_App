from django.contrib import admin

from backend.services.models import Service, Hairstyle, Color


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """
    Controls how the Service model appears inside the Django Admin.
    """

    list_display = ( "id", "name", "image", "duration_minutes", "price", "description",
                     "is_active", )

    search_fields = ( "name", "price", "duration_minutes", "is_active",)

    list_filter = ( "price", "is_active", )

    ordering = ( "price", )


@admin.register(Hairstyle)
class HairstyleAdmin(admin.ModelAdmin):
    """
    Controls how the Hairstyle model appears inside the Django Admin.
    """

    list_display = ( "id", "service__name", "name",
                     "image", "price", "duration_minutes",
                     "description",  "is_active", )

    search_fields = ( "name", "price", "duration_minutes", "is_active",)

    list_filter = ( "name", "is_active", )

    ordering = ( "name", )


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    """
    Controls how the Color model appears inside the Django Admin.
    """

    list_display = ("id", "service__name", "name", "description", "duration_minutes", "is_active",)

    search_fields = ("name", "is_active",)

    list_filter = ("name", "is_active",)

    ordering = ("name",)
