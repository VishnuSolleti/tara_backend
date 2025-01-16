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

        # Check the group of the user
        user_group = UserGroup.objects.filter(user=request.user).first()
        if not user_group:
            return False  # User is not part of any group

        group = user_group.group
        permission_needed = view.permission_required  # Define the permission needed in the view

        # Check if the group has the required permission
        if group.permissions.filter(name=permission_needed).exists():
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
            user_group = UserGroup.objects.filter(user=request.user).first()
            if not user_group:
                return Response({"error": "User is not part of any group."}, status=status.HTTP_403_FORBIDDEN)

            group = user_group.group

            # Check if the group has the required permission
            if group.permissions.filter(name=permission_needed).exists():
                return view_func(request, *args, **kwargs)
            else:
                return Response({"error": "You do not have the necessary permissions to access this resource."},
                                 status=status.HTTP_403_FORBIDDEN)

        return _wrapped_view
    return decorator
