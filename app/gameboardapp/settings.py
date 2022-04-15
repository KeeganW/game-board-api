"""
Django settings for gameboardapp project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import datetime
import os
from pathlib import Path

# Fix the css mimetype error from some css editors, if there’s a need for it
import mimetypes
mimetypes.add_type("text/css", ".css", True)

# Add a slash to the end of all page requests
APPEND_SLASH = True

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = os.path.join(BASE_DIR, 'gameboard')
STATIC_ROOT = os.path.join(APP_ROOT, 'static')
MEDIA_ROOT = os.path.join(APP_ROOT, 'media')

REPOSITORY_ROOT = os.path.dirname(BASE_DIR)

STATIC_URL = os.path.join(APP_ROOT, 'static/')
MEDIA_URL = os.path.join(APP_ROOT, 'media/')

# Set the secret key originally.
SECRET_KEY = os.environ['SECRET_KEY']

# Need to cache some data to make long running calls happen less often
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

WSGI_APPLICATION = 'gameboardapp.wsgi.application'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DBNAME'],
        'USER': os.environ['DBUSER'],
        'PASSWORD': os.environ['DBPASS'],
        'HOST': os.environ['DBHOST'],
        'PORT': 5432,  # os.environ['DBPORT'],
        # TODO Comment IN for production deployment
        # 'OPTIONS': {
        #     'sslmode':'require'
        # },
    }
}

# TODO Comment OUT for production deployment!
DEBUG = True


# We want to allow the website from the env variables as one of the hosts (to access its own site)
ALLOWED_HOSTS = [os.environ['WEBSITE_SITE_NAME'], '127.0.0.1', 'localhost'] if 'WEBSITE_SITE_NAME' in os.environ else ['127.0.0.1', 'localhost']


# Application definition

INSTALLED_APPS = [
    # Standard Django installed
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # API rest things
    'rest_framework',
    # For token authentication
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    # For CORS
    'corsheaders',
    # The app we are building
    'gameboard',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

ROOT_URLCONF = 'gameboardapp.urls'

# TODO: maybe remove if we don't serve templates?
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'gameboard/templates')],
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

WSGI_APPLICATION = 'gameboardapp.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Change the user model from models.User to this
AUTH_USER_MODEL = 'gameboard.Player'

# How long before tokens timeout
TOKEN_TTL = datetime.timedelta(days=5)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        # By default pages should require authentication
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_RATES': {
        # This may need to be adjusted, but here are some starting values
        'anon': '100/day',
        'user': '1000/day'
    },
}


# Info on why we need all of this
# https://www.django-rest-framework.org/topics/ajax-csrf-cors/
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
# TODO Do not use this function! Backup in case cors things stop working
# CORS_ALLOW_ALL_ORIGINS = True

# Allow preflights to work
CORS_ALLOW_CREDENTIALS = True

# CSRF Is for
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

# CSRF_COOKIE_DOMAIN = 'bluemix.net'

