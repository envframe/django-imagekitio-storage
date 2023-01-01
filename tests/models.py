from django.db import models

from imagekit_storage.delete import delete_imagekit_file, delete_imagekit_file_receiver
from imagekit_storage.storage import MediaImagekitStorage, RawMediaImagekitStorage, VideoMediaImagekitStorage
from imagekit_storage.validators import validate_video


class TestModel(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='tests/', blank=True, storage=RawMediaImagekitStorage())


class TestImageModel(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='tests/', blank=True, storage=RawMediaImagekitStorage())
    image = models.ImageField(upload_to='tests-images/', blank=True, storage=MediaImagekitStorage())


class TestModelWithoutFile(models.Model):
    name = models.CharField(max_length=100)


class TestVideoModel(models.Model):
    name = models.CharField(max_length=100)
    video = models.FileField(upload_to='tests-videos/', blank=True, storage=VideoMediaImagekitStorage(),
                             validators=[validate_video])


@delete_imagekit_file_receiver(sender=TestModel)
def delete_test_model_file(instance, *args, **kwargs):
    delete_imagekit_file(instance=instance, field='file', *args, **kwargs)
