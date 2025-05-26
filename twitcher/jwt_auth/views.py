from tokenize import TokenError

from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
from django.views import View
from oauth2_provider.contrib.rest_framework import IsAuthenticatedOrTokenHasScope
from rest_framework import generics, permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.views import TokenObtainPairView

from twitcher import settings
from .forms import CustomUserCreationForm
from .serializers import UserSerializer, MyTokenObtainPairSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = Response(serializer.validated_data)

        response.set_cookie(
            key='access_token',
            value=serializer.validated_data['access'],
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            max_age=60 * 60
        )

        response.set_cookie(
            key='refresh_token',
            value=serializer.validated_data['refresh'],
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            max_age=60 * 60 * 24 * 7
        )
        login(request, serializer.user)

        return response


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrTokenHasScope]
    required_scopes = ['read']

    def get_object(self):
        return self.request.user


class LoginPageView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'jwt_auth/login.html', {'form': form})


class RegisterPageView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'jwt_auth/register.html', {'form': form})


class VerifyTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"valid": False, "error": "Token is required"}, status=400)

        try:
            UntypedToken(token)
            return Response({"valid": True})
        except (InvalidToken, TokenError) as e:
            return Response({"valid": False, "error": str(e)}, status=401)
