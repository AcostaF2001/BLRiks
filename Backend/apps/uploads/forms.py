from django import forms

from .models import UploadedFile


class UploadedFileForm(forms.ModelForm):
    """
    Formulario basado en modelo para la carga de archivos.

    Se limita únicamente al campo original_file porque:
    - organization se toma del usuario autenticado
    - uploaded_by se toma del request.user
    - original_filename se genera automáticamente
    - status inicia automáticamente en PENDING

    Esto evita que el usuario manipule datos que deben controlarse desde backend.
    """

    class Meta:
        model = UploadedFile
        fields = ["original_file"]
        widgets = {
            "original_file": forms.ClearableFileInput(
                attrs={
                    "id": "fileInput",
                    "accept": ".xlsx,.xls,.csv",
                }
            )
        }