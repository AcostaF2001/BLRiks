from pathlib import Path
from decouple import config

# ==========================================================
# BASE_DIR
# ==========================================================
# Esta ruta representa la carpeta base del backend.
# Como este archivo está en config/settings/base.py,
# debemos subir 3 niveles para llegar a Backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ==========================================================
# CONFIGURACIÓN PRINCIPAL DE DJANGO
# ==========================================================
SECRET_KEY = config("DJANGO_SECRET_KEY")
DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config(
    "DJANGO_ALLOWED_HOSTS",
    default="127.0.0.1,localhost",
    cast=lambda v: [s.strip() for s in v.split(",")]
)


# ==========================================================
# APLICACIONES INSTALADAS
# ==========================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",

    # Librerías para API y documentación OpenAPI/Swagger
    "rest_framework",
    "drf_spectacular",
    "drf_spectacular_sidecar",

    "apps.core",
    "apps.accounts",
    "apps.uploads",
    "apps.rules",
    "apps.processing",
    "apps.results",
    "apps.audit",
]


# ==========================================================
# MIDDLEWARE
# ==========================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ==========================================================
# RUTAS PRINCIPALES
# ==========================================================
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# ==========================================================
# TEMPLATES
# ==========================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        # Aquí se agregan carpetas globales de templates.
        # Se usa para templates compartidos, como login.
        "DIRS": [BASE_DIR / "templates"],

        # Permite que Django también busque templates dentro de cada app
        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                # Hace disponible el request en todos los templates
                "django.template.context_processors.request",

                # Hace disponible la información del usuario autenticado
                "django.contrib.auth.context_processors.auth",

                # Hace disponible el sistema de mensajes temporales
                "django.contrib.messages.context_processors.messages",

                # Contexto reutilizable para navegación y permisos
                "apps.core.context_processors.navigation_context",
            ],
        },
    },
]

# ==========================================================
# BASE DE DATOS PRINCIPAL - POSTGRESQL
# ==========================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": config("POSTGRES_HOST"),
        "PORT": config("POSTGRES_PORT", cast=int),
    }
}


# ==========================================================
# VALIDADORES DE CONTRASEÑA
# ==========================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ==========================================================
# INTERNACIONALIZACIÓN
# ==========================================================
LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True


# ==========================================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# ==========================================================
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"


# ==========================================================
# CLAVE PRIMARIA POR DEFECTO
# ==========================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ==========================================================
# MONGODB ATLAS
# ==========================================================
MONGO_DB = config("MONGO_DB")
MONGO_URI = config("MONGO_URI")


# ==========================================================
# REDIS / CELERY
# ==========================================================
REDIS_HOST = config("REDIS_HOST")
REDIS_PORT = config("REDIS_PORT", cast=int)

CELERY_BROKER_URL = config("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND")


# ==========================================================
# USUARIO PERSONALIZADO
# ==========================================================
AUTH_USER_MODEL = "accounts.User"

# ==========================================================
# AUTENTICACIÓN - REDIRECCIONES
# ==========================================================
# LOGIN_URL:
# ruta a la que Django redirige cuando una vista protegida requiere autenticación
LOGIN_URL = "/login/"

# LOGIN_REDIRECT_URL:
# ruta a la que Django envía al usuario después de iniciar sesión correctamente
LOGIN_REDIRECT_URL = "/uploads/"

# LOGOUT_REDIRECT_URL:
# ruta a la que Django envía al usuario después de cerrar sesión
LOGOUT_REDIRECT_URL = "/login/"


# ==========================================================
# DJANGO REST FRAMEWORK
# ==========================================================
# Configuración base de DRF.
# Se define drf-spectacular como generador del esquema OpenAPI.
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",

    # Por ahora mantenemos SessionAuthentication porque el sistema
    # ya usa login de Django y queremos que Swagger aproveche esa sesión.
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],

    # Exigimos autenticación por defecto para la API.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# ==========================================================
# DRF SPECTACULAR / SWAGGER
# ==========================================================
# Configuración de la documentación OpenAPI.
SPECTACULAR_SETTINGS = {
    "TITLE": "Assessment Técnico API",
    "DESCRIPTION": (
        "Documentación de la API del assessment. "
        "Incluye endpoints de archivos, reglas y resultados."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}


# ==========================================================
# ENTORNO
# ==========================================================
APP_ENV = config("APP_ENV", default="local")