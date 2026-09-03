from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction

from backend.accounts.models import (
    User,
    CustomerProfile,
    StaffProfile,
)


# ============================================================
# USER CREATION
# ============================================================

def create_user(*, user_data, role):
    """
    Create a User only.

    This function does NOT create CustomerProfile or StaffProfile.

    Profile creation is handled by:
        create_customer()
        create_staff()

    Supported roles:
        CUSTOMER
        STAFF
        STAFF_ADMIN
    """

    user_data = user_data.copy()

    password = user_data.pop("password", None)
    password2 = user_data.pop("password2", None)

    # --------------------------------------------------------
    # Password is required when creating a user.
    # --------------------------------------------------------

    if not password:
        raise ValidationError({
            "password": "Password is required."
        })

    if not password2:
        raise ValidationError({
            "password2": "Password confirmation is required."
        })

    if password != password2:
        raise ValidationError({
            "password2": "Passwords don't match."
        })

    # --------------------------------------------------------
    # Do not allow the caller to secretly change the role
    # through user_data.
    # --------------------------------------------------------

    user_data.pop("role", None)

    # --------------------------------------------------------
    # Validate role.
    # --------------------------------------------------------

    if role not in User.Role:
        raise ValidationError({
            "role": "Invalid user role."
        })

    # --------------------------------------------------------
    # Create User.
    # --------------------------------------------------------

    user = User( **user_data, role=role,  )

    user.set_password(password)

    # Model validation.
    #
    # This validates things such as:
    # - EmailField format
    # - phone number validator
    # - model field validation
    #
    user.full_clean()

    user.save()

    return user


# ============================================================
# CUSTOMER CREATION
# ============================================================

@transaction.atomic
def create_customer(*, user_data, role=User.Role.CUSTOMER,):
    """
    Atomically creates:

        User
        CustomerProfile

    Customer users are created with the CUSTOMER role.

    If either operation fails, the entire transaction rolls back.
    """

    if role != User.Role.CUSTOMER:
        raise ValidationError({
            "role": "create_customer() can only create CUSTOMER users."
        })

    user = create_user( user_data=user_data, role=role, )

    customer = CustomerProfile.objects.create( user=user, )

    return user, customer


# ============================================================
# STAFF CREATION
# ============================================================

@transaction.atomic
def create_staff( *, user_data, role=User.Role.STAFF, staff_data=None,):
    """
    Atomically creates:

        User
        StaffProfile

    Staff creation is intentionally separate from generic
    User creation because StaffProfile contains staff-specific
    information such as:

        department
        position
        employment_date
        status

    If either operation fails, the entire transaction rolls back.
    """

    if role != User.Role.STAFF:
        raise ValidationError({
            "role": "create_staff() can only create STAFF users."
        })

    staff_data = (staff_data or {}).copy()

    user = create_user( user_data=user_data, role=role, )

    staff = StaffProfile.objects.create( user=user, **staff_data, )

    return user, staff


# ============================================================
# GENERIC USER UPDATE
# ============================================================

@transaction.atomic
def update_user( *, user, user_data, ):
    """
    Update an existing User.

    IMPORTANT:
    This service does NOT support role changes.

    The existing role remains unchanged.

    Password changes:
        password
        password2

    are validated before changing the password.

    This is intended for administrative/general User updates.
    """

    user_data = user_data.copy()

    # --------------------------------------------------------
    # Role changes are NOT supported.
    # --------------------------------------------------------

    user_data.pop("role", None)

    # --------------------------------------------------------
    # Password handling.
    # --------------------------------------------------------

    password = user_data.pop("password", None)
    password2 = user_data.pop("password2", None)

    if password is not None:

        if not password2:
            raise ValidationError({
                "password2":
                    "Password confirmation is required."
            })

        if password != password2:
            raise ValidationError({
                "password2":
                    "Passwords don't match."
            })

        user.set_password(password)

    # --------------------------------------------------------
    # Update normal User fields.
    # --------------------------------------------------------

    for attr, value in user_data.items():
        setattr(user, attr, value)

    # --------------------------------------------------------
    # Validate and save.
    # --------------------------------------------------------

    user.full_clean()
    user.save()

    return user


