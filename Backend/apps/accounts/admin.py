from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Organization, User


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """
    Configuración del modelo Organization dentro del admin.
    """
    list_display = ("id", "name", "slug", "is_active", "created_at")
    search_fields = ("name", "slug")
    list_filter = ("is_active",)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Configuración del usuario personalizado dentro del admin.
    """
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Datos del sistema", {"fields": ("organization", "user_type")}),
    )

    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "organization",
        "user_type",
        "is_staff",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "organization", "user_type")