from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Allows access only to the owner of the user object."""
    def has_object_permission(self, request, view, obj):
        """Check if requested object equals authenticated user."""
        return obj == request.user
