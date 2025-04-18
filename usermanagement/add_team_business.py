from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
import boto3
from botocore.exceptions import ClientError
import logging
from Tara.settings.default import *

from .models import (
    Users, Context, Role, UserContextRole, Module,
    ModuleFeature, UserFeaturePermission, SubscriptionPlan, ModuleSubscription
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# Configure logging
logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_team_member_to_business(request):
    """
    Add a team member to a business context with a specific role and permissions.
    If the team member doesn't exist, create a new user and send an invitation email.
    The user context role will be in a pending state until the team member accepts the invitation.

    Expected request data:
    {
        "context_id": 1,
        "email": "teammember@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "mobile_number": "1234567890",
        "role_id": 3,  # Optional: If not provided, the default employee role will be used
        "permissions": [  # Optional: If not provided, default permissions for the role will be used
            {
                "module_id": 1,
                "feature_code": "employee",
                "actions": ["read", "create", "update"]
            },
            {
                "module_id": 1,
                "feature_code": "attendance",
                "actions": ["read", "create"]
            }
        ]
    }
    """
    # Extract data from request
    context_id = request.data.get('context_id')
    email = request.data.get('email')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    mobile_number = request.data.get('mobile_number')
    role_id = request.data.get('role_id')
    permissions = request.data.get('permissions', [])
    authenticated_user = request.user

    # Validate required fields
    if not all([context_id, email, first_name, last_name, mobile_number]):
        return Response(
            {
                "error": "Missing required fields. Please provide context_id, email, first_name, last_name, and mobile_number."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Get the context
        context = Context.objects.get(id=context_id)

        # Check if the authenticated user is the owner of the context
        if context.owner_user != authenticated_user and not authenticated_user.is_staff and not authenticated_user.is_superuser:
            return Response(
                {"error": "You don't have permission to add team members to this business context."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if the context is a business context
        if context.context_type != 'business':
            return Response(
                {"error": "Team members can only be added to business contexts."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use transaction to ensure all operations succeed or fail together
        with transaction.atomic():
            # 1. Check if user already exists
            try:
                user = User.objects.get(email=email)
                # If user exists, check if they already have a role in this context
                existing_role = UserContextRole.objects.filter(
                    user=user,
                    context=context,
                    status='active'
                ).first()

                if existing_role:
                    return Response(
                        {"error": f"User with email {email} already has an active role in this context."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Check if there's a pending invitation
                pending_role = UserContextRole.objects.filter(
                    user=user,
                    context=context,
                    status='pending'
                ).first()

                if pending_role:
                    return Response(
                        {"error": f"User with email {email} already has a pending invitation to this context."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                is_new_user = False
            except User.DoesNotExist:
                # Create new user if they don't exist
                user = User.objects.create(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    mobile_number=mobile_number,
                    status='pending',
                    registration_flow='invited',
                    registration_completed=False,
                    is_active='no'
                )
                # Set a random password that the user can change later
                user.set_password(User.objects.make_random_password())
                user.save()
                is_new_user = True

            # 2. Get the role
            if role_id:
                try:
                    role = Role.objects.get(id=role_id, context=context)
                except Role.DoesNotExist:
                    return Response(
                        {"error": f"Role with ID {role_id} does not exist in this context."},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Get the default employee role
                role = Role.objects.get(
                    context=context,
                    role_type='employee',
                    is_default_role=True
                )

            # 3. Create user context role with pending status
            user_context_role = UserContextRole.objects.create(
                user=user,
                context=context,
                role=role,
                status='pending',  # Set to pending until the user accepts
                added_by=authenticated_user
            )

            # 4. Set up feature permissions
            if permissions:
                # Use the provided permissions
                for permission_data in permissions:
                    module_id = permission_data.get('module_id')
                    feature_code = permission_data.get('feature_code')
                    actions = permission_data.get('actions', [])

                    if not all([module_id, feature_code, actions]):
                        continue

                    # Create the feature permission
                    UserFeaturePermission.objects.create(
                        user_context_role=user_context_role,
                        module_id=module_id,
                        feature_code=feature_code,
                        actions=actions,
                        is_active=True,
                        created_by=authenticated_user
                    )
            else:
                # Get all modules subscribed to this context
                subscribed_modules = ModuleSubscription.objects.filter(
                    context=context,
                    status__in=['active', 'trial']
                ).values_list('module_id', flat=True)

                # For each module, get all features and create permissions based on role type
                for module_id in subscribed_modules:
                    module = Module.objects.get(id=module_id)
                    module_features = ModuleFeature.objects.filter(module=module)

                    # Determine default actions based on role type
                    default_actions = []
                    if role.role_type == 'admin':
                        default_actions = ['create', 'read', 'update', 'delete', 'approve']
                    elif role.role_type == 'manager':
                        default_actions = ['create', 'read', 'update']
                    else:  # employee or other roles
                        default_actions = ['read']

                    # Create a permission for each feature
                    for feature in module_features:
                        UserFeaturePermission.objects.create(
                            user_context_role=user_context_role,
                            module=module,
                            feature_code=feature.service.lower(),
                            actions=default_actions,
                            is_active=True,
                            created_by=authenticated_user
                        )

            # 5. Send invitation email
            try:
                # Generate invitation token
                invitation_token = str(uuid.uuid4())
                user_context_role.invitation_token = invitation_token
                user_context_role.save()

                # Prepare email content
                business_name = context.name
                owner_name = f"{authenticated_user.first_name} {authenticated_user.last_name}"
                role_name = role.name
                invitation_link = f"{settings.FRONTEND_URL}/accept-invitation/{invitation_token}"

                # Send invitation email
                send_mail(
                    f'Invitation to join {business_name}',
                    f'''
                    Hello {first_name},

                    {owner_name} has invited you to join {business_name} as a {role_name}.

                    Please click the following link to accept the invitation and set up your account:
                    {invitation_link}

                    If you did not expect this invitation, please ignore this email.

                    Best regards,
                    The {settings.SITE_NAME} Team
                    ''',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log the error but don't fail the request
                print(f"Failed to send invitation email: {str(e)}")

            # Return success response
            return Response(
                {
                    "message": "Team member invitation sent successfully.",
                    "user_id": user.id,
                    "email": user.email,
                    "context_id": context.id,
                    "role_id": role.id,
                    "role_name": role.name,
                    "user_context_role_id": user_context_role.id,
                    "status": "pending",
                    "is_new_user": is_new_user
                },
                status=status.HTTP_201_CREATED
            )

    except Context.DoesNotExist:
        return Response(
            {"error": f"Context with ID {context_id} does not exist."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Role.DoesNotExist:
        return Response(
            {"error": "Default employee role not found in this context."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"Failed to add team member: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def accept_team_invitation(request):
    """
    Accept a team invitation and activate the user context role.

    Expected request data:
    {
        "invitation_token": "uuid-token-here",
        "password": "new-password"  # Required for new users
    }
    """
    invitation_token = request.data.get('invitation_token')
    password = request.data.get('password')

    if not invitation_token:
        return Response(
            {"error": "Invitation token is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Get the user context role with the invitation token
        user_context_role = UserContextRole.objects.get(
            invitation_token=invitation_token,
            status='pending'
        )

        user = user_context_role.user

        # Check if this is a new user
        if user.status == 'pending' and user.registration_flow == 'invited':
            # This is a new user, they need to set a password
            if not password:
                return Response(
                    {"error": "Password is required for new users."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update user status
            user.status = 'active'
            user.registration_completed = True
            user.is_active = 'yes'
            user.set_password(password)
            user.save()

        # Activate the user context role
        user_context_role.status = 'active'
        user_context_role.invitation_token = None
        user_context_role.save()

        # Return success response
        return Response(
            {
                "message": "Team invitation accepted successfully.",
                "user_id": user.id,
                "email": user.email,
                "context_id": user_context_role.context.id,
                "role_id": user_context_role.role.id,
                "role_name": user_context_role.role.name
            },
            status=status.HTTP_200_OK
        )

    except UserContextRole.DoesNotExist:
        return Response(
            {"error": "Invalid or expired invitation token."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"Failed to accept invitation: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )