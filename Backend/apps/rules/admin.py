from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import PROCESSINGRule


class PROCESSINGRuleAdminForm(ModelForm):
    """
    Formulario personalizado para el admin de PROCESSINGRule.

    Se usa para asegurar que en el admin también se ejecute
    la validación central del modelo, especialmente la regla de:
    solo una regla activa por organización.
    """

    class Meta:
        model = PROCESSINGRule
        fields = "__all__"

    def clean(self):
        """
        Ejecuta la validación completa del modelo dentro del admin.
        """
        cleaned_data = super().clean()

        instance = self.instance

        # Copiamos al instance los valores del formulario actual
        # para que full_clean() evalúe el estado real que se quiere guardar.
        instance.organization = cleaned_data.get("organization")
        instance.operation_type = cleaned_data.get("operation_type")
        instance.adjustment_value = cleaned_data.get("adjustment_value")
        instance.is_active = cleaned_data.get("is_active")

        try:
            instance.full_clean()
        except ValidationError as exc:
            self.add_error(None, exc)
            raise

        return cleaned_data


@admin.register(PROCESSINGRule)
class PROCESSINGRuleAdmin(admin.ModelAdmin):
    """
    Configuración del admin de reglas de procesamiento.

    Además de mostrar y filtrar información útil,
    este admin usa un formulario personalizado para impedir
    que se creen varias reglas activas para la misma organización.
    """

    form = PROCESSINGRuleAdminForm

    list_display = (
        "id",
        "organization",
        "operation_type",
        "adjustment_value",
        "is_active",
        "updated_at",
    )

    list_filter = ("operation_type", "is_active", "organization")
    search_fields = ("organization__name",)