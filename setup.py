from setuptools import setup, find_packages
from pathlib import Path

version = '0.0.1'

directory = Path(__file__).parent

with open(Path(directory, 'README.md'), 'r') as file:
    if file.readable():
        long_description = file.read()
    else:
        long_description = ''


setup(
    name='file-alchemy',
    version=version,
    description='Library for managing files associated with sqlalchemy database',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/StannisGr/file-alchemy',
    author='StannisGr',
    author_email='bvc344@gmail.com',
    license='Apache License 2.0',
    platforms=['any'],
    keywords='file upload, file managment, sqlalchemy, flask',
    packages=find_packages(where='file_alchemy/*',exclude=('tests/*',)),
    include_package_data=True,
    install_requires=[
        'Pillow>=9.3.0'
    ],
)