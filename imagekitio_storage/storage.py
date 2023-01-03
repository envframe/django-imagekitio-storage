import base64
import errno
import json
import os
from urllib.parse import unquote, urlsplit, urlunsplit

import requests
from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import HashedFilesMixin, ManifestFilesMixin
from django.core.files.base import ContentFile, File
from django.core.files.storage import Storage, FileSystemStorage
from django.core.files.uploadedfile import UploadedFile
from django.utils.deconstruct import deconstructible
from imagekitio.exceptions.BadRequestException import BadRequestException
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

from . import app_settings, ik_api
from .helpers import get_resources

RESOURCE_TYPES = {
    'IMAGE': 'image',
    'RAW': 'raw',
    'VIDEO': 'video'
}


@deconstructible
class MediaImagekitStorage(Storage):
    RESOURCE_TYPE = RESOURCE_TYPES['IMAGE']
    TAG = app_settings.MEDIA_TAG
    UPLOAD_OPTIONS = app_settings.UPLOAD_OPTIONS

    def __init__(self, tag=None, resource_type=None, root_folder=None):
        if root_folder is not None:
            self.UPLOAD_OPTIONS['folder'] = root_folder
        if tag is not None:
            self.TAG = tag.strip('/') if tag is not None else None
        if resource_type is not None:
            self.RESOURCE_TYPE = resource_type

    def _get_resource_type(self, name):
        """
        Implemented to allow different resource types per file name
        within one storage class.
        """
        return self.RESOURCE_TYPE

    def _open(self, name, mode='rb'):
        url = self._get_url(name)
        response = requests.get(url)
        if response.status_code == 404:
            raise IOError
        response.raise_for_status()
        file = ContentFile(response.content)
        file.name = name
        file.mode = mode
        return file

    def _upload(self, file, file_name, options):
        return ik_api.upload(file=file, file_name=file_name, options=options)

    def _save(self, name, content):

        self.UPLOAD_OPTIONS['folder'] = self._get_upload_path(name)

        options = UploadFileRequestOptions(**self.UPLOAD_OPTIONS)

        name = self._normalise_name(name)
        name = self._prepend_prefix(name)

        content = UploadedFile(content, name)

        encoded = base64.b64encode(content.read())

        response = self._upload(file=encoded, file_name=name, options=options)

        return response.file_id

    def delete(self, name):
        file_id = str(name)

        response = ik_api.delete_file(file_id=file_id)
        if response:
            return response.response_metadata
        return super().delete(name)

    def _get_url(self, name):
        try:
            response = ik_api.get_file_details(file_id=name)
            return response.url
        except BadRequestException:
            return name

    def url(self, name):
        return self._get_url(name)

    def exists(self, name):
        url = self._get_url(name)
        response = requests.head(url)
        if response.status_code == 404:
            return False
        response.raise_for_status()
        return True

    def size(self, name):
        url = self._get_url(name)
        response = requests.head(url)
        if response.status_code == 200:
            return int(response.headers['content-length'])
        else:
            return None

    def get_available_name(self, name, max_length=None):
        if max_length is None:
            return name
        else:
            return name[:max_length]

    def _normalize_path(self, path):
        if path != '' and not path.endswith('/'):
            path += '/'
        return path

    def _get_prefix(self):
        return app_settings.PREFIX if app_settings.PREFIX is not None else ''

    def _prepend_prefix(self, name):
        prefix = self._get_prefix().lstrip('/')
        prefix = self._normalize_path(prefix)
        if not name.startswith(prefix):
            name = prefix + name
        return name

    def listdir(self, path):
        path = self._normalize_path(path)
        print(path)
        resources = get_resources(path)
        directories = set()
        files = []
        for resource in resources:
            resource_tail = resource.replace(path, '', 1)
            if '/' in resource_tail:
                directory = resource_tail.split('/', 1)[0]
                directories.add(directory)
            else:
                files.append(resource_tail)
        return list(directories), files

    def _normalise_name(self, name):
        return name.replace('\\', '/')

    def _get_root_folder(self):
        return self.UPLOAD_OPTIONS['folder'].strip('/') if self.UPLOAD_OPTIONS['folder'] is not None else None

    def _get_upload_path(self, name):
        root = self._get_root_folder()

        folder = os.path.dirname(name)

        if folder:
            tagged_dir = f"{root}/{self.TAG}/{folder}"
            normal_dir = f"{root}/{folder}"

            folder = tagged_dir if self.TAG is not None else normal_dir

            return folder
        return root if self.TAG is None else f"{root}/{self.TAG}"


