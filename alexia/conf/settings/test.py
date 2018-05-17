from .base import *  # NOQA

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'NAME': 'alexia_test',
        'USER': 'travis',
        'PASSWORD': '',
    }
}

SECRET_KEY = 'zBCMvM1BwLtlkoXf1mbgCo3W60j2UgIPhevmEJ9cMPft2JtUk5'
