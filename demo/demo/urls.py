from django.conf import settings
from django.contrib import admin
from django.conf.urls import include, url

from .views import IndexView


urlpatterns = [
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^yubin/', include('django_yubin.urls')),
    url(r'^admin/', admin.site.urls),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
