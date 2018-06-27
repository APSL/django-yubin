from __future__ import absolute_import, unicode_literals

from django.test import TestCase, Client
try:
    from django.core.urlresolvers import reverse
except ImportError:
    # For Django >= 2.0
    from django.urls import reverse

from django_yubin.views import MailHealthCheckView


class HealthCheck(TestCase):

    def test_hc_view(self):
        c = Client()
        url = reverse('yubin_health')
        response = c.get(url)
        assert response.status_code == 200
        assert 'oldest_queued_email' in str(response.content)
        assert 'emails_queued_too_old' in str(response.content)
