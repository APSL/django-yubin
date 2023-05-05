from django.urls import path

from .views import MailHealthCheckView


urlpatterns = [
    path('health', MailHealthCheckView.as_view(), name='yubin_health'),
]
