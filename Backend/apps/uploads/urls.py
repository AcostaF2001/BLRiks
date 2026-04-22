from django.urls import path

from .views import (
    reprocess_uploaded_file_view,
    upload_file_view,
    uploaded_file_list_view,
)

app_name = "uploads"

urlpatterns = [
    # Lista de archivos cargados
    path("", uploaded_file_list_view, name="list"),

    # Carga de un nuevo archivo
    path("new/", upload_file_view, name="upload"),

    # Reprocesa un archivo existente creando una nueva versión
    path(
        "<int:uploaded_file_id>/reprocess/",
        reprocess_uploaded_file_view,
        name="reprocess",
    ),
]