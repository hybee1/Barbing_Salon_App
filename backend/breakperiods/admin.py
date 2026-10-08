from django.contrib import admin

from backend.breakperiods.models import BreakTimeAndOffDays


@admin.register(BreakTimeAndOffDays)
class BreakTimeAndOffDays(admin.ModelAdmin):
    """
    Controls how the User model appears inside the Django Admin.
    """

    list_display = (

                     "staff__user__username",
                     "staff__department",
                     "break_date", "break_start_date_time", "break_end_date_time", "status", "reason"
                     )

    search_fields = ( "staff__user__username",
                      "staff__department",
                      "break_date", "break_end_date_time", "break_end_date_time", "status",
                      )

    list_filter = ( "staff__department", "status",)

    ordering = ( "break_date", )

    @admin.display(ordering="staff__user__username")
    def username(self, obj):
        return obj.user.username

    @admin.display(ordering="staff__department")
    def email(self, obj):
        return obj.user.email


