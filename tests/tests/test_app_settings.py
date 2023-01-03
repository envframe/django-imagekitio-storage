import os

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings

from imagekitio_storage import app_settings
from imagekitio_storage.app_settings import set_credentials
from .test_helpers import import_mock

mock = import_mock()


@mock.patch.dict(os.environ, {}, clear=True)
class SetCredentialsWithoutEnvVariablesTests(SimpleTestCase):
    def assert_incomplete_settings_raise_error(self, settings):
        with self.assertRaises(ImproperlyConfigured):
            set_credentials(settings)

    def test_missing_PRIVATE_KEY_setting_raises_error(self):
        self.assert_incomplete_settings_raise_error({'URL_ENDPOINT': 'url_endpoint'})

    def test_missing_API_url_endpoint_setting_raises_error(self):
        self.assert_incomplete_settings_raise_error({'PRIVATE_KEY': 'private_key'})

    def test_missing_PUBLIC_KEY_setting_raises_error(self):
        self.assert_incomplete_settings_raise_error({'PRIVATE_KEY': 'private_key', 'URL_ENDPOINT': 'url_endpoint'})

    @mock.patch('imagekitio_storage.app_settings.imagekit.config')
    def test_proper_configuration_correctly_sets_credentials(self, config_mock):
        set_credentials({'PRIVATE_KEY': 'private_key', 'URL_ENDPOINT': 'url_endpoint', 'PUBLIC_KEY': 'public_key'})
        config_mock.assert_called_once_with(private_key='private_key', url_endpoint='url_endpoint',
                                            public_key='public_key')


class SetCredentialsWithEnvVariablesTests(SimpleTestCase):
    def assert_incomplete_settings_raise_error(self, settings={}):
        with self.assertRaises(ImproperlyConfigured):
            set_credentials(settings)

    @mock.patch.dict(os.environ, {'IMAGEKIT_URL_ENDPOINT': 'url_endpoint', 'IMAGEKIT_PUBLIC_KEY': 'public_key'},
                     clear=True)
    def test_missing_PRIVATE_KEY_variable_raises_error(self):
        self.assert_incomplete_settings_raise_error()

    @mock.patch.dict(os.environ, {'IMAGEKIT_PRIVATE_KEY': 'private_key', 'IMAGEKIT_PUBLIC_KEY': 'public_key'},
                     clear=True)
    def test_missing_API_url_endpoint_variable_raises_error(self):
        self.assert_incomplete_settings_raise_error()

    @mock.patch.dict(os.environ, {'IMAGEKIT_PRIVATE_KEY': 'private_key', 'IMAGEKIT_URL_ENDPOINT': 'url_endpoint'},
                     clear=True)
    def test_missing_PUBLIC_KEY_variable_raises_error(self):
        self.assert_incomplete_settings_raise_error()

    @mock.patch('imagekitio_storage.app_settings.imagekit.config')
    @mock.patch.dict(os.environ,
                     {
                         'IMAGEKIT_PRIVATE_KEY': 'private_key',
                         'IMAGEKIT_URL_ENDPOINT': 'url_endpoint',
                         'IMAGEKIT_PUBLIC_KEY': 'public_key'
                     },
                     clear=True)
    def test_complete_set_of_env_variables_doesnt_raise_error(self, config_mock):
        set_credentials({})
        self.assertFalse(config_mock.called)

    @mock.patch.dict(os.environ, {'IMAGEKIT_URL': 'my-url'}, clear=True)
    @mock.patch('imagekitio_storage.app_settings.imagekit.config')
    def test_IMAGEKIT_URL_env_variable_doesnt_raise_error(self, config_mock):
        set_credentials({})
        self.assertFalse(config_mock.called)


class OverrideSettingsTests(SimpleTestCase):
    def test_override_settings(self):
        old_value = app_settings.MEDIA_TAG
        with override_settings(IMAGEKIT_STORAGE={'MEDIA_TAG': 'test'}):
            self.assertEqual(app_settings.MEDIA_TAG, 'test')
        self.assertEqual(app_settings.MEDIA_TAG, old_value)
