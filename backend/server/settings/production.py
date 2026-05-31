"""
Production settings: PostgreSQL, Redis channels, Whitenoise, security.
"""

import os
import dj_database_url
from .base import *

DEBUG = False

db_url = os.environ.get('DATABASE_URL')
if db_url:
    DATABASES = {
        'default': dj_database_url.parse(db_url)
    }
else:
    raise ValueError("DATABASE_URL environment variable is required in production!")

redis_url = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379')
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [redis_url],
        },
    },
}

whitenoise_middleware = 'whitenoise.middleware.WhiteNoiseMiddleware'
if whitenoise_middleware not in MIDDLEWARE:
    MIDDLEWARE.insert(1, whitenoise_middleware)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

allowed = os.environ.get('ALLOWED_HOSTS', '')
if not allowed or allowed == '*':
    raise ValueError("ALLOWED_HOSTS must be set to your domain in production!")
ALLOWED_HOSTS = allowed.split(',')

cors = os.environ.get('CORS_ALLOWED_ORIGINS', '')
if not cors:
    raise ValueError("CORS_ALLOWED_ORIGINS must be set in production!")
CORS_ALLOWED_ORIGINS = cors.split(',')

SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True') == 'True'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 10485760,
            'backupCount': 5,
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}