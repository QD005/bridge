from rest_framework import permissions

class CanManageWorkflow(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'SUPER_ADMIN':
            return True
        if user.role in ['AGENCY_ADMIN', 'DEVELOPER'] and user.agency == obj.agency:
            return True
        # Others can only view published workflows
        if request.method in permissions.SAFE_METHODS and obj.status == 'PUBLISHED':
            return True
        return False