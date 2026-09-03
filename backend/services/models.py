from django.db import models

from backend.salon_settings.models import TimeStampedModel


# --------------------
# SERVICES
# --------------------

class Service(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="services_image/", blank=True, null=True)
    price = models.DecimalField(max_digits = 10, decimal_places = 2)
    duration_minutes = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

        verbose_name = "Service"

        verbose_name_plural = "Services"

    def __str__(self):
        return self.name

'''
Example records:

Haircut
Beard Trim
Hair Dye
Hair Wash
Hair Treatment
Carving (Hair Design)
Home Service
'''


# --------------------
# HAIRSTYLES
# --------------------

class Hairstyle(TimeStampedModel):
    """
        Hairstyles belonging to a service.
        """

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="hairstyles")

    name = models.CharField(max_length=100, unique=True)

    image = models.ImageField(upload_to="hairstyles_image/", blank=True, null=True)

    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    duration_minutes = models.PositiveIntegerField(default=10)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("service", "name",)
        verbose_name = "Hairstyle"
        verbose_name_plural = "Hairstyles"

    def __str__(self):
        return f"{self.name}"


# --------------------
# HAIR OR BEARD-TINT COLOR
# --------------------

class Color(TimeStampedModel):
    """
        Color belonging to a service.
        """

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="colors")

    name = models.CharField(max_length=10, unique=True)

    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    duration_minutes = models.PositiveIntegerField(default=5)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("service", "name",)
        verbose_name = "Color"
        verbose_name_plural = "Colors"

    def __str__(self):
        return f"{self.name}"

