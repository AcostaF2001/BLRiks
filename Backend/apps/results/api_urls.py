from django.urls import path

from .api_views import UploadedFileResultsAPIView

app_name = "results_api"

urlpatterns = [
    path("files/<int:uploaded_file_id>/results/", UploadedFileResultsAPIView.as_view(), name="file_results"),
]