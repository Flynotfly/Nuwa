from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, LogoutView, RegisterView, SessionView

app_name = "user"

urlpatterns = [
    path("login", LoginView.as_view(), name="login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("session", SessionView.as_view(), name="session"),
    path("register", RegisterView.as_view(), name="register"),
    path("refresh", TokenRefreshView.as_view(), name="refresh"),
]
