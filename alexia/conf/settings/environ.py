# This is the configuration file for Alexia.
# This configuration file will load configuration from environment variables.

# Keep these imports here!
import warnings
import os
import json

import environ
from pathlib import Path

from email.utils import getaddresses
from django.core.management.utils import get_random_secret_key

from alexia.conf.settings.base import *

# Initialize an env object for `django-environ`
env = environ.Env()

# Proxy function for get_random_secret_key that replaces $ with % (because $ has a special function in django-environ)
def get_random_secret_key_no_dollar():
    s = get_random_secret_key()
    return s.replace('$', '%')

# Set base path of the project, to build paths with.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent.parent

# Configure database
DATABASES = {
    'default': env.db_url("DATABASE_URL", default=f"sqlite:////{BASE_DIR}/alexia.db")
}

# Override database options if environment variable is given (unsupported by django-environ's env.db() function)
DATABASE_OPTIONS = env.json('DATABASE_OPTIONS', default={})
if DATABASE_OPTIONS:
    DATABASES['default']['OPTIONS'] = DATABASE_OPTIONS

# Make sure these are set correctly in production
ENV                   = env('DJANGO_ENVIRONMENT', default='PRODUCTION')
DEBUG                 = env.bool('DJANGO_DEBUG', default=False)
DEBUG_TOOLBAR         = env.bool('DJANGO_DEBUG', default=False)
TEMPLATE_DEBUG        = env.bool('DJANGO_DEBUG', default=False)
MY_DEBUG_IN_TEMPLATES = False
IGNORE_REQUIRE_SECURE = False
PYDEV_DEBUGGER        = False
PYDEV_DEBUGGER_IP     = None


# Only enable rosetta and runserver_plus in debug mode
if DEBUG:
    INSTALLED_APPS = INSTALLED_APPS + ['rosetta']
    ROSETTA_POFILE_WRAP_WIDTH = 0

    # Enable django-extensions in debug mode (runserver_plus cmd)
    INSTALLED_APPS = INSTALLED_APPS + ['django_extensions']


# Do not redirect to HTTPS, because the nginx proxy container only listens on HTTP
SECURE_SSL_REDIRECT   = False

# Allowed hosts -- localhost and 127.0.0.1 are always allowed, the rest comes from an environment variable.
ALLOWED_HOSTS = [
    "localhost", "127.0.0.1"
] + env.list("DJANGO_ALLOWED_HOSTS", default=[])

# Example: DJANGO_ADMINS="Jan Janssen <j.janssen@inter-actief.net>, Bob de Bouwer <b.bouwer@inter-actief.net>"
ADMINS = getaddresses([env("DJANGO_ADMINS", default="WWW-committee <alexia-errors@inter-actief.net>")])
MANAGERS = ADMINS

###
#  Logging settings
###
LOG_LEVEL = env("DJANGO_LOG_LEVEL", default="INFO")

LOG_TO_CONSOLE = env.bool("DJANGO_LOG_TO_CONSOLE", default=True)
LOG_TO_FILE = env.bool("DJANGO_LOG_TO_FILE", default=False)
LOG_MAIL_ERRORS = env.bool("DJANGO_MAIL_ERRORS", default=False)

ENABLED_HANDLERS = []
if LOG_TO_CONSOLE:
    ENABLED_HANDLERS.append('console')
if LOG_TO_FILE:
    ENABLED_HANDLERS.append('alexia-file')
