#!/usr/bin/env python
import setuptools
from distutils.core import setup


with open("rubberband/version.py") as f:
    exec(f.read())

with open('requirements.txt') as requirements:
    required = requirements.read().splitlines()

kwargs = {
    "name": "rubberband",
    "version": str(__version__),  # noqa
    "packages": setuptools.find_packages(),
    "description": "A flexible archiving platform for optimization benchmarks",
    "long_description": open("README.md").read(),
    "author": "Cristina Muñoz",
    "maintainer": "Cristina Muñoz",
    "author_email": "hi@xmunoz.com",
    "maintainer_email": "hi@xmunoz.com",
    "license": "MIT",
    "install_requires": required,
    "url": "https://github.com/xmunoz/rubberband",
    "download_url": "https://github.com/xmunoz/rubberband/archive/master.zip",
    "classifiers": [
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
}

setup(**kwargs)
