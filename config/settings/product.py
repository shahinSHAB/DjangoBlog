from .base import *


# ================ Customize Debug And Allow Host ================
DEBUG = False
ALLOWED_HOSTS = []

# =============== Send Email And Use Smtp Gmail ===================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'your_email_host@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_secure_pass'

# =========== Static Files Directory ==============
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ================= Database ====================
DATABASES = {
    'default': env.dj_db_url('DATABASE_URL')
}

MIDDLEWARE.insert(2,"whitenoise.middleware.WhiteNoiseMiddleware")
INSTALLED_APPS.insert(5, 'whitenoise.runserver_nostatic')