# ============================================================
# CURRENT USER / SELF ACCOUNT UPDATE
# ============================================================

@transaction.atomic
def update_my_account(*, user, user_data, current_password=None, ):
    """
    Update the currently authenticated user's account.

    This is intended for endpoints such as:

        PATCH /barbers/me/

    or:

        PATCH /my-account/

    Allowed fields should be controlled by the serializer.

    Role changes are NOT allowed.

    Password changes require:

        current_password
        password
        password2
    """

    user_data = user_data.copy()

    # --------------------------------------------------------
    # Never allow self-service role changes.
    # --------------------------------------------------------

    user_data.pop("role", None)

    # --------------------------------------------------------
    # Password fields.
    # --------------------------------------------------------

    password = user_data.pop("password", None)
    password2 = user_data.pop("password2", None)

    # --------------------------------------------------------
    # Password change.
    # --------------------------------------------------------

    if password is not None:

        if not current_password:
            raise ValidationError({
                "current_password":
                    "Current password is required."
            })

        if not user.check_password(current_password):
            raise ValidationError({
                "current_password":
                    "Current password is incorrect."
            })

        if not password2:
            raise ValidationError({
                "password2":
                    "Password confirmation is required."
            })

        if password != password2:
            raise ValidationError({
                "password2":
                    "Passwords don't match."
            })

        user.set_password(password)

    # --------------------------------------------------------
    # Normal account fields.
    # --------------------------------------------------------

    for attr, value in user_data.items():
        setattr(user, attr, value)

    # --------------------------------------------------------
    # Validate and save.
    # --------------------------------------------------------

    user.full_clean()
    user.save()

    return user


# ============================================================
# COMPLETE STAFF UPDATE
# ============================================================

@transaction.atomic
def update_staff(*, staff,
                 user_data: dict[str, Any] | None = None,
                 staff_data: dict[str, Any] | None = None, ):
    """
    Update a complete Staff record.

    This updates BOTH:

        User
        StaffProfile

    Example User fields:

        first_name
        last_name
        username
        email
        phone_number
        image
        is_active
        password
        password2

    Example StaffProfile fields:

        department
        position
        employment_date
        status

    Role changes are NOT supported.

    The user's existing role must remain STAFF.
    """

    if staff.user.role != User.Role.STAFF:
        raise ValidationError({
            "role":
                "Only STAFF users can be updated through "
                "update_staff()."
        })

    user_data = (user_data or {}).copy()
    staff_data = (staff_data or {}).copy()

    # --------------------------------------------------------
    # Never allow role changes.
    # --------------------------------------------------------

    user_data.pop("role", None)

    # --------------------------------------------------------
    # Password handling.
    #
    # Administrative staff updates do not require the current
    # password. This is different from update_my_account().
    # --------------------------------------------------------

    password: str | None = user_data.pop("password", None)
    password2: str | None = user_data.pop("password2", None)


    if password is not None:

        if not password2:

            raise ValidationError({
                "password2":
                    "Password confirmation is required."
            })

        if password != password2:
            raise ValidationError({
                "password2":
                    "Passwords don't match."
            })

        staff.user.set_password(password)

    # --------------------------------------------------------
    # Update User.
    # --------------------------------------------------------

    for attr, value in user_data.items():
        setattr(staff.user, attr, value)

    # --------------------------------------------------------
    # Update StaffProfile.
    # --------------------------------------------------------

    for attr, value in staff_data.items():
        setattr(staff, attr, value)

    # --------------------------------------------------------
    # Validate BOTH objects before saving.
    # --------------------------------------------------------

    staff.user.full_clean()
    staff.full_clean()

    # --------------------------------------------------------
    # Save BOTH.
    # --------------------------------------------------------

    staff.user.save()
    staff.save()

    return staff


