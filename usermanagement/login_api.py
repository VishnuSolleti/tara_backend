from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import (
    Users, Context, Role, UserContextRole, Module,
    ModuleFeature, UserFeaturePermission, ModuleSubscription
)

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login API that authenticates a user and returns:
    - Access token
    - Refresh token
    - User details
    - Active context information
    - User role in the active context
    - Module subscriptions for the active context

    Expected request data:
    {
        "email": "user@example.com",
        "password": "securepassword"
    }
    """
    # Extract data from request
    email = request.data.get('email')
    password = request.data.get('password')

    # Validate required fields
    if not all([email, password]):
        return Response(
            {"error": "Missing required fields. Please provide email and password."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Try to get the user directly by email
        try:
            user = User.objects.get(email=email)
            # Check if the password is correct
            if not user.check_password(password):
                return Response(
                    {"error": "Invalid credentials. Please check your email and password."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid credentials. Please check your email and password."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if user is active
        if user.is_active != 'yes':
            return Response(
                {"error": "Your account is not active. Please activate your account or contact support."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update last login time
        user.last_login = timezone.now()
        user.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Get user's active context
        active_context = None
        context_data = None
        user_role = None
        role_data = None
        module_subscriptions = []

        if user.active_context:
            active_context = user.active_context
            context_data = {
                "id": active_context.id,
                "name": active_context.name,
                "context_type": active_context.context_type,
                "status": active_context.status,
                "profile_status": active_context.profile_status,
                "created_at": active_context.created_at
            }

            # Get user's role in the active context
            try:
                user_context_role = UserContextRole.objects.get(
                    user=user,
                    context=active_context,
                    status='active'
                )
                user_role = user_context_role.role
                role_data = {
                    "id": user_role.id,
                    "name": user_role.name,
                    "role_type": user_role.role_type,
                    "description": user_role.description
                }

                # Get user's feature permissions
                feature_permissions = UserFeaturePermission.objects.filter(
                    user_context_role=user_context_role,
                    is_active="yes"
                )

                permissions_data = []
                for permission in feature_permissions:
                    permissions_data.append({
                        "id": permission.id,
                        "module_id": permission.module.id,
                        "module_name": permission.module.name,
                        "actions": permission.actions
                    })

                role_data["permissions"] = permissions_data

            except UserContextRole.DoesNotExist:
                pass

            # Get module subscriptions for the active context
            subscriptions = ModuleSubscription.objects.filter(
                context=active_context,
                status__in=['active', 'trial']
            )

            for subscription in subscriptions:
                module_subscriptions.append({
                    "id": subscription.id,
                    "module_id": subscription.module.id,
                    "module_name": subscription.module.name,
                    "plan_id": subscription.plan.id,
                    "plan_name": subscription.plan.name,
                    "status": subscription.status,
                    "start_date": subscription.start_date,
                    "end_date": subscription.end_date,
                    "auto_renew": subscription.auto_renew
                })

        # Prepare user data
        user_data = {
            "id": user.id,
            "email": user.email,
            "mobile_number": user.mobile_number,
            "status": user.status,
            "registration_flow": user.registration_flow,
            "initial_selection": user.initial_selection,
            "registration_completed": user.registration_completed,
            "created_at": user.created_at,
            "last_login": user.last_login
        }

        # Return success response with all required data
        return Response({
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user_data,
            "active_context": context_data,
            "user_role": role_data,
            "module_subscriptions": module_subscriptions
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": f"Login failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Refresh an expired access token using a refresh token

    Expected request data:
    {
        "refresh_token": "your_refresh_token_here"
    }
    """
    # Extract refresh token from request
    refresh_token = request.data.get('refresh_token')

    # Validate required fields
    if not refresh_token:
        return Response(
            {"error": "Missing refresh token. Please provide a valid refresh token."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Create a RefreshToken instance from the provided token
        refresh = RefreshToken(refresh_token)

        # Generate a new access token
        access_token = str(refresh.access_token)

        # Return the new access token
        return Response({
            "message": "Token refreshed successfully",
            "access_token": access_token
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": f"Token refresh failed: {str(e)}"},
            status=status.HTTP_401_UNAUTHORIZED
        )

