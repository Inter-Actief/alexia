import os

from django.core.exceptions import SuspiciousOperation

#
#   Override Django defaults
#

# Directories
CURRENT_DIR = os.path.dirname(__file__)
MEDIA_ROOT = os.path.join(CURRENT_DIR, 'media')
STATIC_ROOT = os.path.join(CURRENT_DIR, 'static')
TEMPLATE_DIRS = (os.path.join(CURRENT_DIR, 'templates'),)
LOCALE_PATHS = (os.path.join(CURRENT_DIR, 'locale'),)
STATICFILES_DIRS = (os.path.join(CURRENT_DIR, 'assets'),)

# General settings
ADMINS = ()
MANAGERS = ADMINS
DEBUG = False
TEMPLATE_DEBUG = False
ALLOWED_HOSTS = ['localhost']
SITE_ID = 1
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
ROOT_URLCONF = 'urls'

# Internationalization / localization
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = 'Europe/Amsterdam'
LANGUAGE_CODE = 'nl'
LANGUAGES = (
    ('en', 'English'),
    ('nl', "Dutch"),
)

# Emails
EMAIL_SUBJECT_PREFIX = '[Alexia] '
EMAIL_FROM = 'Alexia <alexia@localhost>'
DEFAULT_FROM_EMAIL = EMAIL_FROM
SERVER_EMAIL = EMAIL_FROM

MIDDLEWARE_CLASSES = (
    'utils.middleware.ValidateHostMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'utils.middleware.ProfileRequirementMiddleware',
    'utils.middleware.PrimaryOrganizationMiddleware',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.humanize',

    'apps.billing',
    'apps.general',
    'apps.juliana',
    'apps.organization',
    'apps.profile',
    'apps.scheduling',
    'apps.stock',
    'utils',

    'api',

    'compressor',
    'crispy_forms',
    'eventlog',
)


def skip_suspicious_operations(record):
    """
    Filter to ignore SuspiciousOperation exceptions.
    """
    if record.exc_info:
        exc_value = record.exc_info[1]
        if isinstance(exc_value, SuspiciousOperation):
            return False
    return True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'skip_suspicious_operations': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_suspicious_operations,
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false', 'skip_suspicious_operations'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'utils.auth.backends.RadiusBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "utils.context_processors.primary_organization",
)

#
#   django-crispy-forms settings
#

CRISPY_ALLOWED_TEMPLATE_PACKS = ('bootstrap3',)
CRISPY_TEMPLATE_PACK = 'bootstrap3'

#
#   Amelie specific settings
#

# Radius login details
RADIUS_HOST = 'radius1.utsp.utwente.nl'
RADIUS_PORT = 1645
RADIUS_SECRET = ''
RADIUS_IDENTIFIER = ''
RADIUS_DICT = os.path.join(CURRENT_DIR, 'utils/auth/radius.dict')

#
#   Load local_settings.py
#

try:
    from local_settings import *
except ImportError:
    pass

#
#   Debug toolbar
#

if DEBUG:
    # Enable debug toolbar if DEBUG is enabled.

    def show_toolbar(request):
        return True

    INSTALLED_APPS += ('debug_toolbar',)
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': 'settings.show_toolbar'
    }
