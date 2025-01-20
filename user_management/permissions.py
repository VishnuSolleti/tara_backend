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

        # Check if the user is part of any group
        user_groups = UserGroup.objects.filter(user=request.user)
        if not user_groups.exists():
            return False  # User is not part of any group

        permission_needed = view.permission_required  # Define the permission needed in the view

        # Check if any group has the required permission
        for user_group in user_groups:
            if user_group.custom_permissions.filter(codename=permission_needed).exists():
                return True

        return False

def has_group_permission(permission_needed):
    """
    Decorator to check if the user belongs to a group with a specific permission.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

            # Check if the user belongs to any group
            user_groups = UserGroup.objects.filter(user=request.user)
            if not user_groups.exists():
                return Response({"error": "User is not part of any group."}, status=status.HTTP_403_FORBIDDEN)

            # Check if any group has the required permission
            for user_group in user_groups:
                if user_group.custom_permissions.filter(codename=permission_needed).exists():
                    return view_func(request, *args, **kwargs)

            return Response({"error": "You do not have the necessary permissions to access this resource."},
                             status=status.HTTP_403_FORBIDDEN)

        return _wrapped_view
    return decorator

