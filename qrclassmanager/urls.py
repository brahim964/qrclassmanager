from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect  # Para redirigir la raíz (/)

urlpatterns = [
    path("", lambda request: redirect("/docs/")),  # Redirige la raíz al Swagger
    path("admin/", admin.site.urls),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("api/", include("core.urls")),
]

# Servir archivos subidos (por ejemplo QRs) en modo desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
