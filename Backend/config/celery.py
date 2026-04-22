import os

from celery import Celery

# ==========================================================
# CONFIGURACIÓN DEL MÓDULO DE SETTINGS DE DJANGO
# ==========================================================
# Aquí le indicamos a Celery qué settings de Django debe usar.
# Como el proyecto está trabajando con settings modulares,
# apuntamos al entorno local.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

# ==========================================================
# CREACIÓN DE LA APP DE CELERY
# ==========================================================
# Se crea una instancia de Celery con el nombre principal del proyecto.
app = Celery("config")

# ==========================================================
# CARGA DE CONFIGURACIÓN DESDE DJANGO
# ==========================================================
# namespace="CELERY" le dice a Celery que lea variables
# que comiencen por CELERY_ dentro del settings.py
# por ejemplo:
# - CELERY_BROKER_URL
# - CELERY_RESULT_BACKEND
app.config_from_object("django.conf:settings", namespace="CELERY")

# ==========================================================
# AUTODESCUBRIMIENTO DE TASKS
# ==========================================================
# Esto permite que Celery busque automáticamente archivos tasks.py
# dentro de las apps instaladas en Django.
app.autodiscover_tasks()