from django.urls import path
from . import views as core_views

urlpatterns = [
    path("", core_views.HomeView.as_view(), name="home"),
]
