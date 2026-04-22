from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.permissions import is_management_user, is_org_admin, is_superadmin
from .forms import AssignOrganizationForm, OrganizationForm, UserRegisterForm
from .models import Organization

User = get_user_model()


def register_view(request):
    """
    Vista de registro público del sistema.
    """
    if request.user.is_authenticated:
        return redirect("uploads:list")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Tu cuenta fue creada correctamente.")
            return redirect("uploads:list")
    else:
        form = UserRegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
@user_passes_test(is_management_user)
def user_list_view(request):
    """
    Lista usuarios con filtros y paginación.

    Filtros soportados:
    - nombre: busca por username, first_name y last_name
    - user_type: filtra por tipo funcional de usuario
    - email: filtra por correo

    Reglas de acceso:
    - superadmin: ve todos los usuarios
    - admin_org: ve solo usuarios de su organización

    Las búsquedas de texto usan:
    - unaccent: ignora acentos
    - icontains: ignora mayúsculas/minúsculas
    """
    name_query = request.GET.get("name", "").strip()
    user_type_query = request.GET.get("user_type", "").strip()
    email_query = request.GET.get("email", "").strip()

    if is_superadmin(request.user):
        queryset = User.objects.select_related("organization").all()
    else:
        queryset = User.objects.select_related("organization").filter(
            organization=request.user.organization
        )

    # Filtro por nombre (username, nombre o apellido)
    if name_query:
        queryset = queryset.filter(
            Q(username__unaccent__icontains=name_query)
            | Q(first_name__unaccent__icontains=name_query)
            | Q(last_name__unaccent__icontains=name_query)
        )

    # Filtro por tipo de usuario
    if user_type_query:
        queryset = queryset.filter(user_type=user_type_query)

    # Filtro por correo
    if email_query:
        queryset = queryset.filter(email__unaccent__icontains=email_query)

    queryset = queryset.order_by("username")

    # Paginación
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "users": page_obj,
        "page_obj": page_obj,
        "name_query": name_query,
        "user_type_query": user_type_query,
        "email_query": email_query,
        "user_type_choices": User.UserType.choices,
    }

    return render(request, "accounts/user_list.html", context)


@login_required
@user_passes_test(is_management_user)
def assign_organization_view(request, user_id):
    """
    Permite cambiar la organización de un usuario.
    """
    if is_superadmin(request.user):
        user_obj = get_object_or_404(User, id=user_id)
    else:
        user_obj = get_object_or_404(
            User,
            id=user_id,
            organization=request.user.organization,
        )

    if request.method == "POST":
        form = AssignOrganizationForm(request.POST, instance=user_obj)

        if is_org_admin(request.user):
            form.fields["organization"].queryset = Organization.objects.filter(
                id=request.user.organization_id
            )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Organización actualizada para el usuario {user_obj.username}."
            )
            return redirect("accounts:user_list")
    else:
        form = AssignOrganizationForm(instance=user_obj)

        if is_org_admin(request.user):
            form.fields["organization"].queryset = Organization.objects.filter(
                id=request.user.organization_id
            )

    return render(
        request,
        "accounts/assign_organization.html",
        {
            "form": form,
            "user_obj": user_obj,
        },
    )


@login_required
@user_passes_test(is_superadmin)
def organization_list_view(request):
    organizations = Organization.objects.all().order_by("name")

    return render(
        request,
        "accounts/organization_list.html",
        {"organizations": organizations},
    )


@login_required
@user_passes_test(is_superadmin)
def organization_create_view(request):
    if request.method == "POST":
        form = OrganizationForm(request.POST)

        if form.is_valid():
            organization = form.save()
            messages.success(
                request,
                f"Organización '{organization.name}' creada correctamente."
            )
            return redirect("accounts:organization_list")
    else:
        form = OrganizationForm()

    return render(
        request,
        "accounts/organization_form.html",
        {
            "form": form,
            "title": "Crear organización",
        },
    )


@login_required
@user_passes_test(is_superadmin)
def organization_update_view(request, organization_id):
    organization = get_object_or_404(Organization, id=organization_id)

    if request.method == "POST":
        form = OrganizationForm(request.POST, instance=organization)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Organización '{organization.name}' actualizada correctamente."
            )
            return redirect("accounts:organization_list")
    else:
        form = OrganizationForm(instance=organization)

    return render(
        request,
        "accounts/organization_form.html",
        {
            "form": form,
            "title": "Editar organización",
            "organization": organization,
        },
    )