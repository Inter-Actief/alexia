import os

from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Auth
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'utils.auth.backends.radius.RadiusBackend',
]
AUTH_USER_MODEL = 'auth.User'
LOGIN_REDIRECT_URL = '/'  # DEPRECATED
LOGIN_URL = '/login/'  # DEPRECATED

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
MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'utils.middleware.ProfileRequirementMiddleware',
    'utils.middleware.PrimaryOrganizationMiddleware',
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
    'eventlog',

    'api',
    'apps.billing',
    'apps.general',
    'apps.juliana',
    'apps.organization',
    'apps.profile',
    'apps.scheduling',
    'apps.stock',
    'utils',
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
                'django.core.context_processors.debug',
                'django.core.context_processors.i18n',
                'django.core.context_processors.media',
                'django.core.context_processors.static',
                'django.core.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'utils.context_processors.organization',
            ],
            'debug': DEBUG,
        },
    },
]

# Testing
# TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# URLs
ROOT_URLCONF = 'urls'
