#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os
import re

from setuptools import find_packages, setup

NAME = 'srec2bin'
PACKAGES = find_packages(where='.')
META_PATH = os.path.join('srec2bin', '__init__.py')
KEYWORDS = ['motorola', 'srecord', 'S3']
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Other Environment',
    'Natural Language :: English',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX',
    'Operating System :: Win32',
    'Programming Language :: Python :: 3.5',
    'Topic :: Software Development :: Libraries :: Python Modules',
]
INSTALL_REQUIRES = [
]

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), 'rb', 'utf-8') as f:
        return f.read()


META_FILE = read(META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


if __name__ == '__main__':
    setup(
        name=NAME,
        description=find_meta('description'),
        license=find_meta('license'),
        url=find_meta('uri'),
        version=find_meta('version'),
        author=find_meta('author'),
        author_email=find_meta('email'),
        maintainer=find_meta('author'),
        maintainer_email=find_meta('email'),
        keywords=KEYWORDS,
        long_description=read('README.md'),
        packages=PACKAGES,
        # package_dir={'srec2bin': 'srec2bin'},
        # package_data={'srec2bin': ['*.rst']},
        scripts=['bin/srec2bin.py'],
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        python_requires='>=3.5',
    )
