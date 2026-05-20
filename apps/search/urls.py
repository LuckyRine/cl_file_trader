from django.urls import path
from . import views as sv

urlpatterns = [
    path("search/", sv.FileSearchView.as_view(), name="search"),
    path("api/search/", sv.FileSearchAPIView.as_view(), name="api_search"),
]
