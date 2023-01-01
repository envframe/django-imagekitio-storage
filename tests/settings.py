import os

from django.core.management.utils import get_random_secret_key

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG = True
ALLOWED_HOSTS = ['*']
SECRET_KEY = get_random_secret_key()
ROOT_URLCONF = 'tests.urls'

WSGI_APPLICATION = "tests.wsgi.application"

INSTALLED_APPS = [
    'tests',
    'imagekit_storage',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],  # os.path.join(BASE_DIR, "templates"),
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

STATIC_URL = '/static/'
STATICFILES_STORAGE = 'imagekit_storage.storage.StaticHashedImagekitStorage'

MEDIA_URL = '/media/'
DEFAULT_FILE_STORAGE = 'imagekit_storage.storage.MediaImagekitStorage'

IMAGEKIT_STORAGE = {
    'PRIVATE_KEY': os.getenv('IMAGEKIT_PRIVATE_KEY', 'private_BX/xxx='),
    'PUBLIC_KEY': os.getenv('IMAGEKIT_PUBLIC_KEY', 'public_r/xxx='),
    'URL_ENDPOINT': os.getenv('IMAGEKIT_URL_ENDPOINT', 'https://ik.imagekit.io/xxx'),
    'MEDIA_TAG': 'media',
    'INVALID_VIDEO_ERROR_MESSAGE': 'Please upload a valid video file.',
    'EXCLUDE_DELETE_ORPHANED_MEDIA_PATHS': (),
    'STATIC_TAG': 'static',
    'STATICFILES_MANIFEST_ROOT': os.path.join(BASE_DIR, 'manifest'),
    'STATIC_IMAGES_EXTENSIONS': ['jpg', 'jpe', 'jpeg', 'jpc', 'jp2', 'j2k', 'wdp', 'jxr',
                                 'hdp', 'png', 'gif', 'webp', 'bmp', 'tif', 'tiff', 'ico'],
    'STATIC_VIDEOS_EXTENSIONS': ['mp4', 'webm', 'flv', 'mov', 'ogv', '3gp', '3g2', 'wmv',
                                 'mpeg', 'flv', 'mkv', 'avi'],
    'MAGIC_FILE_PATH': 'magic',
    'PREFIX': MEDIA_URL,
    'UPLOAD_OPTIONS': {
        "use_unique_file_name": False,
        "tags": ['django', 'imagekit', 'storage', 'tests'],
        "folder": '/django-imagekit-storage-tests/',
        "is_private_file": False,
        "custom_coordinates": None,
        "response_fields": None,
        "extensions": None,
        "webhook_url": None,
        "overwrite_file": True,
        "overwrite_ai_tags": False,
        "overwrite_tags": False,
        "overwrite_custom_metadata": True
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}
