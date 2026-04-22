from decimal import Decimal

from apps.rules.models import PROCESSINGRule


def get_active_rule_for_organization(organization):
    """
    Retorna la regla activa de una organización.

    Política actual:
    - se espera que exista solo una regla activa por organización
    - esto se fuerza desde el formulario de administración
    - si por alguna inconsistencia existieran varias activas,
      se toma la más recientemente actualizada como fallback defensivo
    """
    rule = (
        PROCESSINGRule.objects.filter(
            organization=organization,
            is_active=True,
        )
        .order_by("-updated_at")
        .first()
    )

    if not rule:
        raise ValueError(
            f"La organización '{organization.name}' no tiene una regla activa configurada."
        )

    return rule


def apply_rule_to_dataframe(df, rule):
    """
    Aplica la regla de negocio sobre el DataFrame.

    Operaciones soportadas:
    - SUM
    - SUBTRACT
    - MEAN

    Se agregan columnas de trazabilidad al DataFrame:
    - Operacion_aplicada
    - Ajuste_aplicado
    - Resultado
    """
    df = df.copy()

    adjustment_value = float(Decimal(rule.adjustment_value))

    df["Operacion_aplicada"] = rule.operation_type
    df["Ajuste_aplicado"] = adjustment_value

    if rule.operation_type == PROCESSINGRule.OperationType.SUM:
        df["Resultado"] = df["Valor_base"] + adjustment_value

    elif rule.operation_type == PROCESSINGRule.OperationType.SUBTRACT:
        df["Resultado"] = df["Valor_base"] - adjustment_value

    elif rule.operation_type == PROCESSINGRule.OperationType.MEAN:
        mean_value = df["Valor_base"].mean()
        df["Resultado"] = mean_value

    else:
        raise ValueError(f"Operación no soportada: {rule.operation_type}")

    return df