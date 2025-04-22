from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import ModuleFeature, UserFeaturePermission
from .models import *
from .serializers import ModuleFeatureSerializer, UserFeaturePermissionSerializer


# ModuleFeature Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_module_features(request):
    """List all module features"""
    print(request.user.active_context)
    features = ModuleFeature.objects.all()
    serializer = ModuleFeatureSerializer(features, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_module_features_by_module(request, module_id):
    """List all module features for a specific module"""
    features = ModuleFeature.objects.filter(module_id=module_id)
    serializer = ModuleFeatureSerializer(features, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_module_feature(request):
    """Create a new module feature"""
    serializer = ModuleFeatureSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_module_feature(request, pk):
    """Get, update or delete a module feature"""
    feature = get_object_or_404(ModuleFeature, pk=pk)

    if request.method == 'GET':
        serializer = ModuleFeatureSerializer(feature)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ModuleFeatureSerializer(feature, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        feature.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_create_module_features(request):
    """Bulk create module features"""
    serializer = ModuleFeatureSerializer(data=request.data, many=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# UserFeaturePermission Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_feature_permissions(request):
    """List all user feature permissions"""
    permissions = UserFeaturePermission.objects.all()
    serializer = UserFeaturePermissionSerializer(permissions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_user_feature_permission(request):
    """Create a new user feature permission"""
    serializer = UserFeaturePermissionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_create_user_feature_permissions(request):
    """Bulk create user feature permissions"""
    serializer = UserFeaturePermissionSerializer(data=request.data, many=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_user_feature_permission(request, pk):
    """Get, update or delete a user feature permission"""
    permission = get_object_or_404(UserFeaturePermission, pk=pk)

    if request.method == 'GET':
        serializer = UserFeaturePermissionSerializer(permission)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserFeaturePermissionSerializer(permission, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        permission.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_feature_permissions_by_role(request, user_context_role_id):
    """Get all feature permissions for a specific user context role"""
    role = get_object_or_404(UserContextRole, pk=user_context_role_id)
    permissions = UserFeaturePermission.objects.filter(user_context_role=role)
    serializer = UserFeaturePermissionSerializer(permissions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_feature_permissions_by_module(request, module_id):
    """Get all feature permissions for a specific module"""
    module = get_object_or_404(Module, pk=module_id)
    permissions = UserFeaturePermission.objects.filter(module=module)
    serializer = UserFeaturePermissionSerializer(permissions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_feature_permissions_by_feature(request, feature_code):
    """Get all feature permissions for a specific feature code"""
    permissions = UserFeaturePermission.objects.filter(feature_code=feature_code)
    serializer = UserFeaturePermissionSerializer(permissions, many=True)
    return Response(serializer.data)
