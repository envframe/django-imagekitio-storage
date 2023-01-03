from django.conf import settings
from django.contrib.staticfiles.management.commands import collectstatic


class Command(collectstatic.Command):
    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('--upload-unhashed-files', action='store_true', dest='upload_unhashed_files',
                            help='Use only when you need it. Use when also want to upload unhashed. ')

    def set_options(self, **options):
        super(Command, self).set_options(**options)
        self.upload_unhashed_files = options['upload_unhashed_files']

    def delete_file(self, path, prefixed_path, source_storage):
        """
        Override to prevent any deleting during command execution.
        """
        return True

    def copy_file(self, path, prefixed_path, source_storage):
        """
        Overwritten to execute only with --upload-unhashed-files param or StaticImagekitStorage.
        Or only hashed files will be uploaded during postprocessing.
        """
        if (settings.STATICFILES_STORAGE == 'imagekitio_storage.storage.StaticImagekitStorage' or
            self.upload_unhashed_files):
            super(Command, self).copy_file(path, prefixed_path, source_storage)
