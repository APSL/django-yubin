from django_yubin.views import MailHealthCheckView
from django.urls import path


urlpatterns = [
    path('health/', MailHealthCheckView.as_view(), name='yubin_health'),
]
