from rest_framework.permissions import BasePermission

from backend.accounts.models import User, StaffProfile


class AnyOf(BasePermission):
    permission_classes = []

    def has_permission(self, request, view):
        return any(
            permission().has_permission(request, view)
            for permission in self.permission_classes
        )

    def has_object_permission(self, request, view, obj):
        return any(
            permission().has_object_permission(request, view, obj)
            for permission in self.permission_classes
        )


class IsAuthenticatedStaffUser(BasePermission):
    message = "Only active staff users can access this resource."

    def has_permission(self, request, view):
        user = request.user

        return bool(
                        user and user.is_authenticated and user.is_active and
                        user.role == User.Role.STAFF and hasattr(user, "staffprofile") and
                        user.staffprofile.status == StaffProfile.StaffStatus.ACTIVE
        )


class IsSalonManager(BasePermission):
    message = "Only salon managers can access this resource."

    def has_permission(self, request, view):
        user = request.user

        return bool(
                        user and user.is_authenticated and user.is_active and
                        user.role == User.Role.STAFF and hasattr(user, "staffprofile") and
                        user.staffprofile.status == StaffProfile.StaffStatus.ACTIVE and
                        user.groups.filter(name__iexact="manager").exists()
        )


class IsReceptionist(BasePermission):
    message = "Only reception staff can access this resource."

    def has_permission(self, request, view):
        user = request.user

        return bool(
                        user and user.is_authenticated and user.is_active and
                        user.role == User.Role.STAFF and hasattr(user, "staffprofile") and
                        user.staffprofile.department == StaffProfile.Department.RECEPTION and
                        user.staffprofile.status == StaffProfile.StaffStatus.ACTIVE
        )


class IsBarber(BasePermission):
    message = "Only barbers can access this resource."

    def has_permission(self, request, view):
        user = request.user

        return bool(
                        user and user.is_authenticated and user.is_active and
                        user.role == User.Role.STAFF and hasattr(user, "staffprofile") and
                        user.staffprofile.department == StaffProfile.Department.BARBER and
                        user.staffprofile.status == StaffProfile.StaffStatus.ACTIVE
        )


class IsBarberStylist(BasePermission):
    message = "Only barber-stylists can access this resource."

    def has_permission(self, request, view):
        user = request.user

        return bool(
                        user and user.is_authenticated and user.is_active and
                        user.role == User.Role.STAFF and hasattr(user, "staffprofile") and
                        user.staffprofile.department == StaffProfile.Department.BARBER_STYLIST and
                        user.staffprofile.status == StaffProfile.StaffStatus.ACTIVE
        )


class IsStylist(BasePermission):
    message = "Only stylists can access this resource."

    def has_permission(self, request, view):
        user = request.user

        return bool(
                        user and user.is_authenticated and user.is_active and
                        user.role == User.Role.STAFF and hasattr(user, "staffprofile") and
                        user.staffprofile.department == StaffProfile.Department.STYLIST and
                        user.staffprofile.status == StaffProfile.StaffStatus.ACTIVE
        )


class SalonManagerOrBarberOrStylistOrIsBarberStylist(AnyOf):
    permission_classes = [IsSalonManager, IsBarber, IsStylist, IsBarberStylist]


class BarberOrStylistOrIsBarberStylist(AnyOf):
    permission_classes = [IsBarber, IsStylist, IsBarberStylist]


class SalonManagerOrBarberOrStylistOrIsBarberStylistOrReceptionist(AnyOf):
    permission_classes = [IsSalonManager, IsBarber, IsStylist, IsBarberStylist, IsReceptionist]


class SalonManagerOrReceptionist(AnyOf):
    permission_classes = [IsSalonManager, IsReceptionist]

