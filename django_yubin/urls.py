from django_yubin.views import MailHealthCheckView
try:
    from django.urls import re_path
except ImportError:
    from django.conf.urls import url as re_path


urlpatterns = [
    re_path(r'^health$', MailHealthCheckView.as_view(), name='yubin_health'),
]
