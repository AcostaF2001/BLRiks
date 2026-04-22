# ==========================================================
# IMAGEN BASE
# ==========================================================
# Se usa una imagen liviana de Python para correr Django y Celery.
FROM python:3.12-slim

# ==========================================================
# VARIABLES DE ENTORNO
# ==========================================================
# Evitan archivos intermedios innecesarios y mejoran logs.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ==========================================================
# DIRECTORIO DE TRABAJO
# ==========================================================
WORKDIR /app

# ==========================================================
# DEPENDENCIAS DEL SISTEMA
# ==========================================================
# Necesarias especialmente para PostgreSQL y algunas librerías Python.
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ==========================================================
# INSTALACIÓN DE DEPENDENCIAS PYTHON
# ==========================================================
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ==========================================================
# COPIA DEL PROYECTO
# ==========================================================
COPY . /app