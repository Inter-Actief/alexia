from .base import *  # NOQA

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '172.17.0.1',
        'NAME': 'alexia_test',
        'USER': 'alexia_test',
        'PASSWORD': 'alexia_test',
        'TEST': {
            'NAME': 'alexia_test',
        }
    }
}

SECRET_KEY = 'zBCMvM1BwLtlkoXf1mbgCo3W60j2UgIPhevmEJ9cMPft2JtUk5'

# Disable secure redirects to allow testing without SSL
SECURE_SSL_REDIRECT = False
