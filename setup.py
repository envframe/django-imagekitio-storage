import codecs
import os

from setuptools import setup


def read(filename):
    return codecs.open(os.path.join(os.path.dirname(__file__), filename)).read()


description = ('Django package that provides Imagekit storages for both media and static files '
               'and management commands for removing unnecessary files.')

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-imagekitio-storage',
    version='0.0.1',
    author='Envframe',
    author_email='envframe@gmail.com',
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/envframe/django-imagekit-storage',
    keywords='django imagekit storage',
    packages=[
        'imagekitio_storage',
        'imagekitio_storage.templatetags',
        'imagekitio_storage.management',
        'imagekitio_storage.management.commands'],
    include_package_data=True,
    install_requires=[
        'requests>=2.28.1',
        'imagekitio>=3.0.1'
    ],
    extras_require={
        'video': ['python-magic>=0.4.27']
    },
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
