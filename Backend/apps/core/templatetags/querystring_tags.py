from django import template

register = template.Library()


@register.simple_tag
def update_query_params(request, **kwargs):
    """
    Construye un querystring conservando los filtros actuales
    y reemplazando solo los parámetros indicados.

    Se usa especialmente para la paginación, de modo que al cambiar
    de página no se pierdan los filtros activos.
    """
    query_params = request.GET.copy()

    for key, value in kwargs.items():
        if value is None or value == "":
            query_params.pop(key, None)
        else:
            query_params[key] = value

    encoded = query_params.urlencode()
    return f"?{encoded}" if encoded else ""