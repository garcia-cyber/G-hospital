from pathlib import Path
import os
from dotenv import load_dotenv

# --- 1. CHEMINS DE BASE ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- 2. CHARGEMENT DU .ENV ---
load_dotenv(os.path.join(BASE_DIR, '.env'))

# --- 3. SÉCURITÉ ---
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-local-dev-key')

if not DEBUG:
    # URL de ton projet sur Render
    ALLOWED_HOSTS = [os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'g-hospital.onrender.com')]
    
    # Sécurité HTTPS pour la production (Optionnel sur Free Tier, mais recommandé)
    SECURE_SSL_REDIRECT = False  # Garde à False si tu as des problèmes de redirection au début
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.100']

# --- 4. APPLICATIONS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app', 
]

# --- 5. MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'conf.urls'

# --- 6. TEMPLATES ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'conf.wsgi.application'

# --- 7. BASE DE DONNÉES (SQLITE ÉPHÉMÈRE) ---
# En mode Gratuit (Option B), on utilise le dossier du projet car /data est interdit
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- 8. STATIQUES ET MÉDIAS ---
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Les médias seront stockés dans le dossier du projet (ils s'effaceront aussi au redémarrage)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- 9. EMAILS ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')

# --- 10. CONFIGURATION GÉNÉRALE ---
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Kinshasa'
USE_I18N = True
USE_TZ = False
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redirections
LOGIN_REDIRECT_URL = '/panel/' 
LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = '/home/'