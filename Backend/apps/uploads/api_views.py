from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .api_serializers import ProcessingExecutionSerializer, UploadedFileSerializer
from .models import ProcessingExecution, UploadedFile
from .services import create_processing_execution
from apps.processing.tasks import process_uploaded_file_task


class UploadedFileListAPIView(generics.ListAPIView):
    """
    Lista archivos de la organización del usuario autenticado.
    """
    serializer_class = UploadedFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UploadedFile.objects.filter(
            organization=self.request.user.organization
        ).select_related("organization", "uploaded_by").order_by("-uploaded_at")


class UploadedFileExecutionListAPIView(generics.ListAPIView):
    """
    Lista historial de ejecuciones/versiones de un archivo.
    """
    serializer_class = ProcessingExecutionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        uploaded_file_id = self.kwargs["uploaded_file_id"]
        return ProcessingExecution.objects.filter(
            uploaded_file_id=uploaded_file_id,
            uploaded_file__organization=self.request.user.organization,
        ).select_related("triggered_by", "applied_rule").order_by("-version")


class ReprocessResponseSerializer(serializers.Serializer):
    """
    Serializer de respuesta para el endpoint de reproceso.
    """
    message = serializers.CharField()
    uploaded_file_id = serializers.IntegerField()
    execution_id = serializers.IntegerField()
    version = serializers.IntegerField()


class UploadedFileReprocessAPIView(APIView):
    """
    Crea una nueva versión de procesamiento para un archivo ya existente.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Reprocesar archivo",
        description=(
            "Crea una nueva ejecución/version del archivo ya cargado, "
            "sin volver a subir el archivo físico."
        ),
        responses={200: ReprocessResponseSerializer},
    )
    def post(self, request, uploaded_file_id):
        uploaded_file = generics.get_object_or_404(
            UploadedFile,
            id=uploaded_file_id,
            organization=request.user.organization,
        )

        execution = create_processing_execution(
            uploaded_file=uploaded_file,
            triggered_by=request.user,
        )

        process_uploaded_file_task.delay(execution.id)

        return Response(
            {
                "message": "Reproceso lanzado correctamente.",
                "uploaded_file_id": uploaded_file.id,
                "execution_id": execution.id,
                "version": execution.version,
            },
            status=status.HTTP_200_OK,
        )