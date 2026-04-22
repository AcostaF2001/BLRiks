from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.processing.tasks import process_uploaded_file_task
from .forms import UploadedFileForm
from .models import UploadedFile
from .services import create_processing_execution


@login_required
def upload_file_view(request):
    """
    Carga un nuevo archivo y crea automáticamente su ejecución inicial (v1).
    """
    if not request.user.organization:
        messages.warning(
            request,
            "Tu usuario no tiene una organización asignada. Contacta a un administrador."
        )
        return redirect("uploads:list")

    if request.method == "POST":
        form = UploadedFileForm(request.POST, request.FILES)

        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.uploaded_by = request.user
            uploaded_file.organization = request.user.organization
            uploaded_file.original_filename = request.FILES["original_file"].name
            uploaded_file.status = UploadedFile.Status.PENDING
            uploaded_file.current_version = 0
            uploaded_file.save()

            execution = create_processing_execution(
                uploaded_file=uploaded_file,
                triggered_by=request.user,
            )

            process_uploaded_file_task.delay(execution.id)

            messages.success(
                request,
                "Archivo cargado correctamente. Se creó la versión 1 del procesamiento."
            )
            return redirect("uploads:list")
    else:
        form = UploadedFileForm()

    return render(request, "uploads/upload_file.html", {"form": form})


@login_required
def uploaded_file_list_view(request):
    """
    Lista archivos de la organización del usuario autenticado
    con filtros y paginación.

    Filtros soportados:
    - filename: nombre del archivo
    - username: usuario que subió el archivo

    Las búsquedas usan:
    - unaccent: ignora acentos
    - icontains: ignora mayúsculas/minúsculas
    """
    filename_query = request.GET.get("filename", "").strip()
    username_query = request.GET.get("username", "").strip()

    queryset = UploadedFile.objects.none()

    if request.user.organization:
        queryset = UploadedFile.objects.filter(
            organization=request.user.organization
        ).select_related("organization", "uploaded_by")

    # Filtro por nombre de archivo
    if filename_query:
        queryset = queryset.filter(
            original_filename__unaccent__icontains=filename_query
        )

    # Filtro por nombre de usuario que subió el archivo
    if username_query:
        queryset = queryset.filter(
            Q(uploaded_by__username__unaccent__icontains=username_query)
            | Q(uploaded_by__first_name__unaccent__icontains=username_query)
            | Q(uploaded_by__last_name__unaccent__icontains=username_query)
        )

    queryset = queryset.order_by("-uploaded_at")

    # Paginación
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "files": page_obj,
        "page_obj": page_obj,
        "filename_query": filename_query,
        "username_query": username_query,
    }

    return render(request, "uploads/uploaded_file_list.html", context)


@login_required
def reprocess_uploaded_file_view(request, uploaded_file_id):
    """
    Reprocesa un archivo ya existente creando una nueva versión.
    """
    uploaded_file = get_object_or_404(
        UploadedFile,
        id=uploaded_file_id,
        organization=request.user.organization,
    )

    execution = create_processing_execution(
        uploaded_file=uploaded_file,
        triggered_by=request.user,
    )

    process_uploaded_file_task.delay(execution.id)

    messages.success(
        request,
        f"Se lanzó el reproceso del archivo '{uploaded_file.original_filename}' en la versión {execution.version}."
    )
    return redirect("uploads:list")