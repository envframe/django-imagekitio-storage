import os

from imagekitio.models.ListAndSearchFileRequestOptions import ListAndSearchFileRequestOptions

from imagekitio_storage import ik_api, app_settings


def get_resources(path):
    options = ListAndSearchFileRequestOptions(
        type='file',
        sort='ASC_CREATED',
        path=path,
        file_type='all',
    )
    resources = []
    while True:
        response = ik_api.list_files(options=options)
        for resource in response.list:
            resources.append(resource.url)
        return resources


def get_resources_query(type: str = None,
                        sort: str = None,
                        path: str = None,
                        search_query: str = None,
                        file_type: str = None,
                        limit: int = None,
                        skip: int = None,
                        tags=None):
    options = ListAndSearchFileRequestOptions(
        type=type or 'file',
        sort=sort or 'ASC_CREATED',
        path=path,
        file_type=file_type or 'all',
        search_query=search_query,
        limit=limit,
        skip=skip,
        tags=tags,
    )
    resources = []
    while True:
        response = ik_api.list_files(options=options)
        for resource in response.list:
            resources.append(resource.__dict__)
        return resources


def get_uploaded_media_file_name_from_url(url, index=-1):
    url = str(url)
    endpoint = app_settings.get_credentials()['url_endpoint']
    url = url.split(endpoint)[1]
    url = url.split('/')[index]
    return url


def get_uploaded_media_path_from_url(url):
    url = str(url)

    endpoint = app_settings.get_credentials()['url_endpoint']
    file = get_uploaded_media_file_name_from_url(url)
    url = url.split(endpoint)[1]
    url = url.split(file)[0].strip('/')
    print(url)
    return url


def set_upload_path(name, tag):
    tag = tag.strip('/') if tag is not None else None
    upload_options = app_settings.UPLOAD_OPTIONS

    default_folder = str(upload_options['folder']).strip('/')

    folder = os.path.dirname(name)

    tagged_dir = f"{default_folder}/{tag}/{folder}"
    normal_dir = f"{default_folder}/{folder}"

    path = tagged_dir if tag is not None else normal_dir
    return path
