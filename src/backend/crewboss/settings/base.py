import environ
import os
from decimal import Decimal

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'frontend')
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR))), 'backup')

env = environ.Env()
ENV_PATH = (environ.Path(__file__) - 3).path('env/settings.env')

try:
    env_file = str(ENV_PATH)
    if os.path.isfile(env_file):
        print('Loading : {}'.format(env_file))
        env.read_env(env_file)
except Exception:
    pass


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG_FLAG", False) == 'True'

ALLOWED_HOSTS = ['*']
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:9090/')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.staticfiles',
    'django_seed',
    'channels',
    'rest_framework',
    'reversion',
    'loginas',
    'django_filters',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
    'health_check.contrib.psutil',

    'cbcommon',
    'account',
    'construction',
    'private',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cbcommon.middleware.maintenance_mode',
    'cbcommon.middleware.BypassRevisionMiddleware',
    'cbcommon.middleware.RequestRoleMiddleware',
]

ROOT_URLCONF = 'crewboss.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR + '/../templates',
            FRONTEND_DIR + '/public'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'crewboss.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', ''),
        'USER': os.environ.get('DB_USER', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
        'PASSWORD': os.environ.get('DB_PASS', ''),
    }
}


# Authentication
AUTH_USER_MODEL = 'account.User'
AUTHENTICATION_BACKENDS = ['account.auth_backends.EmailOrMobileNumberBackend']

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
if SENDGRID_API_KEY:
    EMAIL_USE_TLS = True
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = 'apikey'
    EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
    EMAIL_PORT = 587
else:
    EMAIL_HOST = 'mail'
    EMAIL_PORT = 25

SPARKPOST_API_KEY = os.environ.get('SPARKPOST_API_KEY', '')
SPARKPOST_OPTIONS = {'track_clicks': False}

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'notifications@crewboss.app')
SEND_MESSAGES_TO_ADMIN = os.environ.get('SEND_MESSAGES_TO_ADMIN', True) != 'False'

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Rest API config
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
        'django_filters.rest_framework.backends.DjangoFilterBackend',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework.authentication.SessionAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_PAGINATION_CLASS': 'cbcommon.pagination.RemovablePagination',
    'PAGE_SIZE': 20,
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR))), 'media')

# Amazon S3
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')
AWS_QUERYSTRING_AUTH = False  # Remove query parameter authentication from generated URLs
AWS_STATIC_LOCATION = os.environ.get('AWS_STATIC_LOCATION', '')
AWS_MEDIA_LOCATION = os.environ.get('AWS_MEDIA_LOCATION', '')

# Static and media files
STATICFILES_STORAGE = os.environ.get(
    'STATICFILES_STORAGE',
    'django.contrib.staticfiles.storage.StaticFilesStorage'
)
DEFAULT_FILE_STORAGE = os.environ.get(
    'DEFAULT_FILE_STORAGE',
    'django.core.files.storage.FileSystemStorage'
)

# Channels
ASGI_APPLICATION = 'cbcommon.routing.application'
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}

# Health check
HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,
    'MEMORY_MIN': 100,
}

# Phone Numbers
PHONENUMBER_DEFAULT_REGION = 'US'

# Twilio
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', 'ACbec7e51d27f98cde6305c28043ff7a7d')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '44f8d1f1fa559e236cf2c4398642a6e5')
TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER', '+15005550006')

# Google Translate
files = [f for f in os.listdir('.') if os.path.isfile(f)]
for json_file in files:
    if json_file == 'google-application-credentials.json':
        file_dir = dir_path = os.path.dirname(os.path.realpath(json_file))
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f'{file_dir}/{json_file}'


# CrewBoss settings
MAINTENANCE_MODE = bool(os.environ.get('MAINTENANCE_MODE', False))
AUTH_TOKEN_TOKEN_LENGTH = 8
MAINTENANCE_TASK_TIMEOUT_SECONDS = 60
PRIVATE_API_TOKEN = os.environ.get('PRIVATE_API_TOKEN', '')

# Stripe
STRIPE_SECRET_API_KEY = os.environ.get('STRIPE_SECRET_API_KEY', '')
STRIPE_PRODUCT_ID = os.environ.get('STRIPE_PRODUCT_ID', '')

STRIPE_CONTRACTOR_ANNUAL_PLAN_ID = os.environ.get('STRIPE_CONTRACTOR_ANNUAL_PLAN_ID', '')
STRIPE_CONTRACTOR_MONTHLY_PLAN_ID = os.environ.get('STRIPE_CONTRACTOR_MONTHLY_PLAN_ID', '')
STRIPE_BUILDER_ANNUAL_PLAN_ID = os.environ.get('STRIPE_BUILDER_ANNUAL_PLAN_ID', '')
STRIPE_BUILDER_MONTHLY_PLAN_ID = os.environ.get('STRIPE_BUILDER_MONTHLY_PLAN_ID', '')
STRIPE_PLANS = {
    "contractor_annual": STRIPE_CONTRACTOR_ANNUAL_PLAN_ID,
    "contractor_monthly": STRIPE_CONTRACTOR_MONTHLY_PLAN_ID,
    "builder_annual": STRIPE_BUILDER_ANNUAL_PLAN_ID,
    "builder_monthly": STRIPE_BUILDER_MONTHLY_PLAN_ID,
}
STRIPE_CHARGE_SUCCEEDED_SECRET = os.environ.get('STRIPE_CHARGE_SUCCEEDED_SECRET', '')
STRIPE_CHARGE_FAILED_SECRET = os.environ.get('STRIPE_CHARGE_FAILED_SECRET', '')

SMS_FEE = Decimal('0.05')
PRO_PLAN_FEE = Decimal('10')
INTERNAL_SMS_FEE = Decimal('0.01')
INTERNAL_PRO_PLAN_FEE = Decimal('0.59')
LOGIN_REDIRECT_URL = '/'
