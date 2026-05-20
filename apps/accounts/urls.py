from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

# HTML pages
page_urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
]

# JSON API
api_urlpatterns = [
    path("api/auth/register/", views.RegisterAPIView.as_view(), name="api_register"),
    path("api/auth/profile/", views.ProfileAPIView.as_view(), name="api_profile"),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

urlpatterns = page_urlpatterns + api_urlpatterns
