from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS or request.user.is_staff:
            return True
        return False


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS or request.user.is_authenticated:
            return True
        return False
