from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import View

from . import settings
from .models import Message


class MailHealthCheckView(View):
    def get(self, request, *args, **kwargs):
        oldest, too_old = 0, False
        message = Message.objects.filter(status__lt=Message.STATUS_SENT) \
                                 .order_by('date_created').first()

        if message:
            seconds = (timezone.now().astimezone() - message.date_created.astimezone()).total_seconds()
            oldest = round(seconds / 60)  # to minutes
            too_old = oldest > settings.MAILER_HC_QUEUED_LIMIT_OLD

        texts = (
            'oldest_queued_email: {} mins'.format(oldest),
            'emails_queued_too_old: {}'.format(('no', 'yes')[too_old]),
            'settings.MAILER_HC_QUEUED_LIMIT_OLD: {} mins'.format(settings.MAILER_HC_QUEUED_LIMIT_OLD),
        )
        response = '\n'.join(texts)

        return HttpResponse(response, content_type='text/plain')
