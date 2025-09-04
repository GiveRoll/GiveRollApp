from django.urls import path, include
from .views import UserView, SocialLogin, LoginView #
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView, PasswordChangeView
# from dj_rest_auth.registration.views import ResendEmailVerificationView
from rest_framework_simplejwt.views import TokenBlacklistView
from dj_rest_auth.registration.views import RegisterView

urlpatterns = [
    path('registration/', include('dj_rest_auth.registration.urls')),
    path("user/", UserView.as_view(), name="user"),
    path("social-auth/", SocialLogin.as_view(), name="social_login"),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', TokenBlacklistView.as_view(), name='logout'),
    path('reset/', PasswordResetView.as_view(), name='password_reset'),
    path('reset/change', PasswordChangeView.as_view(), name='password_change'),
    path('reset/confirm/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]