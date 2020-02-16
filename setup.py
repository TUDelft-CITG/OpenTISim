#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for OpenTISim.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 3.1.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
import sys

from pkg_resources import require, VersionConflict
from setuptools import setup, find_packages

try:
    require('setuptools>=38.3')
except VersionConflict:
    print("Error: version of setuptools is too old (<38.3)!")
    sys.exit(1)

requires = [
    "pandas>=0.24.0",
    "numpy",
    "scipy",
    "matplotlib",
    "pyproj",
    "plotly",
    "sphinx_rtd_theme",
]

setup_requirements = [
    "pytest-runner",
]

tests_require = [
    "pytest==3.10.1",
    "pytest-cov",
    "pytest-timeout",
    "pytest-datadir"
]

with open("README.md", "r") as des:
    long_description = des.read()

setup(
    author="Mark van Koningsveld",
    author_email="m.vankoningsveld@tudelft.nl",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
    ],
    description="The OpenTISim package aims to facilitate adaptive terminal planning in the light of an uncertain future.",
    entry_points={
        'console_scripts': [
            'opentisim=opentisim.cli:cli',
        ],
    },
    install_requires=requires,
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="OpenTISim",
    name="opentisim",
    packages=find_packages(include=["opentisim"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=tests_require,
    url="https://github.com/TUDelft-CITG/OpenTISim",
    version="v0.6.0",
    zip_safe=False,
)
