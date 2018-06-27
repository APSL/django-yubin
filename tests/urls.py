# -*- coding: utf-8 -*-

from django.conf.urls import include, url


urlpatterns = [
    url(r'^yubin/', include('django_yubin.urls')),
]
