from django.contrib import admin
from django.conf.urls import include, url

from .views import IndexView


urlpatterns = [
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^yubin/', include('django_yubin.urls')),
    url(r'^admin/', admin.site.urls),
]
