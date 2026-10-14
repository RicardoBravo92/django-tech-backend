from django.urls import path

from apps.users import views

urlpatterns = [
    path("auth/login", views.LoginView.as_view(), name="auth-login"),
    path("auth/register", views.RegisterView.as_view(), name="auth-register"),
    path("auth/refresh", views.RefreshView.as_view(), name="auth-refresh"),
    path("auth/logout", views.LogoutView.as_view(), name="auth-logout"),
    path("auth/me", views.MeView.as_view(), name="auth-me"),
    path(
        "auth/forgot-password",
        views.ForgotPasswordView.as_view(),
        name="auth-forgot-password",
    ),
    path(
        "auth/reset-password",
        views.ResetPasswordView.as_view(),
        name="auth-reset-password",
    ),
    path("users", views.UserListCreateView.as_view(), name="user-list"),
    path("users/<int:user_id>", views.UserDetailView.as_view(), name="user-detail"),
]
