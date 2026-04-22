from rest_framework import serializers

from .models import ProcessingExecution, UploadedFile


class ProcessingExecutionSerializer(serializers.ModelSerializer):
    """
    Serializer del historial de ejecuciones/versiones de un archivo.
    """

    triggered_by_username = serializers.CharField(source="triggered_by.username", read_only=True)
    applied_rule_operation = serializers.CharField(source="applied_rule.operation_type", read_only=True)

    class Meta:
        model = ProcessingExecution
        fields = [
            "id",
            "version",
            "status",
            "triggered_by_username",
            "applied_rule_operation",
            "total_rows",
            "processed_rows",
            "error_message",
            "created_at",
            "started_at",
            "finished_at",
        ]


class UploadedFileSerializer(serializers.ModelSerializer):
    """
    Serializer del archivo cargado.
    Incluye resumen del estado actual y contexto básico.
    """

    organization_name = serializers.CharField(source="organization.name", read_only=True)
    uploaded_by_username = serializers.CharField(source="uploaded_by.username", read_only=True)

    class Meta:
        model = UploadedFile
        fields = [
            "id",
            "original_filename",
            "status",
            "current_version",
            "organization_name",
            "uploaded_by_username",
            "total_rows",
            "processed_rows",
            "error_message",
            "uploaded_at",
            "processed_at",
        ]