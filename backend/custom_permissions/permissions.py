
from rest_framework.permissions import BasePermission
from backend.accounts.models import User, StaffProfile


class Is_Authenticated_Staff_User(BasePermission):
    message = "Only staff users can access this resource."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.role == User.Role.STAFF)


class Is_SalonManager(BasePermission):
    def has_permission(self, request, view):
        return Is_Authenticated_Staff_User and request.user.groups.filter(name__iexact="manager").exists()


class Is_Receptionist(BasePermission):
    def has_permission(self, request, view):
        return (Is_Authenticated_Staff_User and
                request.user.Staffprofile.department == StaffProfile.Department.RECEPTION.value)


class Is_Barber(BasePermission):
    def has_permission(self, request, view):
        return (Is_Authenticated_Staff_User and
                    request.user.Staffprofile == StaffProfile.Department.BARBER.value)


class Is_Barber_Stylist(BasePermission):
    def has_permission(self, request, view):
        return (Is_Authenticated_Staff_User and
                    request.user.Staffprofile == StaffProfile.Department.BARBER_STYLIST.value)


class Is_Stylist(BasePermission):
    def has_permission(self, request, view):
        return (Is_Authenticated_Staff_User and
                    request.user.Staffprofile == StaffProfile.Department.STYLIST.value)
