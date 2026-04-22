from django.urls import path

from .api_views import PROCESSINGRuleListAPIView

app_name = "rules_api"

urlpatterns = [
    path("rules/", PROCESSINGRuleListAPIView.as_view(), name="rule_list"),
]