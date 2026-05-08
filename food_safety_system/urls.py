from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inspections.urls')),
    # Fallback static serving for platforms where /static is not served correctly.
    re_path(r'^static/(?P<path>.*)$', serve, {
        'document_root': settings.BASE_DIR / 'inspections' / 'static',
    }),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
