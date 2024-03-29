import os
import tempfile


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ADMINS = [("Admin1", "admin1@example.com"), ("Admin2", "admin2@example.com")]
MANAGERS = [("Manager1", "manager1@example.com"), ("Manager2", "manager2@example.com")]

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

ROOT_URLCONF = 'tests.urls'

SECRET_KEY = 'yo secret yo'
SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django_yubin',
    'tests.app',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
           os.path.join(BASE_DIR, 'tests', 'tests', 'templates', 'mail'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

MEDIA_ROOT = tempfile.TemporaryDirectory().name

EMAIL_PORT = 1025
EMAIL_BACKEND = 'django_yubin.backends.QueuedEmailBackend'
MAILER_USE_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

CELERY_ALWAYS_EAGER = True
