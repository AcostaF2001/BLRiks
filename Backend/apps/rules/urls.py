from django.urls import path

from .views import rule_create_view, rule_list_view, rule_update_view

# Namespace de la app para usar reverse y templates de forma ordenada
app_name = "rules"

urlpatterns = [
    # Lista de reglas registradas
    path("", rule_list_view, name="rule_list"),

    # Crear nueva regla
    path("new/", rule_create_view, name="rule_create"),

    # Editar una regla existente
    path("<int:rule_id>/edit/", rule_update_view, name="rule_update"),
]