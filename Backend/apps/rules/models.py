from django.core.exceptions import ValidationError
from django.db import models


class PROCESSINGRule(models.Model):
    """
    Modelo que representa una regla de negocio configurable por organización.

    Cada organización puede tener reglas históricas o inactivas,
    pero solo debe existir una regla activa al mismo tiempo.

    Esta regla de unicidad lógica se valida en el método clean().
    """

    class OperationType(models.TextChoices):
        """
        Operaciones soportadas por el sistema para transformar Valor_base.
        """
        SUM = "SUM", "Suma"
        SUBTRACT = "SUBTRACT", "Resta"
        MEAN = "MEAN", "Media aritmética"

    # Organización a la que pertenece la regla
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="PROCESSING_rules",
    )

    # Tipo de operación a aplicar
    operation_type = models.CharField(
        max_length=20,
        choices=OperationType.choices,
    )

    # Valor de ajuste utilizado por las operaciones SUM y SUBTRACT
    adjustment_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    # Indica si esta regla está activa
    is_active = models.BooleanField(default=True)

    # Campos de trazabilidad
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "PROCESSING Rule"
        verbose_name_plural = "PROCESSING Rules"

    def clean(self):
        """
        Valida reglas de negocio antes de guardar.

        Regla principal:
        - solo puede existir una regla activa por organización

        Si esta instancia se intenta guardar como activa y ya existe
        otra regla activa para la misma organización, se lanza un error.
        """
        super().clean()

        if self.is_active and self.organization_id:
            existing_active_rule = PROCESSINGRule.objects.filter(
                organization=self.organization,
                is_active=True,
            ).exclude(id=self.id)

            if existing_active_rule.exists():
                raise ValidationError(
                    {
                        "is_active": (
                            "Ya existe otra regla activa para esta organización. "
                            "Desactívala antes de activar una nueva."
                        )
                    }
                )

    def __str__(self):
        """
        Representación amigable de la regla.
        """
        return f"{self.organization.name} - {self.operation_type} - Active: {self.is_active}"