from django.urls import path

from .views import uploaded_file_results_view

# Namespace de la app para mantener las rutas organizadas
app_name = "results"

urlpatterns = [
    # Muestra los resultados procesados de un archivo específico
    path(
        "uploaded-file/<int:uploaded_file_id>/",
        uploaded_file_results_view,
        name="uploaded_file_results",
    ),
]