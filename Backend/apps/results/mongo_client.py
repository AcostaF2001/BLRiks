from pymongo import MongoClient
from django.conf import settings


def get_mongo_database():
    """
    Retorna la base de datos Mongo configurada en settings.

    Se utiliza MongoDB Atlas a través de MONGO_URI.
    Esto permite separar claramente:
    - PostgreSQL para datos transaccionales y configuración
    - MongoDB para resultados procesados y metadata enriquecida
    """
    client = MongoClient(settings.MONGO_URI)
    return client[settings.MONGO_DB]