from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.utils.text import slugify

from .models import Organization

User = get_user_model()


class AssignOrganizationForm(forms.ModelForm):
    """
    Formulario para asignar o cambiar la organización de un usuario.

    Se usa por superadministradores para administración manual.
    """

    class Meta:
        model = User
        fields = ["organization"]


class OrganizationForm(forms.ModelForm):
    """
    Formulario para crear o editar organizaciones desde la interfaz administrativa.
    """

    class Meta:
        model = Organization
        fields = ["name", "slug", "is_active"]


class UserRegisterForm(UserCreationForm):
    """
    Formulario de registro público del sistema.

    Objetivo:
    permitir que un usuario cree su cuenta y, en el mismo flujo:
    - seleccione una organización existente
    - o cree una nueva organización

    Reglas:
    - no puede crear superusuarios
    - el tipo de usuario es funcional, no administrativo de Django
    - debe elegir organización existente o crear una nueva
    """

    email = forms.EmailField(required=True)

    user_type = forms.ChoiceField(
        choices=User.UserType.choices,
        required=True,
        label="Tipo de usuario",
    )

    organization = forms.ModelChoiceField(
        queryset=Organization.objects.filter(is_active=True).order_by("name"),
        required=False,
        empty_label="Selecciona una organización existente",
        label="Organización existente",
    )

    new_organization_name = forms.CharField(
        required=False,
        label="Nueva organización",
        help_text="Si no seleccionas una organización existente, puedes crear una nueva aquí.",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "user_type",
            "organization",
            "new_organization_name",
            "password1",
            "password2",
        ]

    def clean(self):
        """
        Valida la coherencia del formulario.

        Reglas:
        - el usuario debe escoger una organización existente o escribir una nueva
        - no debe hacer ambas cosas al mismo tiempo
        """
        cleaned_data = super().clean()

        organization = cleaned_data.get("organization")
        new_organization_name = cleaned_data.get("new_organization_name")

        if not organization and not new_organization_name:
            raise forms.ValidationError(
                "Debes seleccionar una organización existente o crear una nueva."
            )

        if organization and new_organization_name:
            raise forms.ValidationError(
                "Debes elegir solo una opción: seleccionar organización existente o crear una nueva."
            )

        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        """
        Guarda el usuario y, si aplica, crea también la organización.

        Flujo:
        - si el usuario eligió una organización existente, se usa esa
        - si escribió una nueva, se crea automáticamente con slug generado
        - luego se crea el usuario asociado a esa organización
        """
        user = super().save(commit=False)

        organization = self.cleaned_data.get("organization")
        new_organization_name = self.cleaned_data.get("new_organization_name")

        if not organization and new_organization_name:
            base_slug = slugify(new_organization_name)
            slug = base_slug
            counter = 1

            while Organization.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            organization = Organization.objects.create(
                name=new_organization_name,
                slug=slug,
                is_active=True,
            )

        user.email = self.cleaned_data["email"]
        user.user_type = self.cleaned_data["user_type"]
        user.organization = organization

        # Registro público: no staff, no superuser.
        user.is_staff = False
        user.is_superuser = False

        if commit:
            user.save()

        return user