import os

from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.normpath(os.path.join(os.path.abspath(__file__), '..', '..', '..'))

# Auth
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'alexia.auth.backends.RadiusBackend',
]
AUTH_USER_MODEL = 'auth.User'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = '/login/'

# Crispy forms
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Debugging
DEBUG = False

# Email
DEFAULT_FROM_EMAIL = 'Alexia <alexia@localhost>'
EMAIL_SUBJECT_PREFIX = '[Alexia] '
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# File uploads
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# I18n/L10n
LANGUAGE_CODE = 'nl-nl'
LANGUAGES = [
    ('nl', _('Dutch')),
    ('en', _('English')),
]
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]
TIME_ZONE = 'Europe/Amsterdam'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# HTTP
INTERNAL_IPS = ['127.0.0.1']
MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'alexia.middleware.common.CommonMiddleware',
]

# Models
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    'compressor',
    'crispy_forms',
    'debug_toolbar',
    'eventlog',
    'wkhtmltopdf',

    'alexia.api',
    'alexia.apps.billing',
    'alexia.apps.consumption',
    'alexia.apps.general',
    'alexia.apps.juliana',
    'alexia.apps.organization',
    'alexia.apps.profile',
    'alexia.apps.scheduling',
    'alexia.utils',
]

# Security
CSRF_COOKIE_HTTPONLY = False

# Sessions

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'assets'),
]
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]


# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'alexia.template.context_processors.organization',
            ],
            'debug': DEBUG,
        },
    },
]

# Testing
# TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# URLs
ROOT_URLCONF = 'alexia.conf.urls'
