from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.core.views import home_redirect_view

urlpatterns = [
    # ==========================================================
    # RAÍZ DEL SISTEMA
    # ==========================================================
    # Redirige a login si no hay sesión, o a uploads si sí la hay.
    path("", home_redirect_view, name="home"),

    # ==========================================================
    # ADMIN Y AUTENTICACIÓN
    # ==========================================================
    path("admin/", admin.site.urls),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # ==========================================================
    # INTERFAZ HTML DEL PROYECTO
    # ==========================================================
    path("uploads/", include("apps.uploads.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("rules/", include("apps.rules.urls")),
    path("results/", include("apps.results.urls")),

    # ==========================================================
    # API
    # ==========================================================
    path("api/accounts/", include("apps.accounts.api_urls")),
    path("api/uploads/", include("apps.uploads.api_urls")),
    path("api/results/", include("apps.results.api_urls")),
    path("api/rules/", include("apps.rules.api_urls")),

    # ==========================================================
    # OPENAPI / SWAGGER
    # ==========================================================
    # Ambos quedan protegidos con login_required, así solo usuarios
    # autenticados pueden ver la documentación.
    path("api/schema/", login_required(SpectacularAPIView.as_view()), name="schema"),
    path(
        "api/docs/",
        login_required(SpectacularSwaggerView.as_view(url_name="schema")),
        name="swagger-ui",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)