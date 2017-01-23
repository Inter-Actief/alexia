from .base import *  # NOQA

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'alexia_test',
        'USER': 'root',
    }
}

SECRET_KEY = 'zBCMvM1BwLtlkoXf1mbgCo3W60j2UgIPhevmEJ9cMPft2JtUk5'
