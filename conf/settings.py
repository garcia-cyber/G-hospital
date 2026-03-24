from pathlib import Path
import os

# Chemins de base
BASE_DIR = Path(__file__).resolve().parent.parent

# Sécurité
SECRET_KEY = 'django-insecure-bqa7p(8i2e9gdu_^2w7doe_t5wr0!(*0grbjpm+2r)lw)$c(ng'
DEBUG = True
ALLOWED_HOSTS = []

# Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'conf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'conf.wsgi.application'

# DATABASE : REVENU SUR SQLITE (Ton choix initial)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# INTERNATIONALISATION (Heure de Kinshasa)
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Kinshasa'  # Pour avoir 17h au lieu de 8h
USE_I18N = True
USE_TZ = False



# Fichiers Statiques
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Médias (Images)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Redirections
LOGIN_REDIRECT_URL = '/panel/' 
LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = '/home/' 

# Emails (Gmail)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mukokogarciagx@gmail.com'
EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx' 

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'