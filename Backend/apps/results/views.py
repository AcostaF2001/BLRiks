from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from apps.results.mongo_client import get_mongo_database
from apps.uploads.models import ProcessingExecution, UploadedFile


@login_required
def uploaded_file_results_view(request, uploaded_file_id):
    """
    Muestra resultados procesados de un archivo con soporte de versionamiento.

    Comportamiento:
    - si no se envía query param version, muestra la versión actual
    - si se envía ?version=N, muestra esa versión específica
    - además carga el historial de ejecuciones del archivo para navegarlo

    Seguridad:
    - solo se permite consultar archivos de la organización del usuario autenticado
    """
    uploaded_file = get_object_or_404(
        UploadedFile.objects.select_related("organization", "uploaded_by"),
        id=uploaded_file_id,
        organization=request.user.organization,
    )

    # ==========================================================
    # DETERMINAR VERSIÓN A CONSULTAR
    # ==========================================================
    requested_version = request.GET.get("version")

    if requested_version:
        try:
            selected_version = int(requested_version)
        except ValueError:
            selected_version = uploaded_file.current_version
    else:
        selected_version = uploaded_file.current_version

    # ==========================================================
    # HISTORIAL DE VERSIONES
    # ==========================================================
    executions = uploaded_file.executions.select_related(
        "triggered_by",
        "applied_rule",
    ).all().order_by("-version")

    # Si la versión pedida no existe, usamos la actual
    if not executions.filter(version=selected_version).exists():
        selected_version = uploaded_file.current_version

    selected_execution = executions.filter(version=selected_version).first()

    # ==========================================================
    # CONSULTA A MONGODB
    # ==========================================================
    db = get_mongo_database()
    collection = db["processed_results"]

    results_cursor = collection.find(
        {
            "uploaded_file_id": uploaded_file.id,
            "execution_version": selected_version,
        },
        {"_id": 0},
    )

    results = list(results_cursor)

    context = {
        "uploaded_file": uploaded_file,
        "results": results,
        "executions": executions,
        "selected_version": selected_version,
        "selected_execution": selected_execution,
    }

    return render(request, "results/uploaded_file_results.html", context)