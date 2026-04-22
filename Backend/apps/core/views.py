from django.shortcuts import redirect


def home_redirect_view(request):
    """
    Redirección principal del sistema.

    Comportamiento:
    - si el usuario ya está autenticado, lo enviamos al listado de uploads
    - si no está autenticado, lo enviamos al login

    Esto hace que acceder a "/" tenga un comportamiento claro
    y consistente con el flujo de la aplicación.
    """
    if request.user.is_authenticated:
        return redirect("uploads:list")

    return redirect("login")