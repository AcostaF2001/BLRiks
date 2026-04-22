from django.urls import path

from .api_views import (
    AssignOrganizationAPIView,
    CurrentUserAPIView,
    OrganizationListAPIView,
    UserListAPIView,
    UserRegisterAPIView,
)

app_name = "accounts_api"

urlpatterns = [
    # Usuario autenticado actual
    path("me/", CurrentUserAPIView.as_view(), name="me"),

    # Registro público
    path("register/", UserRegisterAPIView.as_view(), name="register"),

    # Usuarios
    path("users/", UserListAPIView.as_view(), name="user_list"),
    path("users/<int:user_id>/assign-organization/", AssignOrganizationAPIView.as_view(), name="assign_organization"),

    # Organizaciones
    path("organizations/", OrganizationListAPIView.as_view(), name="organization_list"),
]