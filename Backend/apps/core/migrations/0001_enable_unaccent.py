from django.db import migrations
from django.contrib.postgres.operations import UnaccentExtension


class Migration(migrations.Migration):
    """
    Habilita la extensión unaccent en PostgreSQL.

    Esto permite hacer búsquedas ignorando tildes/acentos,
    algo muy útil para filtros de usuarios y archivos.
    """

    dependencies = []

    operations = [
        UnaccentExtension(),
    ]