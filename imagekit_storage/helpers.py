from imagekit_storage import imagekit
from imagekitio.models.ListAndSearchFileRequestOptions import ListAndSearchFileRequestOptions


def get_resources(path):
    options = ListAndSearchFileRequestOptions(
        type='file',
        sort='ASC_CREATED',
        path=path,
        file_type='all',
    )
    resources = []
    while True:
        response = imagekit.list_files(options=options)
        for resource in response.list:
            resources.append(resource)
        return resources
