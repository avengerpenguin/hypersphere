#!/usr/bin/env python

import os
from setuptools import setup

setup(
    name="hypersphere",
    version="0.0.0",
    author='Ross Fenning',
    author_email='github@rossfenning.co.uk',
    description='Hypersphere',
    url='http://github.com/avengerpenguin/hypersphere',
    install_requires=[
        'rdflib',
        ],
    packages=['hypersphere'],
)
