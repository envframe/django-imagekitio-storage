import importlib
import os
import sys
from operator import itemgetter

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.dispatch import receiver
from django.test.signals import setting_changed

from imagekitio_storage import ik_api, get_credentials, IMAGEKIT_URL, IMAGEKIT_PRIVATE_KEY, IMAGEKIT_PUBLIC_KEY, \
    IMAGEKIT_URL_ENDPOINT

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
user_settings = getattr(settings, 'IMAGEKIT_STORAGE', {})

USER_CREDENTIALS = get_credentials(user_settings)

MEDIA_TAG = user_settings.get('MEDIA_TAG', None)
INVALID_VIDEO_ERROR_MESSAGE = user_settings.get('INVALID_VIDEO_ERROR_MESSAGE', 'Please upload a valid video file.')

STATIC_TAG = user_settings.get('STATIC_TAG', None)
STATICFILES_MANIFEST_ROOT = user_settings.get('STATICFILES_MANIFEST_ROOT', os.path.join(BASE_DIR, 'manifest'))

STATIC_IMAGES_EXTENSIONS = user_settings.get('STATIC_IMAGES_EXTENSIONS',
                                             [
                                                 'jpg',
                                                 'jpe',
                                                 'jpeg',
                                                 'jpc',
                                                 'jp2',
                                                 'j2k',
                                                 'wdp',
                                                 'jxr',
                                                 'hdp',
                                                 'png',
                                                 'gif',
                                                 'webp',
                                                 'bmp',
                                                 'tif',
                                                 'tiff',
                                                 'ico'
                                             ])

STATIC_VIDEOS_EXTENSIONS = user_settings.get('STATIC_VIDEOS_EXTENSIONS',
                                             [
                                                 'mp4',
                                                 'webm',
                                                 'flv',
                                                 'mov',
                                                 'ogv',
                                                 '3gp',
                                                 '3g2',
                                                 'wmv',
                                                 'mpeg',
                                                 'flv',
                                                 'mkv',
                                                 'avi'
                                             ])

MAGIC_FILE_PATH = user_settings.get('MAGIC_FILE_PATH', 'magic')

PREFIX = user_settings.get('PREFIX', settings.MEDIA_URL)

DEFAULT_UPLOAD_OPTIONS = {
    "use_unique_file_name": False,
    "tags": None,
    "folder": '/django-imagekitio-storage/',
    "is_private_file": False,
    "custom_coordinates": None,
    "response_fields": None,
    "extensions": None,
    "webhook_url": None,
    "overwrite_file": True,
    "overwrite_ai_tags": False,
    "overwrite_tags": False,
    "overwrite_custom_metadata": True,
    'custom_metadata': None
}

UPLOAD_OPTIONS = user_settings.get('UPLOAD_OPTIONS', DEFAULT_UPLOAD_OPTIONS)
DEFAULT_ROOT_FOLDER = UPLOAD_OPTIONS.get('folder', '/django-imagekitio-storage/')
DEFAULT_MEDIA_FOLDER = MEDIA_TAG
DEFAULT_STATIC_FOLDER = STATIC_TAG


def set_credentials(user_attrs=user_settings):
    try:
        credentials = itemgetter('PRIVATE_KEY', 'PUBLIC_KEY', 'URL_ENDPOINT')(user_attrs)
    except KeyError:
        if IMAGEKIT_URL:
            return
        if IMAGEKIT_PRIVATE_KEY and IMAGEKIT_PUBLIC_KEY and IMAGEKIT_URL_ENDPOINT:
            return
        else:
            raise ImproperlyConfigured('In order to use imagekit storage, you need to provide '
                                       'IMAGEKIT_STORAGE dictionary with PRIVATE_KEY, PUBLIC_KEY '
                                       'and URL_ENDPOINT in the settings or set IMAGEKIT_URL variable '
                                       '(or IMAGEKIT_PUBLIC_KEY, IMAGEKIT_PUBLIC_KEY, IMAGEKIT_URL_ENDPOINT '
                                       'variables).')
    else:
        ik_api.ik_request.private_key = credentials[0]
        ik_api.ik_request.public_key = credentials[1]
        ik_api.ik_request.url_endpoint = credentials[2]


@receiver(setting_changed)
def reload_settings(*args, **kwargs):
    setting_name, value = kwargs['setting'], kwargs['value']
    if setting_name in ['IMAGEKIT_STORAGE', 'MEDIA_URL']:
        importlib.reload(sys.modules[__name__])
