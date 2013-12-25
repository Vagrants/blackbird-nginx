#!/usr/bin/env python
# -*- codig: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='blackbird-nginx',
    version='0.1.1',
    description=(
        'get nginx stats by using stub_status.'
    ),
    author='makocchi',
    author_email='makocchi@gmail.com',
    url='https://github.com/Vagrants/blackbird-nginx',
)
