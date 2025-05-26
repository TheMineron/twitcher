from django.urls import path, include
from .views import RegisterView, MyTokenObtainPairView, UserProfileView, LoginPageView, RegisterPageView, \
    VerifyTokenView

urlpatterns = [
    path('api/auth/register/', RegisterView.as_view(), name='auth_register'),
    path('api/auth/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/userinfo/', UserProfileView.as_view(), name='user_profile'),
    path('login/', LoginPageView.as_view(), name='login'),
    path('register/', RegisterPageView.as_view(), name='register'),
    path('api/verify-token/', VerifyTokenView.as_view(), name='verify-token'),
    path('oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]