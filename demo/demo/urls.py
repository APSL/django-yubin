from django.urls import path
from django.contrib import admin

from demo.views import IndexView


urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('admin/', admin.site.urls),
]
