#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='pytoml',
    version='0.1.16',

    description='A parser for TOML-0.4.0',
    author='Martin Vejnár',
    author_email='avakar@ratatanek.cz',
    url='https://github.com/avakar/pytoml',
    license='MIT',
    packages=['pytoml'],
    classifiers=[
        # Supported python versions
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

        # License
        'License :: OSI Approved :: MIT License',

        # Topics
        'Topic :: Software Development :: Libraries',
    ]
)
