import os
from django.db import models

from django.forms.models import model_to_dict

from imagekit_storage import imagekit


def delete_imagekit_file_receiver(signal=None, **kwargs):
    """
    A decorator for connecting receivers to signals. Used by passing in the
    signal (or list of signals) and keyword arguments to connect::

        @receiver(post_save, sender=MyModel)
        def signal_receiver(sender, **kwargs):
            ...

        @receiver([post_save, post_delete], sender=MyModel)
        def signals_receiver(sender, **kwargs):
            ...
    """

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


def _delete_file(path):
    """ Deletes file from imagekitio. """
    response = imagekit.delete_file(file_id=str(path).split('?file_id=')[1])
    return response.response_metadata


def delete_imagekit_file(instance=None, field=None, *args, **kwargs):
    model = model_to_dict(instance)
    if instance and model[field]:
        _delete_file(model[field])
