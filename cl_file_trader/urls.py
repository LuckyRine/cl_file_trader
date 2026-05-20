from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path("admin/", admin.site.urls),
                  path("", include("apps.core.urls")),  # /
                  path("", include("apps.accounts.urls")),  # /register/ /login/ /logout/ /profile/
                  path("", include("apps.files.urls")),  # /upload/ /my-files/ /f/<slug>/
                  path("", include("apps.subscriptions.urls")),  # /pricing/ /pricing/checkout/<id>/
                  # path("", include("apps.search.urls")),  # /search/
                  path("", include("apps.ads.urls")), # /serve/ /click/

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)