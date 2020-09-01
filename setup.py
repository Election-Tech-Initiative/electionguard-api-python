#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

from glob import glob
from os.path import basename, splitext, abspath, dirname, join

from setuptools import find_packages
from setuptools import setup

current_directory = abspath(dirname(__file__))
with open(join(current_directory, "README.md"), encoding="utf-8") as readme_file:
    LONG_DESCRIPTION = readme_file.read()

NAME = "electionguard-web-api"
VERSION = "0.1.0"
LICENSE = "MIT"
DESCRIPTION = "ElectionGuard Web Api: Support for e2e verified elections."
LONG_DESCRIPTION_CONTENT_TYPE = "text/markdown"
AUTHOR = "Microsoft Corporation"
AUTHOR_EMAIL = "electionguard@microsoft.com"
URL = "https://github.com/microsoft/electionguard-web-api"
PROJECT_URLS = {
    "Documentation": "https://microsoft.github.io/electionguard-web-api",
    "Read the Docs": "https://electionguard-web-api.readthedocs.io",
    "Releases": "https://github.com/microsoft/electionguard-web-api/releases",
    "Milestones": "https://github.com/microsoft/electionguard-web-api/milestones",
    "Issue Tracker": "https://github.com/microsoft/electionguard-web-api/issues",
}


setup(
    name=NAME,
    version=VERSION,
    license=LICENSE,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    project_urls=PROJECT_URLS,
    python_requires="~=3.8",
    install_requires=["fastapi", "uvicorn"],
)
