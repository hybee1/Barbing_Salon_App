from rest_framework.permissions import BasePermission

from backend.accounts.models import User, StaffProfile


class Is_Authenticated_Staff_User(BasePermission):
    message = "Only active staff users can access this resource."

    def has_permission(self, request, view):
        user = request.user

        return bool(
                        user and user.is_authenticated and user.is_active and
                        user.role == User.Role.STAFF and hasattr(user, "staffprofile") and
                        user.staffprofile.status == StaffProfile.StaffStatus.ACTIVE
        )


class Is_SalonManager(BasePermission):
    message = "Only salon managers can access this resource."

    def has_permission(self, request, view):
        user = request.user

        return bool(
                        user and user.is_authenticated and user.is_active and
                        user.groups.filter(name__iexact="manager").exists()
        )


class Is_Receptionist(BasePermission):
    message = "Only reception staff can access this resource."

    def has_permission(self, request, view):
        user = request.user

        return bool(
                        user and user.is_authenticated and user.is_active and
                        user.role == User.Role.STAFF and hasattr(user, "staffprofile") and
                        user.staffprofile.department == StaffProfile.Department.RECEPTION and
                        user.staffprofile.status == StaffProfile.StaffStatus.ACTIVE
        )


class Is_Barber(BasePermission):
    message = "Only barbers can access this resource."

    def has_permission(self, request, view):
        user = request.user

        return bool(
                        user and user.is_authenticated and user.is_active and
                        user.role == User.Role.STAFF and hasattr(user, "staffprofile") and
                        user.staffprofile.department == StaffProfile.Department.BARBER and
                        user.staffprofile.status == StaffProfile.StaffStatus.ACTIVE
        )


class Is_Barber_Stylist(BasePermission):
    message = "Only barber-stylists can access this resource."

    def has_permission(self, request, view):
        user = request.user

        return bool(
                        user and user.is_authenticated and user.is_active and
                        user.role == User.Role.STAFF and hasattr(user, "staffprofile") and
                        user.staffprofile.department == StaffProfile.Department.BARBER_STYLIST and
                        user.staffprofile.status == StaffProfile.StaffStatus.ACTIVE
        )


class Is_Stylist(BasePermission):
    message = "Only stylists can access this resource."

    def has_permission(self, request, view):
        user = request.user

        return bool(
                        user and user.is_authenticated and user.is_active and
                        user.role == User.Role.STAFF and hasattr(user, "staffprofile") and
                        user.staffprofile.department == StaffProfile.Department.STYLIST and
                        user.staffprofile.status == StaffProfile.StaffStatus.ACTIVE
        )
