#!/usr/bin/env python

import os
import setuptools

from distutils.core import setup


with open("rubberband/version.py") as f:
    exec(f.read())

with open('requirements.txt') as requirements:
    # setuptools can't parse -e (ipet)
    required = requirements.read().splitlines()[1:]

kwargs = {
    "name": "rubberband",
    "version": str(__version__),  # noqa
    "packages": setuptools.find_packages(),
    "description": "An elasticsearch front-end for experiment run log viewing and analysis.",
    "long_description": open("README.md").read(),
    "author": "Cristina Munoz",
    "maintainer": "Cristina Munoz",
    "author_email": "munoz@zib.de",
    "maintainer_email": "munoz@zib.de",
    "license": "MIT",
    "install_requires": required,
    "dependency_links": ["git+git@git.zib.de:optimization/ipet-reader.git#egg=ipet-reader"],
    "url": "https://git.zib.de/optimizaiton/rubberband",
    "download_url": "https://git.zib.de/optimization/rubberband/archive/master.tar.gz",
    "classifiers": [
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
}

setup(**kwargs)
