"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('habitacao.api.urls')),
    # Compat: redirect /api/ to versioned base /api/v1/
    path('api/', RedirectView.as_view(url='/api/v1/', permanent=False)),
    # Optional convenience: redirect root to Swagger
    path('', RedirectView.as_view(url='/api/v1/swagger/', permanent=False)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
