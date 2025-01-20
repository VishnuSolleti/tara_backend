# visa/permissions.py

from rest_framework.permissions import BasePermission
from .models import UserGroup
from functools import wraps
from rest_framework.response import Response
from rest_framework import status

class GroupPermission(BasePermission):
    """
    Custom permission to check if the user belongs to a group with a specific permission.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Get the single user group (assuming one group per user)
        try:
            user_group = UserGroup.objects.get(user=request.user)
        except UserGroup.DoesNotExist:
            return Response({"error": "User is not part of any group."}, status=status.HTTP_403_FORBIDDEN)

        permission_needed = getattr(view, 'permission_required', None)  # Get permission(s) required for the view

        if permission_needed:
            # If it's a list of permissions, check for each one
            if isinstance(permission_needed, list):
                for perm in permission_needed:
                    # Check if the user group has the required permission
                    if user_group.custom_permissions.filter(codename=perm).exists():
                        return True
            else:
                # If it's a single permission, check if the user group has it
                if user_group.custom_permissions.filter(codename=permission_needed).exists():
                    return True

        return False


def has_group_permission(*permissions_needed):
    """
    Decorator to check if the user belongs to a group with specific permissions.
    Supports multiple permissions.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

            # Check if the user belongs to any group (get one group per user)
            try:
                user_group = UserGroup.objects.get(user=request.user)
            except UserGroup.DoesNotExist:
                return Response({"error": "User is not part of any group."}, status=status.HTTP_403_FORBIDDEN)

            # Check if the group has the required permissions
            permissions_found = set()

            for permission_needed in permissions_needed:
                if user_group.custom_permissions.filter(codename=permission_needed).exists():
                    permissions_found.add(permission_needed)

            # Check if all required permissions are found
            if set(permissions_needed) == permissions_found:
                return view_func(request, *args, **kwargs)

            return Response(
                {"error": "You do not have the necessary permissions to access this resource."},
                status=status.HTTP_403_FORBIDDEN
            )

        return _wrapped_view
    return decorator

