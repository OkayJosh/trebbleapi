import os
from pathlib import Path

from dotenv import dotenv_values


# Load the environment variables from .env
env_vars = dotenv_values('.env')
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env_vars['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(env_vars['DEBUG'])

ALLOWED_HOSTS = env_vars['ALLOWED_HOSTS'].split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_framework',
    'rest_framework.authtoken',
    'django_extensions',
    'treblle',
    'brand',
    'contentgen',
    'linkedin_oauth2',
    'socials',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # third party middleware
    'treblle.middleware.TreblleMiddleware',
]

ROOT_URLCONF = 'trebbleapi.urls'


TREBLLE_INFO = {
    'api_key': env_vars['TREBLLE_API_KEY'],
    'project_id': env_vars['TREBLLE_PROJECT_ID']
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates', ],
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

WSGI_APPLICATION = 'trebbleapi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CELERY_BROKER_URL = env_vars['CELERY_BROKER_URL']
CELERY_RESULT_BACKEND = env_vars['CELERY_RESULT_BACKEND']

CELERY_BROKER_URL = ""
CELERY_RESULT_BACKEND = ""

SOCIALACCOUNT_PROVIDERS = {
    'linkedin': {
        'SCOPE': [
            'w_member_social',
            'r_emailaddress',
            'r_liteprofile',
        ],
        'PROFILE_FIELDS': [
            'id',
            'first-name',
            'last-name',
            'email-address',
            'picture-url',
            'public-profile-url',
        ],
        'CLIENT_ID': env_vars['LINKEDIN_CLIENT_ID'],
        'SECRET': env_vars['LINKEDIN_SECRET'],
        'VERIFIED_EMAIL': True,
        'AUTH_PARAMS': {'access_type': 'offline'},
    }
}
AUTH_USER_MODEL = 'users.User'
#
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

PROJECT_APP_NAME = 'trebelleapi'

STATIC_ROOT = os.path.join(BASE_DIR, "static/")


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'trebelle.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

LOGIN_REDIRECT_URL = env_vars['LOGIN_REDIRECT_URL']
SOCIALACCOUNT_TOKEN_EXPIRY = int(env_vars['SOCIALACCOUNT_TOKEN_EXPIRY'])
SOCIALACCOUNT_STORE_TOKENS = bool(env_vars['SOCIALACCOUNT_STORE_TOKENS'])
ACCOUNT_EMAIL_REQUIRED = bool(env_vars['ACCOUNT_EMAIL_REQUIRED'])
SOCIALACCOUNT_QUERY_EMAIL = ACCOUNT_EMAIL_REQUIRED
AUTHENTICATED_LOGIN_REDIRECTS = env_vars['AUTHENTICATED_LOGIN_REDIRECTS']


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

