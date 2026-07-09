import environ

from .base import *  # NOQA

env = environ.Env()

# Database
# Defaults to the CI MariaDB service (reachable via the Docker bridge gateway);
# override with DATABASE_URL to point at a different DB, e.g. the docker-compose "db" service.
DATABASES = {
    'default': env.db_url(
        'DATABASE_URL',
        default='mysql://alexia_test:alexia_test@172.17.0.1:3306/alexia_test',
    )
}
DATABASES['default']['TEST'] = {'NAME': 'alexia_test'}

SECRET_KEY = env('DJANGO_SECRET_KEY', default='zBCMvM1BwLtlkoXf1mbgCo3W60j2UgIPhevmEJ9cMPft2JtUk5')

# Disable secure redirects to allow testing without SSL
SECURE_SSL_REDIRECT = False
