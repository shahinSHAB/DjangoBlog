from .base import *


DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# =========== Static files directory ==============
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'assets',
]

# STATIC_ROOT = BASE_DIR / 'static'

# =========== Upload media directory ==============
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = 'media/'

# ================= Database ====================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ========== Application definition ==============
INSTALLED_APPS += [
    # third_party
    'debug_toolbar',
]

INTERNAL_IPS = ['127.0.0.1', ]

# ============== Custom Middleware ===============
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# ================= Setting for sending email ====================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ============== Custom Timezone ==================
TIME_ZONE = 'Asia/Tehran'
