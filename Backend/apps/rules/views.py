from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.permissions import is_management_user, is_org_admin, is_superadmin
from apps.accounts.models import Organization
from .forms import PROCESSINGRuleForm
from .models import PROCESSINGRule


@login_required
@user_passes_test(is_management_user)
def rule_list_view(request):
    """
    Lista reglas según el nivel del usuario autenticado.

    Reglas:
    - superadmin: ve todas las reglas
    - admin_org: ve solo reglas de su organización
    """
    if is_superadmin(request.user):
        rules = PROCESSINGRule.objects.select_related("organization").all().order_by(
            "organization__name",
            "-updated_at",
        )
    else:
        rules = PROCESSINGRule.objects.select_related("organization").filter(
            organization=request.user.organization
        ).order_by("-updated_at")

    return render(request, "rules/rule_list.html", {"rules": rules})


@login_required
@user_passes_test(is_management_user)
def rule_create_view(request):
    """
    Permite crear reglas.

    Reglas:
    - superadmin: puede crear para cualquier organización
    - admin_org: solo puede crear para su propia organización
    """
    if request.method == "POST":
        form = PROCESSINGRuleForm(request.POST)

        # Si el usuario es ADMIN_ORG, restringimos el queryset
        # para que solo pueda elegir su propia organización.
        if is_org_admin(request.user):
            form.fields["organization"].queryset = Organization.objects.filter(
                id=request.user.organization_id
            )

        if form.is_valid():
            rule = form.save()
            messages.success(
                request,
                f"Regla creada correctamente para la organización '{rule.organization.name}'."
            )
            return redirect("rules:rule_list")
    else:
        form = PROCESSINGRuleForm()

        # Restricción para ADMIN_ORG en GET
        if is_org_admin(request.user):
            form.fields["organization"].queryset = Organization.objects.filter(
                id=request.user.organization_id
            )
            form.initial["organization"] = request.user.organization

    return render(
        request,
        "rules/rule_form.html",
        {
            "form": form,
            "title": "Crear regla",
        },
    )


@login_required
@user_passes_test(is_management_user)
def rule_update_view(request, rule_id):
    """
    Permite editar reglas.

    Reglas:
    - superadmin: puede editar cualquier regla
    - admin_org: solo puede editar reglas de su organización
    """
    if is_superadmin(request.user):
        rule = get_object_or_404(PROCESSINGRule, id=rule_id)
    else:
        rule = get_object_or_404(
            PROCESSINGRule,
            id=rule_id,
            organization=request.user.organization,
        )

    if request.method == "POST":
        form = PROCESSINGRuleForm(request.POST, instance=rule)

        # Restricción para ADMIN_ORG:
        # solo puede mantener la regla dentro de su propia organización.
        if is_org_admin(request.user):
            form.fields["organization"].queryset = Organization.objects.filter(
                id=request.user.organization_id
            )

        if form.is_valid():
            form.save()
            messages.success(request, "Regla actualizada correctamente.")
            return redirect("rules:rule_list")
    else:
        form = PROCESSINGRuleForm(instance=rule)

        if is_org_admin(request.user):
            form.fields["organization"].queryset = Organization.objects.filter(
                id=request.user.organization_id
            )

    return render(
        request,
        "rules/rule_form.html",
        {
            "form": form,
            "title": "Editar regla",
            "rule": rule,
        },
    )