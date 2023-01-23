from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from .views import IndexView


urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('yubin/', include('django_yubin.urls')),
    path('admin/', admin.site.urls),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
