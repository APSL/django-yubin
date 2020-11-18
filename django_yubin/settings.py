from django.conf import settings


# Provide a way of temporarily pausing the sending of mail.
PAUSE_SEND = getattr(settings, "MAILER_PAUSE_SEND", False)

USE_BACKEND = getattr(settings, 'MAILER_USE_BACKEND',
                      'django.core.mail.backends.smtp.EmailBackend')

# When MAILER_TEST_MODE is True, recipient addresses of all messages are replaced with
# the email addresses set in MAILER_TEST_EMAIL before being sent
MAILER_TEST_MODE = getattr(settings, "MAILER_TEST_MODE", False)
MAILER_TEST_EMAIL = getattr(settings, "MAILER_TEST_EMAIL", '')

MAILER_HC_QUEUED_LIMIT_OLD = getattr(settings, "MAILER_HC_QUEUED_LIMIT_OLD", 30)