class RawMediaImagekitStorage(MediaImagekitStorage):
    RESOURCE_TYPE = RESOURCE_TYPES['RAW']


class VideoMediaImagekitStorage(MediaImagekitStorage):
    RESOURCE_TYPE = RESOURCE_TYPES['VIDEO']


storages_per_type = {
    RESOURCE_TYPES['IMAGE']: MediaImagekitStorage(),
    RESOURCE_TYPES['RAW']: RawMediaImagekitStorage(),
    RESOURCE_TYPES['VIDEO']: VideoMediaImagekitStorage(),
}


class StaticImagekitStorage(MediaImagekitStorage):
    """
    Base storage for staticfiles kept in Imagekit.
    Uploads only unhashed files, so it is highly unrecommended to use it directly,
    because static files are cached both by Imagekit CDN and browsers
    and changing files could become problematic.
    """
    RESOURCE_TYPE = RESOURCE_TYPES['RAW']
    TAG = app_settings.STATIC_TAG
    UPLOAD_OPTIONS = app_settings.UPLOAD_OPTIONS

    def _get_resource_type(self, name):
        """
        Implemented as static files can be of different resource types.
        Because web developers are the people who control those files, we can distinguish them
        simply by looking at their extensions, we don't need any content based validation.
        """
        extension = self._get_file_extension(name)
        if extension is None:
            return self.RESOURCE_TYPE
        elif extension in app_settings.STATIC_IMAGES_EXTENSIONS:
            return RESOURCE_TYPES['IMAGE']
        elif extension in app_settings.STATIC_VIDEOS_EXTENSIONS:
            return RESOURCE_TYPES['VIDEO']
        else:
            return self.RESOURCE_TYPE

    @staticmethod
    def _get_file_extension(name):
        substrings = name.split('.')
        if len(substrings) == 1:
            return None
        else:
            return substrings[-1].lower()

    def url(self, name):
        if settings.DEBUG:
            return settings.STATIC_URL + name
        return super(StaticImagekitStorage, self).url(name)

    def _upload(self, file, file_name, options=None):
        name = self._remove_extension_for_non_raw_file(file_name)
        if options is None:
            self.UPLOAD_OPTIONS['folder'] = self._get_upload_path(name)

            options = UploadFileRequestOptions(**self.UPLOAD_OPTIONS)

        return ik_api.upload_file(file=file, file_name=name, options=options)

    def _remove_extension_for_non_raw_file(self, name):
        """
        Implemented as image and video files' Imagekit public id
        shouldn't contain file extensions, otherwise Imagekit url
        would contain doubled extension - Imagekit adds extension to url
        to allow file conversion to arbitrary file, like png to jpg.
        """
        file_resource_type = self._get_resource_type(name)
        if file_resource_type is None or file_resource_type == self.RESOURCE_TYPE:
            return name
        else:
            extension = self._get_file_extension(name)
            return name[:-len(extension) - 1]

    # we only need 2 methods of HashedFilesMixin, so we just copy them as function objects to avoid MRO complexities
    file_hash = HashedFilesMixin.file_hash
    clean_name = HashedFilesMixin.clean_name

    def _exists_with_etag(self, name, content):
        """
        Checks whether a file with a name and a content is already uploaded to Imagekit.
        Uses ETAG header and MD5 hash for the content comparison.
        """
        url = self._get_url(name)
        response = requests.head(url)
        if response.status_code == 404:
            return False
        etag = response.headers['ETAG'].split('"')[1]
        hash = self.file_hash(name, content)
        return etag.startswith(hash)

    def _save(self, name, content):
        """
        Saves only when a file with a name and a content is not already uploaded to Imagekit.
        """
        name = self.clean_name(name)  # to change to UNIX style path on windows if necessary
        if not self._exists_with_etag(name, content):
            content.seek(0)
            super(StaticImagekitStorage, self)._save(name, content)
        return self._prepend_prefix(name)

    def _get_prefix(self):
        return settings.STATIC_URL

    def listdir(self, path):
        """
        Not implemented as static assets can be of different resource types
        in contrast to media storages, which are specialized per given resource type.
        That's why we cannot use parent's class listdir.
        This method could be implemented in the future if there is a demand for it.
        """
        raise NotImplementedError()

    def stored_name(self, name):
        """
        Implemented to standardize interface
        for StaticImagekitStorage and StaticHashedImagekitStorage
        """
        return self._prepend_prefix(name)


