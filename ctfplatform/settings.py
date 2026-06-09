from pathlib import Path
from dotenv import load_dotenv
import os
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
#SECRET_KEY = "qdvlqnvmvjmzfj!fnmvdmvq!vf"
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-ctf-dev-key-change-in-prod')
#DEBUG = True
DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = ['secx-c16k.onrender.com']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_htmx',
    'challenges',
    'teams',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'ctfplatform.urls'

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

WSGI_APPLICATION = 'ctfplatform.wsgi.application'



if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

else:

    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600
        )
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        # 'OPTIONS': {
        #     'min_length': 8, 
        # }
    },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

if DEBUG:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
else:
     # On indique à Django d'utiliser notre nouvelle classe S3
    DEFAULT_FILE_STORAGE = 'challenges.storage.SupabaseStorage'
    
    # Configuration AWS S3 pour Supabase
    AWS_ACCESS_KEY_ID = os.environ.get('SUPABASE_S3_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('SUPABASE_S3_SECRET')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('SUPABASE_S3_BUCKET', 'media')
    AWS_S3_REGION_NAME = os.environ.get('SUPABASE_S3_REGION', 'eu-west-2')
    
    # L'URL Endpoint S3 fournie par Supabase
    AWS_S3_ENDPOINT_URL = os.environ.get('SUPABASE_S3_ENDPOINT')
    
    # URL publique pour afficher tes fichiers sur la plateforme CTF
    # Format : https://[ID].supabase.co/storage/v1/object/public/[BUCKET]/
    SUPABASE_URL = os.environ.get('VITE_SUPABASE_URL', '').rstrip('/')
    MEDIA_URL = f"{SUPABASE_URL}/storage/v1/object/public/{AWS_STORAGE_BUCKET_NAME}/"


# Extensions autorisées pour l'upload de fichiers de challenge( je vais devoir add plus par après )
ALLOWED_CHALLENGE_FILE_EXTENSIONS = ['.py', '.sh', '.zip', '.tar.gz', '.tar', '.txt', '.pcap', '.bin', '.c', '.js']
MAX_CHALLENGE_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

TIME_ZONE = 'UTC'
