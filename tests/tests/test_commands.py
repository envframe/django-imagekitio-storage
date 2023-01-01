import os

from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.test import SimpleTestCase, override_settings
from django.utils import version

from imagekit_storage import app_settings
from imagekit_storage.storage import (MediaImagekitStorage, RawMediaImagekitStorage, StaticImagekitStorage,
                                      StaticHashedImagekitStorage)
from tests.models import TestModel, TestImageModel, TestModelWithoutFile
from tests.tests.test_helpers import (get_random_name, set_media_tag, execute_command,
                                      get_save_calls_counter_in_postprocess_of_adjustable_file,
                                      get_postprocess_counter_of_adjustable_file, import_mock)

mock = import_mock()

DEFAULT_MEDIA_TAG = app_settings.MEDIA_TAG


class BaseOrphanedMediaCommandTestsMixin(object):
    @classmethod
    def setUpClass(cls):
        super(BaseOrphanedMediaCommandTestsMixin, cls).setUpClass()
        set_media_tag(get_random_name())
        TestModelWithoutFile.objects.create(name='without file')
        TestModel.objects.create(name='without file')
        TestImageModel.objects.create(name='without image')
        cls.file = cls.add_file_to_model(TestModel(name='with file')).file.name
        cls.file_2 = cls.add_file_to_model(TestModel(name='with file')).file.name
        image_model_instance = cls.add_file_to_model(TestImageModel(name='with file and image'))
        cls.file_removed = image_model_instance.file.name
        cls.add_file_to_model(image_model_instance)
        cls.file_removed_2 = image_model_instance.file.name
        cls.add_file_to_model(image_model_instance)
        cls.file_3 = image_model_instance.file.name
        image = ImageFile(open(os.path.join('tests', 'dummy-files', 'dummy-image.jpg'), 'rb'))
        image_model_instance.image.save(get_random_name(), image)
        cls.file_4 = image_model_instance.image.name

    @classmethod
    def add_file_to_model(cls, model_instance):
        content = ContentFile(b'Content of file')
        model_instance.file.save(get_random_name(), content)
        return model_instance

    @classmethod
    def tearDownClass(cls):
        super(BaseOrphanedMediaCommandTestsMixin, cls).tearDownClass()
        raw_storage = RawMediaImagekitStorage()
        raw_storage.delete(cls.file)
        raw_storage.delete(cls.file_2)
        raw_storage.delete(cls.file_3)
        raw_storage.delete(cls.file_removed)
        raw_storage.delete(cls.file_removed_2)
        image_storage = MediaImagekitStorage()
        image_storage.delete(cls.file_4)
        set_media_tag(DEFAULT_MEDIA_TAG)


STATIC_FILES = (
    os.path.join('tests', 'css', 'style.css'),
    os.path.join('tests', 'images', 'dummy-static-image.jpg')
)


@override_settings(STATICFILES_STORAGE='imagekit_storage.storage.StaticImagekitStorage')
class CollectStaticCommandTests(SimpleTestCase):
    @mock.patch.object(StaticImagekitStorage, 'save')
    def test_command_saves_static_files(self, save_mock):
        output = execute_command('collectstatic', '--noinput')
        self.assertEqual(save_mock.call_count, 2)
        if version.get_complete_version() >= (2, 0):
            self.assertIn('2 static files copied.', output)
        else:
            for file in STATIC_FILES:
                self.assertIn(file, output)
            self.assertIn('2 static files copied.', output)


@override_settings(STATICFILES_STORAGE='imagekit_storage.storage.StaticHashedImagekitStorage')
@mock.patch.object(StaticHashedImagekitStorage, '_save')
class CollectStaticCommandWithHashedStorageTests(SimpleTestCase):
    @mock.patch.object(StaticHashedImagekitStorage, 'save_manifest')
    def test_command_saves_hashed_static_files(self, save_manifest_mock, save_mock):
        output = execute_command('collectstatic', '--noinput')
        self.assertEqual(save_mock.call_count, 1 * get_save_calls_counter_in_postprocess_of_adjustable_file() + 1)
        if version.get_complete_version() <= (2, 0):
            for file in STATIC_FILES:
                self.assertIn(file, output)
        post_process_counter = 1 + 1 * get_postprocess_counter_of_adjustable_file()
        self.assertIn('0 static files copied, {} post-processed.'.format(post_process_counter), output)

    @mock.patch.object(StaticHashedImagekitStorage, 'save_manifest')
    def test_command_saves_unhashed_static_files_with_upload_unhashed_files_arg(self, save_manifest_mock, save_mock):
        output = execute_command('collectstatic', '--noinput', '--upload-unhashed-files')
        self.assertEqual(save_mock.call_count, 2 + 1 + 1 * get_save_calls_counter_in_postprocess_of_adjustable_file())
        if version.get_complete_version() <= (2, 0):
            for file in STATIC_FILES:
                self.assertIn(file, output)
        post_process_counter = 1 + 1 * get_postprocess_counter_of_adjustable_file()
        self.assertIn('2 static files copied, {} post-processed.'.format(post_process_counter), output)


class CollectStaticCommandWithHashedStorageWithoutMockTests(SimpleTestCase):
    def test_command_saves_manifest_file(self):
        name = get_random_name()
        StaticHashedImagekitStorage.manifest_name = name
        execute_command('collectstatic', '--noinput')
        try:
            manifest_path = os.path.join(app_settings.STATICFILES_MANIFEST_ROOT, name)
            self.assertTrue(os.path.exists(manifest_path))
            os.remove(manifest_path)
        finally:
            StaticHashedImagekitStorage.manifest_name = 'staticfiles.json'
