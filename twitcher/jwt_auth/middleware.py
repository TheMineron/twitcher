from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.middleware import get_user

def get_user_jwt(request):
    user = get_user(request)
    if user.is_authenticated:
        return user
    try:
        token = request.COOKIES.get('access_token')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        auth = JWTAuthentication()
        user, token = auth.authenticate(request)
        return user
    except:
        return AnonymousUser()

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = SimpleLazyObject(lambda: get_user_jwt(request))
        return self.get_response(request)
