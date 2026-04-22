from django.urls import path

from .api_views import (
    UploadedFileExecutionListAPIView,
    UploadedFileListAPIView,
    UploadedFileReprocessAPIView,
)

app_name = "uploads_api"

urlpatterns = [
    path("files/", UploadedFileListAPIView.as_view(), name="file_list"),
    path("files/<int:uploaded_file_id>/executions/", UploadedFileExecutionListAPIView.as_view(), name="file_executions"),
    path("files/<int:uploaded_file_id>/reprocess/", UploadedFileReprocessAPIView.as_view(), name="file_reprocess"),
]