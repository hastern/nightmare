#!/usr/bin/env python

import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name='pyTest',
	version='1.0',
	description='A simple test programm for command line programms.',
	author='Hanno Sternberg',
	author_email='hanno@almostintelligent.de',
	url='https://github.com/drakehutner/pyTest',
	packages=['test'],
	scripts=['pyTest.py','TestGui.py','__main__.py'],
	license=read('LICENSE'),
	long_description=read('README.md'),
	ntry_points = {
        'setuptools.installation': [
            'eggsecutable = __main__:main_func',
        ]
    }
)