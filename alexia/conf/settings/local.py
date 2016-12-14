# Voorbeeld voor lokale settings, wordt geimporteerd door __init__.py
#
from .base import *

# Debug aan voor lokaal
DEBUG = True

# Admins die exceptie-notificaties krijgen
ADMINS = ()
MANAGERS = ADMINS

# Hostnames
ALLOWED_HOSTS = []

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'alexia',                       # Of pad naar sqlite3 database
        # Hieronder negeren voor sqlite3
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '',                       # Leeg voor localhost
        'PORT': '',                       # Leeg is default
    }
}

# Jouw secret key
# http://www.miniwebtool.com/django-secret-key-generator/
SECRET_KEY = 'di32mcm)s**t(34u*^wgi)9ua+l-7twx0@$eqjfva$8(86+$rs'

# UT Radius login
RADIUS_SECRET = ''
RADIUS_IDENTIFIER = ''

# Email settings
EMAIL_HOST = 'localhost'
EMAIL_SUBJECT_PREFIX = '[Alexia] '
EMAIL_FROM = 'Alexia <alexia@localhost>'
DEFAULT_FROM_EMAIL = EMAIL_FROM
SERVER_EMAIL = EMAIL_FROM
