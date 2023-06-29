from django.conf import settings


# Provide a way of temporarily pausing the sending of mail.
PAUSE_SEND = getattr(settings, "MAILER_PAUSE_SEND", False)

# Real backend to send emails.
USE_BACKEND = getattr(settings, 'MAILER_USE_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')

# When MAILER_TEST_MODE is True, recipient addresses of all messages are replaced with
# the email addresses set in MAILER_TEST_EMAIL before being sent.
MAILER_TEST_MODE = getattr(settings, "MAILER_TEST_MODE", False)
MAILER_TEST_EMAIL = getattr(settings, "MAILER_TEST_EMAIL", '')

# If there are emails created, enqueued or in progress for more than x minutes, the HealthCheck
# view will show an error.
MAILER_HC_QUEUED_LIMIT_OLD = getattr(settings, "MAILER_HC_QUEUED_LIMIT_OLD", 30)

# Storage to save full emails.
MAILER_STORAGE_BACKEND = getattr(
    settings,
    "MAILER_STORAGE_BACKEND",
    "django_yubin.storage_backends.DatabaseStorageBackend",
)

# Delete storage data when deleting messages from the database.
MAILER_STORAGE_DELETE = getattr(settings, "MAILER_STORAGE_DELETE", True)

# Subdirectory to save emails when using the FileStorageBackend.
MAILER_FILE_STORAGE_DIR = getattr(settings, "MAILER_FILE_STORAGE_DIR", 'yubin')
