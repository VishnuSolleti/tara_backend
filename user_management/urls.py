from django.urls import path
from . import views
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', views.user_registration, name='user_registration'),
    path('users/', users_creation, name='users_creation'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('visa-users/', visa_users_creation, name='visa_users_creation'),
    path('activate/<uid>/<token>/', ActivateUserView.as_view(), name='activate'),
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
