from django.db import models
from django.forms.models import model_to_dict

from imagekitio_storage import ik_api


def imagekit_delete_file_receiver(signal=None, **kwargs):
    if signal is None:
        signal = models.signals.post_delete

    def _decorator(func):
        if isinstance(signal, (list, tuple)):
            for s in signal:
                s.connect(func, **kwargs)
        else:
            signal.connect(func, **kwargs)
        return func

    return _decorator


def _delete_files(file):
    """ Deletes files from imagekitio. """
    file_id = str(file)

    response = ik_api.delete_file(file_id=file_id)
    return response.response_metadata


def delete_imagekit_files(instance=None, fields=None, *args, **kwargs):
    if fields is None:
        fields = []

    if instance:
        model = model_to_dict(instance)

        for field in fields:
            if model[field]:
                _delete_files(model[field])
            else:
                raise KeyError(f"{field} is not found in instance")
