from rest_framework.permissions import BasePermission, SAFE_METHODS

class OnlyAdminCreate(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_superuser:
            return request.method in SAFE_METHODS
        return request.method