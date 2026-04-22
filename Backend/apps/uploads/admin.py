from django.contrib import admin

from .models import UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    """
    Configuración del modelo UploadedFile dentro del admin de Django.

    Este admin permite:
    - visualizar rápidamente archivos cargados
    - revisar su estado
    - filtrar por organización, fecha o estado
    - buscar por nombre de archivo, usuario u organización
    """

    # Columnas visibles en el listado del admin
    list_display = (
        "id",
        "original_filename",
        "organization",
        "uploaded_by",
        "status",
        "total_rows",
        "processed_rows",
        "uploaded_at",
        "processed_at",
    )

    # Filtros laterales para facilitar la exploración en admin
    list_filter = ("status", "organization", "uploaded_at")

    # Campos sobre los que se puede buscar
    search_fields = ("original_filename", "uploaded_by__username", "organization__name")