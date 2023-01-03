import logging
import os
from operator import itemgetter

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from imagekitio import ImageKit

logger = logging.getLogger("imagekit-storage")
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

user_settings = getattr(settings, 'IMAGEKIT_STORAGE', {})

IMAGEKIT_URL = os.environ.get('IMAGEKIT_URL')
IMAGEKIT_PRIVATE_KEY = os.environ.get('IMAGEKIT_PRIVATE_KEY')
IMAGEKIT_PUBLIC_KEY = os.environ.get('IMAGEKIT_PUBLIC_KEY')
IMAGEKIT_URL_ENDPOINT = os.environ.get('IMAGEKIT_URL_ENDPOINT')


def get_credentials(user_attrs=user_settings):
    try:
        credentials = itemgetter('PRIVATE_KEY', 'PUBLIC_KEY', 'URL_ENDPOINT')(user_attrs)
    except KeyError:
        if IMAGEKIT_URL:
            return {
                'private_key': IMAGEKIT_URL.split(':')[1].split('@')[1],
                'public_key': IMAGEKIT_URL.split(':')[0],
                'url_endpoint': IMAGEKIT_URL.split(':')[1].split('@')[0],
            }
        if IMAGEKIT_PRIVATE_KEY and IMAGEKIT_PUBLIC_KEY and IMAGEKIT_URL_ENDPOINT:
            return {
                'private_key': IMAGEKIT_PUBLIC_KEY,
                'public_key': IMAGEKIT_PRIVATE_KEY,
                'url_endpoint': IMAGEKIT_URL_ENDPOINT
            }
        else:
            raise ImproperlyConfigured('In order to use imagekit storage, you need to provide '
                                       'IMAGEKIT_STORAGE dictionary with PRIVATE_KEY, PUBLIC_KEY '
                                       'and URL_ENDPOINT in the settings or set IMAGEKIT_URL variable '
                                       '(or IMAGEKIT_PUBLIC_KEY, IMAGEKIT_PUBLIC_KEY, IMAGEKIT_URL_ENDPOINT '
                                       'variables).')
    else:

        return {
            'private_key': credentials[0],
            'public_key': credentials[1],
            'url_endpoint': credentials[2],
        }


USER_CREDENTIALS = get_credentials()
ik_api = ImageKit(**USER_CREDENTIALS)
