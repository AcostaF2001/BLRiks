from django.conf import settings
from django.db import models


class UploadedFile(models.Model):
    """
    Representa el archivo original cargado por el usuario.

    Este modelo almacena la identidad principal del archivo y conserva
    un resumen de la última ejecución realizada sobre él.

    Importante:
    el historial completo de reprocesos/versiones no vive aquí,
    sino en ProcessingExecution.
    """

    class Status(models.TextChoices):
        """
        Estados posibles del archivo según la última ejecución realizada.
        """
        PENDING = "PENDING", "Pendiente"
        PROCESSING = "PROCESSING", "Procesando"
        FINISHED = "FINISHED", "Finalizado"
        ERROR = "ERROR", "Error"

    # Organización a la que pertenece el archivo
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.PROTECT,
        related_name="uploaded_files",
    )

    # Usuario que realizó la carga inicial del archivo
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="uploaded_files",
    )

    # Archivo físico almacenado en disco
    original_file = models.FileField(upload_to="uploads/%Y/%m/%d/")

    # Nombre original del archivo tal como lo subió el usuario
    original_filename = models.CharField(max_length=255)

    # Estado correspondiente a la última ejecución/version
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    # Resumen de la última ejecución
    total_rows = models.PositiveIntegerField(default=0)
    processed_rows = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, default="")

    # Versión actual del archivo según el último reproceso ejecutado
    current_version = models.PositiveIntegerField(default=0)

    # Fechas de trazabilidad
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Uploaded File"
        verbose_name_plural = "Uploaded Files"

    def __str__(self):
        return f"{self.original_filename} - v{self.current_version} - {self.status}"


class ProcessingExecution(models.Model):
    """
    Representa una ejecución concreta de procesamiento de un archivo.

    Cada vez que el archivo se procesa o reprocesa, se crea una nueva
    instancia de este modelo con una versión incremental.

    Beneficios:
    - historial de ejecuciones
    - versionamiento real
    - trazabilidad por reproceso
    - prevención de duplicados por versión
    """

    class Status(models.TextChoices):
        """
        Estados posibles de una ejecución específica.
        """
        PENDING = "PENDING", "Pendiente"
        PROCESSING = "PROCESSING", "Procesando"
        FINISHED = "FINISHED", "Finalizado"
        ERROR = "ERROR", "Error"

    # Archivo al que pertenece esta ejecución
    uploaded_file = models.ForeignKey(
        UploadedFile,
        on_delete=models.CASCADE,
        related_name="executions",
    )

    # Número de versión incremental de esta ejecución
    version = models.PositiveIntegerField()

    # Estado de esta corrida específica
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    # Regla aplicada en esta ejecución
    applied_rule = models.ForeignKey(
        "rules.ProcessingRule",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="executions",
    )

    # Métricas y error de esta ejecución
    total_rows = models.PositiveIntegerField(default=0)
    processed_rows = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, default="")

    # Usuario que disparó esta ejecución o reproceso
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="processing_executions",
    )

    # Fechas de trazabilidad de la ejecución
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-version", "-created_at"]
        verbose_name = "Processing Execution"
        verbose_name_plural = "Processing Executions"
        constraints = [
            models.UniqueConstraint(
                fields=["uploaded_file", "version"],
                name="unique_uploaded_file_version",
            )
        ]

    def __str__(self):
        return f"File #{self.uploaded_file_id} - v{self.version} - {self.status}"