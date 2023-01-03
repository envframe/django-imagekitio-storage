from django.db import models
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFit

from imagekitio_storage.delete import delete_imagekit_files, imagekit_delete_file_receiver
from imagekitio_storage.storage import MediaImagekitStorage, RawMediaImagekitStorage, VideoMediaImagekitStorage
from imagekitio_storage.validators import validate_video


class TestFileFieldModel(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='raw-file-tests/', blank=True, storage=RawMediaImagekitStorage())

    def __str__(self):
        return str(self.file)


class TestFileAndImageFieldModel(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='raw-file-tests/', blank=True, storage=RawMediaImagekitStorage())
    image = models.ImageField(upload_to='image-file-tests/', blank=True, storage=MediaImagekitStorage())

    def __str__(self):
        return "File: {file} - Image: {image}".format(file=self.file, image=self.image)


class TestWithoutMediaModel(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)


class TestFileFieldVideoModel(models.Model):
    name = models.CharField(max_length=100)
    video = models.FileField(upload_to='video-file-tests/', blank=True, storage=VideoMediaImagekitStorage(),
                             validators=[validate_video])

    def __str__(self):
        return str(self.video)


class TestThirdPartyFieldModel(models.Model):
    name = models.CharField(max_length=100)
    file = ProcessedImageField(
        upload_to='third-party-raw-file-tests/',
        width_field="width",
        height_field="height",
        processors=[ResizeToFit(1280)],
        options={"quality": 80},
        blank=True,
        storage=RawMediaImagekitStorage()
    )
    image = ProcessedImageField(
        upload_to='third-party-image-tests/',
        width_field="width",
        height_field="height",
        processors=[ResizeToFit(1280)],
        options={"quality": 80},
        blank=True,
        storage=MediaImagekitStorage()
    )
    width = models.IntegerField(default=0, null=True)
    height = models.IntegerField(default=0, null=True)

    def __str__(self):
        return "File: {file} - Image: {image}".format(file=self.file, image=self.image)


@imagekit_delete_file_receiver(sender=TestFileFieldModel)
def delete_test_file_field_model_file(instance, *args, **kwargs):
    delete_imagekit_files(instance=instance, fields=['file'], *args, **kwargs)


@imagekit_delete_file_receiver(sender=TestFileAndImageFieldModel)
def delete_test_file_image_field_model_file(instance, *args, **kwargs):
    delete_imagekit_files(instance=instance, fields=['file', 'image'], *args, **kwargs)


@imagekit_delete_file_receiver(sender=TestFileFieldVideoModel)
def delete_test_file_field_video_model_file(instance, *args, **kwargs):
    delete_imagekit_files(instance=instance, fields=['video'], *args, **kwargs)


@imagekit_delete_file_receiver(sender=TestThirdPartyFieldModel)
def delete_test_third_party_field_video_model_file(instance, *args, **kwargs):
    delete_imagekit_files(instance=instance, fields=['file', 'image'], *args, **kwargs)
