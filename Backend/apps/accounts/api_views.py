from django.contrib.auth import get_user_model, login
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import is_management_user, is_org_admin, is_superadmin
from .api_serializers import (
    AssignOrganizationSerializer,
    OrganizationSerializer,
    UserRegisterSerializer,
    UserSerializer,
)
from .models import Organization

User = get_user_model()


class CurrentUserAPIView(APIView):
    """
    Devuelve la información del usuario autenticado actual.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Usuario autenticado actual",
        description="Devuelve la información del usuario que tiene la sesión activa.",
        responses=UserSerializer,
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserRegisterAPIView(APIView):
    """
    Registro público de usuarios.

    Permite:
    - crear cuenta
    - asignar tipo de usuario funcional
    - seleccionar organización existente o crear una nueva
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Registrar usuario",
        description=(
            "Crea una cuenta nueva y permite asociarla a una organización existente "
            "o crear una nueva organización en el mismo flujo."
        ),
        request=UserRegisterSerializer,
        responses={201: UserSerializer},
    )
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Opcionalmente iniciamos sesión para mantener coherencia con la interfaz web.
        login(request, user)

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class UserListAPIView(generics.ListAPIView):
    """
    Lista usuarios según el rol del usuario autenticado.

    Reglas:
    - superadmin: ve todos los usuarios
    - ADMIN_ORG: ve solo usuarios de su organización
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Listar usuarios",
        description=(
            "Lista usuarios según el contexto del usuario autenticado. "
            "Superadmin ve todos; ADMIN_ORG ve solo su organización."
        ),
        responses=UserSerializer(many=True),
    )
    def get(self, request, *args, **kwargs):
        if not is_management_user(request.user):
            return Response(
                {"detail": "No tienes permisos para consultar usuarios."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if is_superadmin(self.request.user):
            return User.objects.select_related("organization").all().order_by("username")

        return User.objects.select_related("organization").filter(
            organization=self.request.user.organization
        ).order_by("username")


class OrganizationListAPIView(generics.ListAPIView):
    """
    Lista organizaciones.

    Regla:
    - solo superadmin puede ver todas las organizaciones
    """
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Listar organizaciones",
        description="Devuelve el listado completo de organizaciones. Solo superadmin.",
        responses=OrganizationSerializer(many=True),
    )
    def get(self, request, *args, **kwargs):
        if not is_superadmin(request.user):
            return Response(
                {"detail": "No tienes permisos para consultar organizaciones."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Organization.objects.all().order_by("name")


class AssignOrganizationAPIView(APIView):
    """
    Asigna o cambia la organización de un usuario.

    Reglas:
    - superadmin: puede cambiar cualquier usuario a cualquier organización
    - ADMIN_ORG: solo puede gestionar usuarios de su organización
      y solo reasignarlos dentro de su misma organización
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Asignar organización a usuario",
        description=(
            "Permite cambiar la organización de un usuario. "
            "Superadmin tiene alcance global; ADMIN_ORG solo dentro de su organización."
        ),
        request=AssignOrganizationSerializer,
        responses=UserSerializer,
    )
    def patch(self, request, user_id):
        if not is_management_user(request.user):
            return Response(
                {"detail": "No tienes permisos para gestionar usuarios."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if is_superadmin(request.user):
            user_obj = User.objects.filter(id=user_id).select_related("organization").first()
        else:
            user_obj = User.objects.filter(
                id=user_id,
                organization=request.user.organization,
            ).select_related("organization").first()

        if not user_obj:
            return Response(
                {"detail": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AssignOrganizationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        organization = serializer.validated_data["organization"]

        if is_org_admin(request.user) and organization.id != request.user.organization_id:
            return Response(
                {"detail": "Solo puedes asignar usuarios dentro de tu propia organización."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user_obj.organization = organization
        user_obj.save(update_fields=["organization"])

        return Response(UserSerializer(user_obj).data, status=status.HTTP_200_OK)