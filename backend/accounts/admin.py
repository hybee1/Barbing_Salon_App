from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


from .models import (
    User,
    CustomerProfile,
    StaffProfile,
)


# ============================================================
# USER ADMIN
# ============================================================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Controls how the User model appears inside Django Admin.

    User profile creation is NOT handled here.

    Profiles are created explicitly through the service layer:

        create_customer()
        create_staff()

    There is intentionally no role-transition synchronization here.
    """

    list_display = (
        "first_name",
        "last_name",
        "username",
        "email",
        "phone_number",
        "role",
        "image",
        "is_active",
        "is_staff",
        "is_superuser",
        "last_login",
        "date_joined",
    )

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Additional Information",
            {
                "fields": (
                    "role",
                    "phone_number",
                    "image",
                ),
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Additional Information",
            {
                "fields": (
                    "role",
                    "phone_number",
                    "image",
                ),
            },
        ),
    )

    search_fields = (
        "username",
        "phone_number",
        "email",
    )

    list_filter = (
        "role",
        "date_joined",
    )

    ordering = (
        "date_joined",
    )


# ============================================================
# CUSTOMER ADMIN
# ============================================================

@admin.register(CustomerProfile)
class CustomerAdmin(admin.ModelAdmin):
    """
    Controls CustomerProfile in Django Admin.

    CustomerProfile is linked to User through:

        CustomerProfile.user

    User information is displayed through helper methods.
    """

    list_display = (
        "first_name",
        "last_name",
        "username",
        "email",
        "phone_number",
        "role",
        "photo_url",
        "is_active",
        "last_login",
        "date_joined",
    )

    search_fields = (
        "user__username",
        "user__phone_number",
        "user__email",
        "user__first_name",
        "user__last_name",
    )

    list_filter = (
        "user__role",
        "user__is_active",
        "user__date_joined",
    )

    ordering = (
        "user__date_joined",
    )

    @admin.display(
        ordering="user__username",
        description="Username",
    )
    def username(self, obj):
        return obj.user.username

    @admin.display(
        ordering="user__first_name",
        description="First Name",
    )
    def first_name(self, obj):
        return obj.user.first_name

    @admin.display(
        ordering="user__last_name",
        description="Last Name",
    )
    def last_name(self, obj):
        return obj.user.last_name

    @admin.display(
        ordering="user__email",
        description="Email",
    )
    def email(self, obj):
        return obj.user.email

    @admin.display(
        ordering="user__phone_number",
        description="Phone Number",
    )
    def phone_number(self, obj):
        return obj.user.phone_number

    @admin.display(
        ordering="user__role",
        description="Role",
    )
    def role(self, obj):
        return obj.user.role

    @admin.display(
        ordering="user__image",
        description="User Image",
    )
    def photo_url(self, obj):
        if obj.user.image:
            return obj.user.image.url

        return None

    @admin.display(
        ordering="user__date_joined",
        description="Date Joined",
    )
    def date_joined(self, obj):
        return obj.user.date_joined

    @admin.display(
        boolean=True,
        ordering="user__is_active",
        description="Active",
    )
    def is_active(self, obj):
        return obj.user.is_active

    @admin.display(
        ordering="user__last_login",
        description="Last Login",
    )
    def last_login(self, obj):
        return obj.user.last_login


# ============================================================
# STAFF ADMIN
# ============================================================

@admin.register(StaffProfile)
class StaffAdmin(admin.ModelAdmin):
    """
    Controls StaffProfile in Django Admin.

    StaffProfile contains staff-specific information:

        department
        position
        employment_date
        status

    User information is displayed through helper methods.
    """

    list_display = (
        "first_name",
        "last_name",
        "username",
        "email",
        "department",
        "position",
        "phone_number",
        "employment_date",
        "photo_url",
        "status",
        "last_login",
        "date_joined",
    )

    search_fields = (
        "department",
        "position",
        "status",
        "user__username",
        "user__email",
        "user__phone_number",
        "user__first_name",
        "user__last_name",
    )

    list_filter = (
        "department",
        "position",
        "status",
        "user__is_active",
    )

    ordering = (
        "user__date_joined",
    )

    @admin.display(
        ordering="user__username",
        description="Username",
    )
    def username(self, obj):
        return obj.user.username

    @admin.display(
        ordering="user__first_name",
        description="First Name",
    )
    def first_name(self, obj):
        return obj.user.first_name

    @admin.display(
        ordering="user__last_name",
        description="Last Name",
    )
    def last_name(self, obj):
        return obj.user.last_name

    @admin.display(
        ordering="user__email",
        description="Email",
    )
    def email(self, obj):
        return obj.user.email

    @admin.display(
        ordering="user__phone_number",
        description="Phone Number",
    )
    def phone_number(self, obj):
        return obj.user.phone_number

    @admin.display(
        ordering="user__role",
        description="Role",
    )
    def role(self, obj):
        return obj.user.role

    @admin.display(
        ordering="user__image",
        description="User Image",
    )
    def photo_url(self, obj):
        if obj.user.image:
            return obj.user.image.url

        return None

    @admin.display(
        ordering="user__date_joined",
        description="Date Joined",
    )
    def date_joined(self, obj):
        return obj.user.date_joined

    @admin.display(
        ordering="user__last_login",
        description="Last Login",
    )
    def last_login(self, obj):
        return obj.user.last_login