from django.contrib.auth.models import AbstractUser
from django.db import models


class Organization(models.Model):
    """
    Representa una organización dentro del sistema.

    Cada usuario pertenece a una organización y toda la información
    debe filtrarse según este contexto organizacional.
    """
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Usuario personalizado del sistema.

    Extiende el usuario nativo de Django para:
    - asociarlo a una organización
    - definir un tipo de usuario funcional dentro de la plataforma

    Nota:
    Esto NO reemplaza los permisos internos de Django como:
    - is_staff
    - is_superuser

    El campo user_type se usa como clasificación de negocio
    dentro de la aplicación.
    """

    class UserType(models.TextChoices):
        """
        Tipos funcionales de usuario dentro del sistema.
        """
        ADMIN_ORG = "ADMIN_ORG", "Administrador de organización"
        ANALYST = "ANALYST", "Analista"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
    )

    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.ANALYST,
    )

    def __str__(self):
        return self.username