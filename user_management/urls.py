from django.urls import path
from . import views
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('permissions/', views.custom_permission_list_create, name='custom_permission_list_create'),
    path('permissions/<int:pk>/', views.custom_permission_retrieve_update_destroy,
         name='custom_permission_retrieve_update_destroy'),
    # CRUD for CustomGroup
    path('groups/', views.custom_group_list_create, name='custom_group_list_create'),
    path('groups/<int:pk>/', views.custom_group_retrieve_update_destroy, name='custom_group_retrieve_update_destroy'),
    # Add Permission to the Group
    path('groups/<int:group_id>/permissions/', views.assign_permissions_to_group, name='assign_permissions_to_group'),

    # path('users/by-type/', UserListByTypeAPIView.as_view(), name='users-by-type')

    path('users/stats/', DynamicUserStatsAPIView.as_view(), name='user-stats'),
    path('users/by-type/', UsersByDynamicTypeAPIView.as_view(), name='users-by-type'),

    # Permission Assignment
    path('user-group/assign/', assign_group_with_permissions, name='assign_group_with_permissions'),

    path('user-group/<int:user_group_id>/permissions/', update_group_permissions, name='update_group_permissions'),
    path('user-group', get_user_group_permissions, name='get_user_group_permissions'),

    path('register/', views.user_registration, name='user_registration'),
    path('admin/user-registration/', user_registration_by_admin, name='admin-user-registration'),
    path('users/', users_creation, name='users_creation'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('visa-users/', visa_users_creation, name='visa_users_creation'),
    path('activate', ActivateUserView.as_view(), name='activate'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protected/', TestProtectedAPIView.as_view(), name='test_protected'),
    # Forgot password view
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),

    # Reset password view
    path('reset-password/<uid>/<token>/', ResetPasswordView.as_view(), name='reset-password'),

    # Refresh token view
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh-token'),

    path('users-kyc/', UsersKYCListView.as_view(), name='user-kyc-list'),

    # URL for retrieving, updating, and deleting specific user details
    path('users-kyc/<int:pk>/', UsersKYCDetailView.as_view(), name='user-kyc-detail'),

    # firm urls
    path('firmkyc/', FirmKYCView.as_view(), name='firmkyc'),

    path('update-users-info', views.partial_update_user, name='partial_update_user'),

    path('services/', ServicesMasterDataListAPIView.as_view()),  # For GET (list) and POST

    path('services/<int:pk>/', ServicesMasterDataDetailAPIView.as_view()),  # For GET (detail), PUT, DELETE

    # Endpoint for specific visa application actions (GET, PUT, DELETE)
    path('visa-applicants/<int:pk>/', VisaApplicationDetailAPIView.as_view(), name='visa-applications-detail-update-delete'),

    path('visa-servicetasks/', manage_visa_applications, name='manage_visa_applications'),

    path('visa-clients/', get_visa_clients_users_list, name='visa_clients_list'),

    path('visa-clients/dashboard-status/', service_status, name='service-status'),

    path('visa-applicants/all-tasks-data/', all_service_data, name='all_service_data'),

    path('service-details/<int:pk>/', ServiceDetailsAPIView.as_view(), name='service-details'),

]
