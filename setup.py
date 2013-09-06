#!/usr/bin/env python

import os
from setuptools import setup
import py2exe


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name='pyTest',
	version='2.0',
	description='pyTest - A simple test tool for command line programms',
	author='Hanno Sternberg',
	author_email='hanno@almostintelligent.de',
	url='https://github.com/drakehutner/pyTest',
	packages=['pyTestCore','pyTestGui'],
	py_modules=['pyTest','__main__'],
	license=read('LICENSE'),
	long_description=read('README.md'),
	entry_points={
		'setuptools.installation':[
			"eggsecutable = pyTest:main"
		]
	},
	options = {"py2exe": {
			"compressed": 1, 
			"optimize": 0,
			"bundle_files": 1,
			"includes": ['pyTestCore','pyTestGui','pyTest','__main__'],
			"excludes": ['pyreadline','pyreadline.console', 'pyreadline.rlmain','unittest','email', 'email.Utils','_ssl'],
			"packages": [],
			"dll_excludes": ['w9xpopen.exe',"MSVCP90.dll"],
			"dist_dir": "dist",
			"custom_boot_script": '',
			"unbuffered": True,
			}
		},
	console=['pyTest.py'],
	zipfile = None,
	zip_safe=True,
)