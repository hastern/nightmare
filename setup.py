#!/usr/bin/env python

import os
from setuptools import setup
try:
	import py2exe
except:
	py2exe = None


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    
includes = ['pyTest','pyTestMain','pyTestSuite','pyTestRunner','pyTestGui','pyTestEditForm','pyTestUtils','__main__','arnold_converter']
excludes = ['pyreadline','pyreadline.console', 'pyreadline.rlmain','unittest','email', 'email.Utils','calendar','_ssl','Tkinter',"Tkconstants", "tcl"]
packages = ['pyparsing']
dll_excludes = ['w9xpopen.exe',"MSVCP90.dll"]
mainScript = 'pyTestMain'

if py2exe is not None:
	options = {"py2exe": {
		"compressed": 1, 
		"optimize": 0,
		"bundle_files": 1,
		"includes": includes,
		"excludes": excludes,
		"packages": packages,
		"dll_excludes": dll_excludes,
		"dist_dir": "dist",
		"custom_boot_script": '',
		"unbuffered": True,
		}
	}
else:
	options = {}

setup(
	name='nightmare',
	#name='pyTest',
	version='2.0',
	description='NIGHTMARE is of Generous Help when Testing; May Arnold be Remembered Eternally',
	author='Hanno Sternberg',
	author_email='hanno@almostintelligent.de',
	url='https://github.com/drakehutner/pyTest',
	py_modules=includes,
	license=read('LICENSE'),
	long_description=read('README.md'),
	entry_points={
		'setuptools.installation':[
			"eggsecutable = {}:main".format(mainScript)
		]
	},
	install_requires=['pyparsing'],
	options = options,
	console=[mainScript+'.py'],
	data_files=[('',['example/suite.py'])],
	#scripts=['pyTest.py'],
	zipfile=None,
	zip_safe=True,
)