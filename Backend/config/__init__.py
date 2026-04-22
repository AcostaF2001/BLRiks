# ==========================================================
# EXPORTACIÓN DE LA APP DE CELERY
# ==========================================================
# Esto permite que al importar config, también quede disponible
# la instancia principal de Celery.
from .celery import app as celery_app

__all__ = ("celery_app",)