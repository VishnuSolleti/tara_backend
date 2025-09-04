# Tara/middleware/auth.py - ADD THIS CODE
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from django.conf import settings


class CrossSubdomainAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check JWT cookie from any subdomain
        access_token = request.COOKIES.get('access_token')

        if access_token:
            try:
                # Validate JWT token
                token = AccessToken(access_token)
                user_id = token['user_id']

                # Set user in request
                from usermanagement.models import Users
                user = Users.objects.get(id=user_id)
                request.user = user

            except Exception as e:
                # Clear invalid cookies
                response = JsonResponse({'error': 'Invalid token'}, status=401)
                response.delete_cookie('access_token', domain='.tarafirst.com')
                response.delete_cookie('refresh_token', domain='.tarafirst.com')
                return response

        return self.get_response(request)