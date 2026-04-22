from celery import shared_task
from django.utils import timezone

from apps.results.mongo_client import get_mongo_database
from apps.rules.services import apply_rule_to_dataframe, get_active_rule_for_organization
from apps.uploads.models import ProcessingExecution, UploadedFile
from .services import process_uploaded_excel


@shared_task(bind=True)
def process_uploaded_file_task(self, execution_id):
    """
    Task asíncrona que procesa una ejecución/version específica.

    Flujo:
    1. recupera la ejecución y su archivo
    2. cambia estado a PROCESSING
    3. lee y limpia el Excel
    4. obtiene la regla activa de la organización
    5. aplica la regla al DataFrame
    6. elimina resultados previos solo de esta misma ejecución/version
    7. inserta resultados versionados en MongoDB
    8. actualiza la ejecución y también el resumen del UploadedFile

    Esto permite:
    - reprocesos versionados
    - historial por ejecución
    - evitar duplicados sin borrar el historial previo
    """
    execution = ProcessingExecution.objects.select_related(
        "uploaded_file",
        "uploaded_file__organization",
        "uploaded_file__uploaded_by",
        "triggered_by",
    ).get(id=execution_id)

    uploaded_file = execution.uploaded_file

    try:
        # ==========================================================
        # MARCAR EJECUCIÓN Y ARCHIVO COMO PROCESSING
        # ==========================================================
        now = timezone.now()

        execution.status = ProcessingExecution.Status.PROCESSING
        execution.error_message = ""
        execution.started_at = now
        execution.save(update_fields=["status", "error_message", "started_at"])

        uploaded_file.status = UploadedFile.Status.PROCESSING
        uploaded_file.error_message = ""
        uploaded_file.save(update_fields=["status", "error_message", "updated_at"])

        # ==========================================================
        # LEER Y LIMPIAR EL EXCEL
        # ==========================================================
        result = process_uploaded_excel(uploaded_file.original_file.path)

        df = result["dataframe"]
        total_rows = result["total_rows"]
        processed_rows = result["processed_rows"]

        # ==========================================================
        # OBTENER Y REGISTRAR REGLA ACTIVA
        # ==========================================================
        rule = get_active_rule_for_organization(uploaded_file.organization)
        execution.applied_rule = rule
        execution.save(update_fields=["applied_rule"])

        # ==========================================================
        # APLICAR REGLA DE NEGOCIO
        # ==========================================================
        df = apply_rule_to_dataframe(df, rule)

        # ==========================================================
        # MONGODB: GUARDADO VERSIONADO
        # ==========================================================
        db = get_mongo_database()
        collection = db["processed_results"]

        # Anti-duplicados:
        # borramos solo resultados de la misma ejecución/version si existieran
        collection.delete_many(
            {
                "uploaded_file_id": uploaded_file.id,
                "execution_id": execution.id,
                "execution_version": execution.version,
            }
        )

        documents = []

        for _, row in df.iterrows():
            valor_base = row.get("Valor_base")
            fecha_valor = row.get("Fecha")
            resultado = row.get("Resultado")

            documents.append(
                {
                    "uploaded_file_id": uploaded_file.id,
                    "execution_id": execution.id,
                    "execution_version": execution.version,

                    "organization_id": uploaded_file.organization.id,
                    "organization_name": uploaded_file.organization.name,
                    "uploaded_by_id": uploaded_file.uploaded_by.id,
                    "uploaded_by_username": uploaded_file.uploaded_by.username,
                    "triggered_by_id": execution.triggered_by.id,
                    "triggered_by_username": execution.triggered_by.username,

                    "original_data": {
                        "Identificador": row.get("Identificador"),
                        "Nombre": row.get("Nombre"),
                        "Valor_base": None if valor_base is None else (
                            float(valor_base) if valor_base == valor_base else None
                        ),
                        "Categoría": row.get("Categoría"),
                        "Fecha": None if fecha_valor is None else str(fecha_valor),
                    },

                    "transformed_data": {
                        "Operacion_aplicada": row.get("Operacion_aplicada"),
                        "Ajuste_aplicado": row.get("Ajuste_aplicado"),
                        "Resultado": None if resultado is None else (
                            float(resultado) if resultado == resultado else None
                        ),
                    },

                    "applied_rule": {
                        "rule_id": rule.id,
                        "operation_type": rule.operation_type,
                        "adjustment_value": float(rule.adjustment_value),
                        "is_active": rule.is_active,
                    },

                    "PROCESSING_metadata": {
                        "processed_at": timezone.now().isoformat(),
                        "status": "PROCESSED",
                        "source_filename": uploaded_file.original_filename,
                    },
                }
            )

        if documents:
            collection.insert_many(documents)

        # ==========================================================
        # ACTUALIZAR EJECUCIÓN
        # ==========================================================
        FINALIZADO_at = timezone.now()

        execution.status = ProcessingExecution.Status.FINALIZADO
        execution.total_rows = total_rows
        execution.processed_rows = processed_rows
        execution.error_message = ""
        execution.FINALIZADO_at = FINALIZADO_at
        execution.save(
            update_fields=[
                "status",
                "total_rows",
                "processed_rows",
                "error_message",
                "FINALIZADO_at",
            ]
        )

        # ==========================================================
        # ACTUALIZAR RESUMEN DEL ARCHIVO PRINCIPAL
        # ==========================================================
        uploaded_file.status = UploadedFile.Status.FINALIZADO
        uploaded_file.total_rows = total_rows
        uploaded_file.processed_rows = processed_rows
        uploaded_file.processed_at = FINALIZADO_at
        uploaded_file.error_message = ""
        uploaded_file.current_version = execution.version
        uploaded_file.save(
            update_fields=[
                "status",
                "total_rows",
                "processed_rows",
                "processed_at",
                "error_message",
                "current_version",
                "updated_at",
            ]
        )

    except Exception as exc:
        failed_at = timezone.now()

        execution.status = ProcessingExecution.Status.ERROR
        execution.error_message = str(exc)
        execution.FINALIZADO_at = failed_at
        execution.save(
            update_fields=[
                "status",
                "error_message",
                "FINALIZADO_at",
            ]
        )

        uploaded_file.status = UploadedFile.Status.ERROR
        uploaded_file.error_message = str(exc)
        uploaded_file.processed_at = failed_at
        uploaded_file.current_version = execution.version
        uploaded_file.save(
            update_fields=[
                "status",
                "error_message",
                "processed_at",
                "current_version",
                "updated_at",
            ]
        )

        raise