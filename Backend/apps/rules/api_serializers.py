from rest_framework import serializers

from .models import PROCESSINGRule


class PROCESSINGRuleSerializer(serializers.ModelSerializer):
    """
    Serializer para exponer reglas de procesamiento en la API.
    """

    organization_name = serializers.CharField(source="organization.name", read_only=True)

    class Meta:
        model = PROCESSINGRule
        fields = [
            "id",
            "organization",
            "organization_name",
            "operation_type",
            "adjustment_value",
            "is_active",
            "created_at",
            "updated_at",
        ]