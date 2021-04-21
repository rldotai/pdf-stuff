#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Some PDF utility scripts, for comparing PDFs, extracting glyphs, etc.
"""
from __future__ import unicode_literals

# To use a consistent encoding
import codecs
from setuptools import setup, find_packages
import sys, os.path


def parse_reqs(req_path="./requirements.txt"):
    """Recursively parse requirements from nested pip files."""
    install_requires = []
    with codecs.open(req_path, "r") as handle:
        # remove comments and empty lines
        lines = (
            line.strip() for line in handle if line.strip() and not line.startswith("#")
        )
        for line in lines:
            # check for nested requirements files
            if line.startswith("-r"):
                # recursively call this function
                install_requires += parse_reqs(req_path=line[3:])
            else:
                # add the line as a new requirement
                install_requires.append(line)
    return install_requires


setup(
    name="pdf_stuff",
    version="0.0.1",
    url="https://github.com/rldotai/pdf-stuff",
    license="BSD",
    author="rldotai",
    author_email="rldotai@users.noreply.github.com",
    description="Scripts and such for working with PDFs.",
    long_description=__doc__,
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    install_requires=parse_reqs(),
    entry_points={
        "console_scripts": [
            "pdfdiff.py = pdf_stuff.pdfdiff:main",
            "pdf2text.py = pdf_stuff.pdf2text:main",
            "pdfmeta.py = pdf_stuff.pdfmeta:main",
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
