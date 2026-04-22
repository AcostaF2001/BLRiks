from apps.accounts.permissions import is_management_user, is_org_admin, is_superadmin


def navigation_context(request):
    """
    Context processor para exponer información de navegación
    y permisos básicos a todos los templates.

    Esto permite que la barra de navegación muestre enlaces
    según el tipo de usuario autenticado.
    """
    user = getattr(request, "user", None)

    return {
        "nav_is_authenticated": bool(user and user.is_authenticated),
        "nav_is_superadmin": is_superadmin(user) if user else False,
        "nav_is_org_admin": is_org_admin(user) if user else False,
        "nav_is_management_user": is_management_user(user) if user else False,
    }