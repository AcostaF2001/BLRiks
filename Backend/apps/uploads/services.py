from django.db import transaction
from django.db.models import Max

from .models import ProcessingExecution, UploadedFile


@transaction.atomic
def create_processing_execution(uploaded_file: UploadedFile, triggered_by):
    """
    Crea una nueva ejecución/version para un archivo.

    Flujo:
    - consulta la última versión existente del archivo
    - calcula la siguiente versión incremental
    - crea un nuevo registro de PROCESSING
    - actualiza el archivo principal con esa versión como actual

    Esto permite:
    - reprocesar sin volver a subir el archivo
    - mantener trazabilidad por versión
    - evitar duplicados entre ejecuciones distintas
    """
    last_version = (
        uploaded_file.executions.aggregate(max_version=Max("version")).get("max_version") or 0
    )
    next_version = last_version + 1

    execution = ProcessingExecution.objects.create(
        uploaded_file=uploaded_file,
        version=next_version,
        status=ProcessingExecution.Status.PENDING,
        triggered_by=triggered_by,
    )

    uploaded_file.current_version = next_version
    uploaded_file.status = UploadedFile.Status.PENDING
    uploaded_file.error_message = ""
    uploaded_file.total_rows = 0
    uploaded_file.processed_rows = 0
    uploaded_file.processed_at = None
    uploaded_file.save(
        update_fields=[
            "current_version",
            "status",
            "error_message",
            "total_rows",
            "processed_rows",
            "processed_at",
            "updated_at",
        ]
    )

    return execution