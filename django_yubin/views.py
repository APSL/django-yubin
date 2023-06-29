from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import View

from . import settings
from .models import Message


class MailHealthCheckView(View):
    def get(self, request, *args, **kwargs):
        try:
            threshold = int(request.GET.get('t', settings.MAILER_HC_QUEUED_LIMIT_OLD))
        except ValueError:
            return HttpResponse("Threshold error, it should be an integer",
                                content_type='text/plain', status=400)
        oldest, too_old = 0, False

        message = Message.objects.filter(status__lt=Message.STATUS_SENT) \
                                 .order_by('date_created').first()
        if message:
            seconds = (timezone.now().astimezone() - message.date_created.astimezone()).total_seconds()
            oldest = round(seconds / 60)  # to minutes
            too_old = oldest > threshold

        response = '\n'.join((
            'oldest_queued_email: {} mins'.format(oldest),
            'emails_queued_too_old: {}'.format(('no', 'yes')[too_old]),
            'threshold: {} mins'.format(threshold),
        ))
        return HttpResponse(response, content_type='text/plain', status=(200, 500)[too_old])
