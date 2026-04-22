from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.results.mongo_client import get_mongo_database
from apps.uploads.models import UploadedFile


class UploadedFileResultsAPIView(APIView):
    """
    Devuelve resultados procesados de un archivo por versión.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Consultar resultados de un archivo",
        description=(
            "Devuelve los resultados procesados del archivo. "
            "Si no se envía versión, usa la versión actual."
        ),
        parameters=[
            OpenApiParameter(
                name="version",
                description="Versión específica del procesamiento a consultar",
                required=False,
                type=int,
            )
        ],
    )
    def get(self, request, uploaded_file_id):
        uploaded_file = UploadedFile.objects.select_related("organization").filter(
            id=uploaded_file_id,
            organization=request.user.organization,
        ).first()

        if not uploaded_file:
            return Response({"detail": "Archivo no encontrado."}, status=404)

        requested_version = request.GET.get("version")
        selected_version = uploaded_file.current_version

        if requested_version:
            try:
                selected_version = int(requested_version)
            except ValueError:
                selected_version = uploaded_file.current_version

        db = get_mongo_database()
        collection = db["processed_results"]

        results = list(
            collection.find(
                {
                    "uploaded_file_id": uploaded_file.id,
                    "execution_version": selected_version,
                },
                {"_id": 0},
            )
        )

        return Response(
            {
                "uploaded_file_id": uploaded_file.id,
                "filename": uploaded_file.original_filename,
                "current_version": uploaded_file.current_version,
                "selected_version": selected_version,
                "results": results,
            }
        )