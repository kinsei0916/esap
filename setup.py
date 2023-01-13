"""Setup script for Esap."""
from __future__ import print_function

import sys

if sys.version_info < (3, 7):
  print('esap requires python3 version >= 3.7.', file=sys.stderr)
  sys.exit(1)

import io
import os

from setuptools import setup

packages = ['esap']

install_requires = [
    'httplib2>=0.15.0,<1dev',
    'lxml>=4.0.0,<5',
    'pandas>=1.3.0,<2',
    'tabulate>=0.8.10,<1',
]

package_root = os.path.abspath(os.path.dirname(__file__))

readme_filename = os.path.join(package_root, 'README.md')
with io.open(readme_filename, encoding='utf-8') as readme_file:
  readme = readme_file.read()

version = {}
with open(os.path.join(package_root, 'esap/version.py'),
          mode='r',
          encoding='utf-8') as fp:
  exec(fp.read(), version)
version = version['__version__']

setup(
    name='esap',
    version=version,
    description='Utilities for esa',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='kinsei0916',
    author_email='kinsei0916@gmail.com',
    url='https://github.com/kinsei0916/esap/',
    install_requires=install_requires,
    python_requires='>=3.7',
    packages=packages,
    license='Apache 2.0',
    keywords='esa api client',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
