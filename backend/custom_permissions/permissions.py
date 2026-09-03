
from rest_framework.permissions import BasePermission
from backend.accounts.models import User


class Is_Authenticated_Staff_User(BasePermission):
    message = "Only staff users can access this resource."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.role == User.Role.STAFF)

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ADMIN"


class IsReceptionist(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["RECEPTIONIST", "ADMIN"]


class IsBarber(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "BARBER"