if LOG_MAIL_ERRORS:
    ENABLED_HANDLERS.append('mail_admins')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s %(name)s %(funcName)s (%(filename)s:%(lineno)d) %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'alexia-file': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': f'{BASE_DIR}/alexia.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': False,
        },
    },
    'root': { # all other errors go to the console, the general log file and sentry
        'level': 'DEBUG',
        'handlers': ENABLED_HANDLERS,
    },
    'loggers': {
        'alexia': { # Log all Alexia errors
            'level': 'DEBUG',
        },
        'django': { # Reset default settings for django
            'handlers': [],
        },
        'django.request': { # Reset default settings for django.request
            'handlers': [],
            'level': 'ERROR',
            'propagate': True,
        },
        'py.warnings': { # Reset default settings for py.warnings
            'handlers': [],
        },
        'sentry.errors': { # do not propagate sentry errors to sentry
            'level': 'DEBUG',
            'handlers': ENABLED_HANDLERS,
            'propagate': False,
        },
        'tornado.access': { # Ignore tornado.access INFO logging
            'handlers': [],
            'level': 'WARNING',
        },
        'amqp': { # Set AMQP to something else than debug (log spam)
            'level': 'WARNING',
        },
        'urllib3': { # Set urllib3 to something else than debug
            'level': 'WARNING',
        },
        'daphne': { # Set daphne logging to INFO
            'level': 'INFO'
        },
        # Set OIDC logging to at least info due to process_request log flooding
        'mozilla_django_oidc.middleware': {'level': 'INFO'},
    },
}

# Sentry SDK configuration
DJANGO_SENTRY_DSN = env("DJANGO_SENTRY_DSN", default="")
DJANGO_SENTRY_ENVIRONMENT = env("DJANGO_SENTRY_ENVIRONMENT", default="production")
if DJANGO_SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    sentry_sdk.init(
        dsn=DJANGO_SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
        ],
        # Proportion of requests that are traced for performance monitoring.
        # Keep at (or very very very close to) 0 in production!
        traces_sample_rate=0,
        # Send user details of request to Sentry
        send_default_pii=True,
        auto_session_tracking=False,
        environment=DJANGO_SENTRY_ENVIRONMENT,
    )


###
# Authentication settings
###

# Django authentication backends
# Login settings -- only allow login using specified backends
AUTHENTICATION_BACKENDS = env.list("DJANGO_AUTHENTICATION_BACKENDS", default=[
    "django.contrib.auth.backends.ModelBackend", "alexia.auth.backends.IAOIDCAuthenticationBackend"
])

# OIDC Single sign-on configuration
OIDC_RP_CLIENT_ID = env("OIDC_RP_CLIENT_ID", default="alexia")
OIDC_RP_CLIENT_SECRET = env("OIDC_RP_CLIENT_SECRET", default="")


###
# Security settings
###

# Only use cookies for HTTPS
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# If the proxy tells us the external side is HTTPS, use that
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Make this unique, and don't share it with anybody.
SECRET_KEY = env('DJANGO_SECRET_KEY', default=get_random_secret_key_no_dollar())


###
#  Internationalization
###
LOCALE_PATHS = ('/alexia/locale', )


###
#  URL and Media settings
###
# Path to alexia static files
STATIC_ROOT = '/static'
STATIC_URL = env("ALEXIA_STATIC_URL", default="/static/")

# Path to alexia media
MEDIA_ROOT = '/media'
MEDIA_URL = env("ALEXIA_MEDIA_URL", default="/media/")

# Path to website (needed for pictures via the API among other things)
ABSOLUTE_PATH_TO_SITE = env("ALEXIA_ABSOLUTE_PATH_TO_SITE", default="http://localhost:8080/")


###
#  E-mail settings
###
EMAIL_BACKEND = env("ALEXIA_EMAIL_BACKEND", default="django.core.mail.backends.filebased.EmailBackend")
EMAIL_HOST = env("ALEXIA_EMAIL_HOST", default="smtp.snt.utwente.nl")
EMAIL_PORT = env.int("ALEXIA_EMAIL_PORT", default=25)
EMAIL_FROM = env("ALEXIA_EMAIL_FROM", default='Alexia <alexia@inter-actief.net>')
EMAIL_SUBJECT_PREFIX = env("ALEXIA_EMAIL_SUBJECT_PREFIX", default='[Alexia] ')
DEFAULT_FROM_EMAIL = EMAIL_FROM
SERVER_EMAIL = EMAIL_FROM


###
# Alexia-specific settings
###
# HTML to PDF script
WKHTMLTOPDF_CMD = '/alexia/scripts/wkhtmltopdf.sh'
