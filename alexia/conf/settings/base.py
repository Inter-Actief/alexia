import os

import saml2
from django.utils.translation import ugettext_lazy as _
from saml2.sigver import get_xmlsec_binary

BASE_DIR = os.path.normpath(os.path.join(os.path.abspath(__file__), '..', '..', '..', '..'))

# Auth
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'alexia.auth.backends.RadiusBackend',  # RADIUS logins with the UT
    'alexia.auth.backends.AlexiaSAML2Backend',  # SAML logins with the UT
]
AUTH_USER_MODEL = 'auth.User'
LOGIN_REDIRECT_URL = '/login_complete/'
LOGIN_URL = '/saml2sp/login/'
LOGOUT_REDIRECT_URL = '/'

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
    'jsonrpc',
    'sslserver',
    'wkhtmltopdf',

    # SAML2 SP (authentication via UT)
    'djangosaml2',

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

# SAML Service Provider configuration defaults
SAML_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../saml')
SAML_CONFIG = {
    # full path to the xmlsec1 binary program
    'xmlsec_binary': get_xmlsec_binary(['/opt/local/bin', '/usr/bin/xmlsec1']),

    # your entity id, usually your subdomain plus the url to the metadata view
    'entityid': 'https://alex.ia.utwente.nl/saml2sp/metadata/',

    # directory with attribute mapping
    'attribute_map_dir': os.path.join(SAML_BASE_DIR, 'attribute-maps'),

    # this block states what services we provide
    'service': {
        # we are just a lonely SP
        'sp': {
            'name': 'Alexia SAML SP',
            'name_id_format': None,
            'endpoints': {
                # url and binding to the assertion consumer service view
                # do not change the binding or service name
                'assertion_consumer_service': [
                    ('https://alex.ia.utwente.nl/saml2sp/acs/', saml2.BINDING_HTTP_POST),
                ],
                # url and binding to the single logout service view
                # do not change the binding or service name
                'single_logout_service': [
                    ('https://alex.ia.utwente.nl/saml2sp/ls/', saml2.BINDING_HTTP_REDIRECT),
                    ('https://alex.ia.utwente.nl/saml2sp/ls/post', saml2.BINDING_HTTP_POST),
                ],
            },

            # attributes that this project need to identify a user
            'required_attributes': ['uid'],

            # attributes that may be useful to have but not required
            'optional_attributes': ['eduPersonAffiliation'],

            # Don't request signed responses, the UT SAML server does not do that
            'want_response_signed': False,

            # in this section the list of IdPs we talk to are defined
            'idp': {
                # we do not need a WAYF service since there is
                # only an IdP defined here. This IdP should be
                # present in our metadata

                # the keys of this dictionary are entity ids
                'https://login.microsoftonline.com/f1ec8743-cb11-40ae-982a-45e321af98b4/federationmetadata/2007-06/federationmetadata.xml?appid=3805dc19-54c8-4b3f-aaf3-e8a04975c495': {
                    'single_sign_on_service': {
                        saml2.BINDING_HTTP_REDIRECT: 'https://login.microsoftonline.com/f1ec8743-cb11-40ae-982a-45e321af98b4/saml2',
                        saml2.BINDING_HTTP_POST: 'https://login.microsoftonline.com/f1ec8743-cb11-40ae-982a-45e321af98b4/saml2',
                    },
                    'single_logout_service': {
                        saml2.BINDING_HTTP_REDIRECT: 'https://login.microsoftonline.com/f1ec8743-cb11-40ae-982a-45e321af98b4/saml2',
                    },
                },
            },
        },
    },

    # where the remote metadata is stored
    'metadata': {
        'local': [os.path.join(SAML_BASE_DIR, 'utwente_metadata_prod.xml')],
    },

    # set to 1 to output debugging information
    'debug': 0,

    # Signing
    'key_file': "/etc/ia/key_beta.ia.utwente.nl.pem",  # private part
    'cert_file': "/etc/ia/cert_beta.ia.utwente.nl.pem",  # public part

    # Encryption
    'encryption_keypairs': [{
        'key_file': "/etc/ia/key_beta.ia.utwente.nl.pem",  # private part
        'cert_file': "/etc/ia/cert_beta.ia.utwente.nl.pem",  # public part
    }],

    # own metadata settings
    'contact_person': [
        {'given_name': 'WWW Commissie',
         'company': 'I.C.T.S.V. Inter-Actief',
         'email_address': 'www@inter-actief.net',
         'contact_type': 'technical'},
        {'given_name': 'Dagelijks Bestuur',
         'company': 'Stichting Borrelbeheer Zilverling',
         'email_address': 'db@sbz.utwente.nl',
         'contact_type': 'administrative'},
    ],
    # you can set multilanguage information here
    'organization': {
        'name': [('Stichting Borrelbeheer Zilverling', 'nl'), ('Stichting Borrelbeheer Zilverling', 'en')],
        'display_name': [('SBZ', 'nl'), ('SBZ', 'en')],
        'url': [('http://www.sbz.utwente.nl', 'nl'), ('http://www.sbz.utwente.nl', 'en')],
    },
    'valid_for': 24,  # how long is our metadata valid
}
