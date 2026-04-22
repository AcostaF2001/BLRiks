from django.contrib.auth import get_user_model

User = get_user_model()


def is_superadmin(user):
    """
    Valida si el usuario autenticado es superusuario del sistema.

    Este rol tiene acceso global a todos los módulos administrativos.
    """
    return user.is_authenticated and user.is_superuser


def is_org_admin(user):
    """
    Valida si el usuario autenticado es administrador de organización.

    Este rol no es superusuario de Django, pero sí puede gestionar
    recursos internos de su propia organización.
    """
    return (
        user.is_authenticated
        and not user.is_superuser
        and getattr(user, "user_type", None) == User.UserType.ADMIN_ORG
    )


def is_management_user(user):
    """
    Valida si el usuario tiene permisos de gestión.

    Se considera usuario de gestión si es:
    - superadmin
    - administrador de organización
    """
    return is_superadmin(user) or is_org_admin(user)