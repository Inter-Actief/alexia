import os

from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.normpath(os.path.join(os.path.abspath(__file__), '..', '..', '..', '..'))

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
    'jsonrpc',
    'sslserver',
    'wkhtmltopdf',

    'alexia.api',
    'alexia.apps.BillingConfig',
    'alexia.apps.ConsumptionConfig',
    'alexia.apps.GeneralConfig',
    'alexia.apps.OrganizationConfig',
    'alexia.apps.ProfileConfig',
    'alexia.apps.SchedulingConfig',
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
            'builtins': [
                'crispy_forms.templatetags.crispy_forms_tags',
                'django.contrib.staticfiles.templatetags.staticfiles',
                'django.templatetags.i18n',
            ],
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'alexia.template.context_processors.organization',
                'alexia.template.context_processors.permissions',
            ],
            'debug': DEBUG,
        },
    },
]

# Testing
# TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# URLs
ROOT_URLCONF = 'alexia.conf.urls'

# Compressor
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
]
