import os

from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from imagekitio_storage import app_settings
from imagekitio_storage.storage import RawMediaImagekitStorage, VideoMediaImagekitStorage
from tests.models import TestFileFieldModel, TestFileFieldVideoModel
from tests.tests.test_helpers import get_random_name


class TestModelTests(TestCase):
    def test_file_exists_after_model_instance_with_file_is_saved(self):
        file_name = get_random_name()
        content = ContentFile(b'https://imagekit.io/user/folder/filename.png?file_id=0987654321')
        model = TestFileFieldModel(name='name')
        model.file.save(file_name, content)
        file_name = model.file.name
        storage = RawMediaImagekitStorage()
        try:
            self.assertTrue(storage.exists(file_name))
        finally:
            storage.delete(file_name)


class TestVideoModelTests(TestCase):
    def test_video_can_be_uploaded(self):
        file_name = get_random_name()
        video = File(open(os.path.join('tests', 'files', 'video-file.mp4'), 'rb'))
        model = TestFileFieldVideoModel(name='name')
        model.video.save(file_name, video)
        model.full_clean()
        file_name = model.video.name
        storage = VideoMediaImagekitStorage()
        try:
            self.assertTrue(storage.exists(file_name))
        finally:
            storage.delete(file_name)

    def test_invalid_video_raises_valuation_error(self):
        model = TestFileFieldVideoModel(name='name')
        invalid_file = SimpleUploadedFile(get_random_name(), b'invalid video file', content_type='video/mp4')
        model.video = invalid_file
        with self.assertRaises(ValidationError) as e:
            model.full_clean()
        self.assertEqual(e.exception.messages, [app_settings.INVALID_VIDEO_ERROR_MESSAGE])
