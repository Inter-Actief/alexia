# Settings used for running tests in Travis
#

# Load default settings
# noinspection PyUnresolvedReferences
from default import *

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'alexia_test',                       # Of pad naar sqlite3 database
        # Hieronder negeren voor sqlite3
        'USER': 'travis',
        'PASSWORD': '',
        'HOST': '',                       # Leeg voor localhost
        'PORT': '',                       # Leeg is default
    }
}

SECRET_KEY = 'zBCMvM1BwLtlkoXf1mbgCo3W60j2UgIPhevmEJ9cMPft2JtUk5'
