#!/usr/bin/env python
import setuptools
from distutils.core import setup

with open("requirements.txt") as requirements:
    required = requirements.read().splitlines()

kwargs = {
    "packages": setuptools.find_packages(),
    "install_requires": required[1:],
    "classifiers": [
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
}

setup(**kwargs)