# ============================================================
# STAFF PROFILE ONLY UPDATE
# ============================================================

@transaction.atomic
def update_staff_profile(*, profile, profile_data, ):
    """
    Update ONLY StaffProfile.

    This does NOT update the User.

    Use this when you only want to change:

        department
        position
        employment_date
        status
    """

    profile_data = profile_data.copy()

    # --------------------------------------------------------
    # Do not allow changing the associated user.
    # --------------------------------------------------------

    profile_data.pop("user", None)

    # --------------------------------------------------------
    # Update StaffProfile.
    # --------------------------------------------------------

    for attr, value in profile_data.items():
        setattr(profile, attr, value)

    profile.full_clean()
    profile.save()

    return profile


# ============================================================
# CUSTOMER PROFILE ONLY UPDATE
# ============================================================

@transaction.atomic
def update_customer_profile( *, profile, profile_data, ):
    """
    Update ONLY CustomerProfile.

    This does NOT update the User.
    """

    profile_data = profile_data.copy()

    # The User relationship must not be changed here.
    profile_data.pop("user", None)

    for attr, value in profile_data.items():
        setattr(profile, attr, value)

    profile.full_clean()
    profile.save()

    return profile


# ============================================================
# CUSTOMER COMPLETE UPDATE
# ============================================================

@transaction.atomic
def update_customer( *, customer, user_data=None, profile_data=None, ):
    """
    Update a complete Customer record.

    Updates:

        User
        CustomerProfile

    Role changes are NOT supported.

    The User must remain CUSTOMER.
    """

    if customer.user.role != User.Role.CUSTOMER:
        raise ValidationError({
            "role":
                "Only CUSTOMER users can be updated through "
                "update_customer()."
        })

    user_data = (user_data or {}).copy()
    profile_data = (profile_data or {}).copy()

    # --------------------------------------------------------
    # Never allow role changes.
    # --------------------------------------------------------

    user_data.pop("role", None)

    # --------------------------------------------------------
    # Password handling.
    # --------------------------------------------------------

    password = user_data.pop("password", None)
    password2 = user_data.pop("password2", None)

    if password is not None:

        if not password2:
            raise ValidationError({
                "password2":
                    "Password confirmation is required."
            })

        if password != password2:
            raise ValidationError({
                "password2":
                    "Passwords don't match."
            })

        customer.user.set_password(password)

    # --------------------------------------------------------
    # Update User.
    # --------------------------------------------------------

    for attr, value in user_data.items():
        setattr(customer.user, attr, value)

    # --------------------------------------------------------
    # Update CustomerProfile.
    #
    # Your current CustomerProfile only contains "user", so
    # this will normally be empty.
    # --------------------------------------------------------

    profile_data.pop("user", None)

    for attr, value in profile_data.items():
        setattr(customer, attr, value)

    # --------------------------------------------------------
    # Validate.
    # --------------------------------------------------------

    customer.user.full_clean()
    customer.full_clean()

    # --------------------------------------------------------
    # Save.
    # --------------------------------------------------------

    customer.user.save()
    customer.save()

    return customer


# ============================================================
# DELETE STAFF
# ============================================================

@transaction.atomic
def delete_staff( *, staff, ):
    """
    Delete a Staff.

    The StaffProfile belongs to the User through:

        StaffProfile.user = OneToOneField(...,
                                          on_delete=CASCADE)

    Therefore deleting the User automatically deletes the
    StaffProfile.

    We deliberately delete the User rather than only deleting
    StaffProfile because the account itself should disappear.
    """

    user = staff.user

    user.delete()

    return True


# ============================================================
# DELETE CUSTOMER
# ============================================================

@transaction.atomic
def delete_customer(*, customer, ):
    """
    Delete a Customer.

    Deleting the User automatically deletes CustomerProfile
    because CustomerProfile.user uses CASCADE.
    """

    user = customer.user

    user.delete()

    return True