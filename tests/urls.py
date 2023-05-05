# -*- coding: utf-8 -*-

try:
    from django.urls import include, re_path
except ImportError:
    from django.conf.urls import include, url as re_path


urlpatterns = [
    re_path(r'^yubin/', include('django_yubin.urls')),
]
