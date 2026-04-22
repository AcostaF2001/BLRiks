from django import forms
from django.db import transaction

from .models import PROCESSINGRule


class PROCESSINGRuleForm(forms.ModelForm):
    """
    Formulario para crear o editar reglas de procesamiento.

    Regla de negocio adicional:
    si una regla se guarda como activa, se desactivan automáticamente
    las demás reglas activas de la misma organización.

    Con esto garantizamos que solo exista una regla activa por organización,
    evitando ambigüedad durante el procesamiento asíncrono.
    """

    class Meta:
        model = PROCESSINGRule
        fields = [
            "organization",
            "operation_type",
            "adjustment_value",
            "is_active",
        ]

    @transaction.atomic
    def save(self, commit=True):
        """
        Sobrescribe el guardado del formulario para imponer
        la regla de unicidad lógica de la regla activa por organización.
        """
        instance = super().save(commit=False)

        if commit:
            instance.save()

            # Si esta regla quedó activa, desactiva las demás reglas activas
            # de la misma organización.
            if instance.is_active:
                PROCESSINGRule.objects.filter(
                    organization=instance.organization,
                    is_active=True,
                ).exclude(id=instance.id).update(is_active=False)

            self.save_m2m()

        return instance