class ManifestImagekitStorage(FileSystemStorage):
    """
    Storage for manifest file which will keep map of hashed paths.
    Subclasses FileSystemStorage, so the manifest file is kept locally.
    It is highly recommended to keep the manifest in your version control system,
    then you are guaranteed the manifest will be used in all production environment,
    including Heroku and AWS Elastic Beanstalk.
    """

    def __init__(self, location=None, base_url=None, *args, **kwargs):
        location = app_settings.STATICFILES_MANIFEST_ROOT if location is None else location
        super(ManifestImagekitStorage, self).__init__(location, base_url, *args, **kwargs)


class HashImagekitMixin(object):
    def __init__(self, *args, **kwargs):
        self.manifest_storage = ManifestImagekitStorage()
        super(HashImagekitMixin, self).__init__(*args, **kwargs)

    def hashed_name(self, name, content=None, filename=None):
        parsed_name = urlsplit(unquote(name))
        clean_name = parsed_name.path.strip()
        opened = False
        if content is None:
            absolute_path = finders.find(clean_name)
            try:
                content = open(absolute_path, 'rb')
            except (IOError, OSError) as e:
                if e.errno == errno.ENOENT:
                    raise ValueError("The file '%s' could not be found with %r." % (clean_name, self))
                else:
                    raise
            content = File(content)
            opened = True
        try:
            file_hash = self.file_hash(clean_name, content)
        finally:
            if opened:
                content.close()
        path, filename = os.path.split(clean_name)
        root, ext = os.path.splitext(filename)
        if file_hash is not None:
            file_hash = ".%s" % file_hash
        hashed_name = os.path.join(path, "%s%s%s" % (root, file_hash, ext))
        unparsed_name = list(parsed_name)
        unparsed_name[2] = hashed_name

        if '?#' in name and not unparsed_name[3]:
            unparsed_name[2] += '?'
        return urlunsplit(unparsed_name)

    def post_process(self, paths, dry_run=False, **options):
        original_exists = self.exists
        self.exists = lambda name: False  # temporarily overwritten to prevent any exist check
        for response in super(HashImagekitMixin, self).post_process(paths, dry_run, **options):
            yield response
        self.exists = original_exists

    def read_manifest(self):
        try:
            with self.manifest_storage.open(self.manifest_name) as manifest:
                return manifest.read().decode('utf-8')
        except IOError:
            return None

    def add_unix_path_keys_to_paths(self, paths):
        for path in paths.copy():
            if '\\' in path:
                clean_path = self.clean_name(path)
                paths[clean_path] = paths[path]

    def save_manifest(self):
        payload = {'paths': self.hashed_files, 'version': self.manifest_version}
        if os.name == 'nt':
            paths = payload['paths']
            self.add_unix_path_keys_to_paths(paths)
        if self.manifest_storage.exists(self.manifest_name):
            self.manifest_storage.delete(self.manifest_name)
        contents = json.dumps(payload).encode('utf-8')
        self.manifest_storage._save(content=ContentFile(contents), name=self.manifest_name)

    # we only need 1 method of HashedFilesMixin, so we just copy it as function objects to avoid MRO complexities
    stored_name = HashedFilesMixin.stored_name


class StaticHashedImagekitStorage(HashImagekitMixin, ManifestFilesMixin, StaticImagekitStorage):
    pass
