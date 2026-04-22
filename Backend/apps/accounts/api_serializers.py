from django.contrib.auth import get_user_model
from rest_framework import serializers

from .forms import UserRegisterForm
from .models import Organization

User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Serializer para exponer organizaciones en la API.
    """

    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "slug",
            "is_active",
            "created_at",
        ]


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para exponer usuarios del sistema.

    Incluye información legible de organización y tipo de usuario
    para facilitar la consulta en Swagger y en clientes API.
    """

    organization_name = serializers.CharField(source="organization.name", read_only=True)
    user_type_display = serializers.CharField(source="get_user_type_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "organization",
            "organization_name",
            "user_type",
            "user_type_display",
            "is_staff",
            "is_superuser",
        ]


class UserRegisterSerializer(serializers.Serializer):
    """
    Serializer para documentar y procesar el registro público de usuarios.

    Reutiliza internamente la lógica del formulario existente para:
    - crear usuario
    - seleccionar organización existente o crear una nueva
    - asignar tipo de usuario
    """

    username = serializers.CharField()
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField()
    user_type = serializers.ChoiceField(choices=User.UserType.choices)

    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )

    new_organization_name = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Reutiliza el formulario de Django para centralizar reglas de validación.
        """
        form = UserRegisterForm(data=attrs)

        if not form.is_valid():
            raise serializers.ValidationError(form.errors)

        self._validated_form = form
        return attrs

    def create(self, validated_data):
        """
        Crea el usuario usando la lógica ya existente en el formulario.
        """
        return self._validated_form.save()


class AssignOrganizationSerializer(serializers.Serializer):
    """
    Serializer para asignar o cambiar la organización de un usuario.
    """
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.filter(is_active=True)
    )