from django.contrib import admin

from backend.breakperiods.models import BreakTimeAndOffDays


@admin.register(BreakTimeAndOffDays)
class BreakTimeAndOffDays(admin.ModelAdmin):
    """
    Controls how the User model appears inside the Django Admin.
    """

    list_display = (
                     # "staff__user__first_name", "staff__user__last_name",
                     "staff__user__username",
                     # "staff__user__email",
                     "staff__department",
                     # "staff__user__phone_number",
                     # "staff__user__role", "staff__user__image", "staff__user__is_active",
                     # "is_staff",  "is_superuser",
                     # "staff__user__last_login", "staff__user__date_joined",
                     "date", "start_time", "end_time", "status", "reason"
                     )

    search_fields = ( "staff__user__username",
                      # "staff__user__phone_number", "staff__user__email",
                      "staff__department",
                      "date", "start_time", "end_time", "status",
                      )

    list_filter = ( "staff__department", "status",)

    ordering = ( "date", )

    @admin.display(ordering="staff__user__username")
    def username(self, obj):
        return obj.user.username

    # @admin.display(ordering="staff__user__first_name")
    # def first_name(self, obj):
    #     return obj.user.first_name
    #
    # @admin.display(ordering="staff__user__last_name")
    # def last_name(self, obj):
    #     return obj.user.last_name
    #
    # @admin.display(ordering="staff__user__email")
    # def email(self, obj):
    #     return obj.user.email

    @admin.display(ordering="staff__department")
    def email(self, obj):
        return obj.user.email

    # @admin.display(ordering="staff__user__phone_number")
    # def phone_number(self, obj):
    #     return obj.user.phone_number
    #
    # @admin.display(ordering="staff__user__role")
    # def role(self, obj):
    #     return obj.role
    #
    # @admin.display(ordering="staff__user__image")
    # def photo_url(self, obj):
    #     return obj.user.image.url if obj.user.image else None

    # @admin.display(ordering="staff__user__date_joined")
    # def date_joined(self, obj):
    #     return obj.user.date_joined

    # @admin.display(boolean=True, ordering="staff__user__is_active")
    # def is_active(self, obj):
    #     return obj.user.is_active
