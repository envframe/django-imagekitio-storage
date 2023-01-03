from django.test import SimpleTestCase, override_settings

from imagekitio_storage.storage import StaticHashedImagekitStorage
from tests.tests.test_helpers import execute_command, StaticHashedStorageTestsMixin, import_mock

mock = import_mock()


@override_settings(STATICFILES_STORAGE='imagekitio_storage.storage.StaticImagekitStorage')
class IndexPageTestsWithUnhashedStaticStorageTests(SimpleTestCase):
    @override_settings(DEBUG=True)
    def test_urls_with_debug_true(self):
        response = self.client.get('/')
        self.assertContains(response, '/static/tests/css/style.css')

    def test_urls_with_debug_false(self):
        response = self.client.get('/')
        self.assertContains(response, '/raw/upload/v1/static/tests/css/style.css')


@override_settings(STATICFILES_STORAGE='imagekitio_storage.storage.StaticHashedImagekitStorage')
class IndexPageTestsWithStaticHashedStorageTests(StaticHashedStorageTestsMixin, SimpleTestCase):
    @override_settings(DEBUG=True)
    def test_urls_with_debug_true(self):
        response = self.client.get('/')
        self.assertContains(response, '/static/tests/css/style.css')

    def test_urls_with_debug_false(self):
        response = self.client.get('/')
        self.assertContains(response, '/raw/upload/v1/static/tests/css/style.{}.css'.format(self.style_hash))


@override_settings(STATICFILES_STORAGE='imagekitio_storage.storage.StaticHashedImagekitStorage')
class IndexPageTestsWithStaticHashedStorageWithManifestTests(StaticHashedStorageTestsMixin, SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super(IndexPageTestsWithStaticHashedStorageWithManifestTests, cls).setUpClass()
        with mock.patch.object(StaticHashedImagekitStorage, '_upload'):
            execute_command('collectstatic', '--noinput')
            with open(cls.manifest_path) as f:
                cls.manifest = f.read()

    @override_settings(DEBUG=True)
    def test_urls_with_debug_true(self):
        response = self.client.get('/')
        self.assertContains(response, '/static/tests/css/style.css')

    def test_urls_with_debug_false(self):
        response = self.client.get('/')
        self.assertContains(response, '/raw/upload/v1/static/tests/css/style.{}.css'.format(self.style_hash))

    @mock.patch.object(StaticHashedImagekitStorage, 'hashed_name')
    def test_manifest_is_used_in_production(self, hashed_name_mock):
        self.client.get('/')
        self.assertFalse(hashed_name_mock.called)

    def test_manifest_has_correct_content(self):
        self.assertIn('tests/css/style.css', self.manifest)
        self.assertIn('tests/css/style.{}.css'.format(self.style_hash), self.manifest)
