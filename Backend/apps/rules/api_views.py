from rest_framework import generics, permissions

from apps.accounts.permissions import is_org_admin, is_superadmin
from .api_serializers import PROCESSINGRuleSerializer
from .models import PROCESSINGRule


class PROCESSINGRuleListAPIView(generics.ListAPIView):
    """
    Lista reglas según el contexto del usuario autenticado.
    """
    serializer_class = PROCESSINGRuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if is_superadmin(self.request.user):
            return PROCESSINGRule.objects.select_related("organization").all().order_by("-updated_at")

        return PROCESSINGRule.objects.select_related("organization").filter(
            organization=self.request.user.organization
        ).order_by("-updated_at")