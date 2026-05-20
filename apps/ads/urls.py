from django.urls import path
from . import views

urlpatterns = [
    path("api/ads/serve/<str:placement>/", views.AdServeView.as_view(), name="ad_serve"),
    path("api/ads/click/<int:banner_id>/", views.AdClickView.as_view(), name="ad_click"),
]

