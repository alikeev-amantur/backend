from .base import *
import dj_database_url

DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get('DATABASE_URL', )
    )
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
