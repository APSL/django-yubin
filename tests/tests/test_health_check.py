from django.test import TestCase, Client
from django.urls import reverse


class TestHealthCheck(TestCase):

    def testHealthCheckView(self):
        c = Client()
        url = reverse('yubin_health')
        response = c.get(url)
        assert response.status_code == 200
        assert 'oldest_queued_email' in str(response.content)
        assert 'emails_queued_too_old' in str(response.content)
