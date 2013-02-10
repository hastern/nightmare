#!/usr/bin/env python

import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name='pyTest',
	version='1.0',
	description='A simple test programm for command line programms.',
	author='Hanno Sternberg',
	author_email='hanno@almostintelligent.de',
	url='https://github.com/drakehutner/pyTest',
	packages=find_packages(),
	py_modules=['pyTest','TestGui','__main__'],
	license=read('LICENSE'),
	long_description=read('README.md'),
	entry_points={
		'setuptools.installation':[
			"eggsecutable = pyTest:main"
		]
	}
)