#!/usr/bin/env python
from importlib.machinery import SourceFileLoader

from setuptools import find_packages, setup

version = SourceFileLoader("version", "starlette-i18n/version.py").load_module()


CLASSIFIERS = [
    "Development Status :: 3 - Beta",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Operating System :: OS Independent",
    "Topic :: System :: Networking",
    "Topic :: Software Development",
    "Topic :: Software Development :: Libraries",
    "Environment :: Console",
    "Intended Audience :: Developers",
]

setup(
    author="Pavel Liashkov",
    author_email="pavel.liashkov@protonmail.com",
    name="starlette-i18n",
    description="Localisation helper for starlette",
    version=str(version.VERSION),
    url="https://github.com/bigbag/starlette-i18n",
    platforms=CLASSIFIERS,
    install_requires=["starlette==0.14.1", "babel==2.9.0"],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite="",
)
