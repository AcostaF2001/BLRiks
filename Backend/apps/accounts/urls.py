from django.urls import path

from .views import (
    assign_organization_view,
    organization_create_view,
    organization_list_view,
    organization_update_view,
    register_view,
    user_list_view,
)

app_name = "accounts"

urlpatterns = [
    # Registro público de usuarios
    path("register/", register_view, name="register"),

    # Usuarios
    path("users/", user_list_view, name="user_list"),
    path(
        "users/<int:user_id>/assign-organization/",
        assign_organization_view,
        name="assign_organization",
    ),

    # Organizaciones
    path("organizations/", organization_list_view, name="organization_list"),
    path("organizations/new/", organization_create_view, name="organization_create"),
    path(
        "organizations/<int:organization_id>/edit/",
        organization_update_view,
        name="organization_update",
    ),
]