from rest_framework import permissions

class CanManageService(permissions.BasePermission):
    """
    Super Admin: all services
    Agency Admin / Developer: own agency services
    Others: read-only if service is ACTIVE
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'SUPER_ADMIN':
            return True
        if user.role in ['AGENCY_ADMIN', 'DEVELOPER'] and user.agency == obj.agency:
            return True
        # Read-only for others
        if request.method in permissions.SAFE_METHODS and obj.status == 'ACTIVE':
            return True
        return False