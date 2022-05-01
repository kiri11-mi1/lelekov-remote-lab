from setuptools import setup, find_packages
from os.path import join, dirname


setup(
    name='lelekov_remote_lab',
    description='Библиотека для управления системой ориентации',
    version='1.0',
    packages=find_packages(),
    long_description_content_type='text/markdown',
    long_description=open(join(dirname(__file__), 'ReadMe.md'), encoding='utf-8').read(),
    install_requires=[
        'matplotlib',
        'numpy'
    ],
)

