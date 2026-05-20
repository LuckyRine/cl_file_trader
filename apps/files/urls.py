from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.UploadPageView.as_view(), name="upload"),
    path("my-files/", views.MyFilesView.as_view(), name="my_files"),
    path("f/<slug:slug>/", views.DownloadPageView.as_view(), name="download"),
    path("api/files/upload/", views.FileUploadAPIView.as_view(), name="api_upload"),
    path("api/files/my/", views.UserFileListAPIView.as_view(), name="api_my_files"),
    path("api/files/download/<slug:slug>/", views.FileDownloadAPIView.as_view(), name="api_download"),
    path("api/files/delete/<slug:slug>/", views.FileDeleteAPIView.as_view(), name="api_delete"),
    path("api/files/serve/<slug:slug>/", views.FileServeView.as_view(), name="api_serve"),
]