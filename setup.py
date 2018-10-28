#!/usr/bin/env python3

import os
from setuptools import setup
try:
	import py2exe
except:
	py2exe = None


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

from version import *

Name = "nightmare"
Description = "NIGHTMARE is of Generous Help when Testing; May Arnold be Remembered Eternally"
Author = "Hanno Sternberg"
Mail = "hanno@almostintelligent.de"
Url = 'https://github.com/hastern/nightmare'
Company = ''
Copyright = ''



MANIFEST_TEMPLATE = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
  />
  <description>%(descr)s</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false">
        </requestedExecutionLevel>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
            type="win32"
            name="Microsoft.VC90.CRT"
            version="9.0.21022.8"
            processorArchitecture="x86"
            publicKeyToken="1fc8b3b9a1e18e3b">
      </assemblyIdentity>
    </dependentAssembly>
  </dependency>
  <dependency>
    <dependentAssembly>
         <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
  </dependency>
</assembly>
"""

includes = ['__main__','main','case','suite','runner','gui','editform','utils','arnold_converter','version', 'pyparsing']
excludes = ['pyreadline','pyreadline.console', 'pyreadline.rlmain','unittest','email', 'email.Utils','calendar','_ssl','Tkinter',"Tkconstants", "tcl"]
packages = ['pyparsing']
icon_resources = [(1,"resource/nightmare.ico")]
bitmap_resources = []
other_resources = [(24, 1, MANIFEST_TEMPLATE % dict(prog=Name, descr=Description))]
dll_excludes = ['w9xpopen.exe',"MSVCP90.dll"]
mainScript = '__main__'


if py2exe is not None:
	options = {"py2exe": {
		"compressed": 1,
		"optimize": 2,
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

GUI2Exe_Target = {
	'script': mainScript + '.py',
	'icon_resources': icon_resources,
	'bitmap_resources': bitmap_resources,
	'other_resources': other_resources,
	'dest_base': Name,
	'version': Version,
	'company_name': Company,
	'copyright': Copyright,
	'name': Name
}

setup(
	name=Name, version=Version, description=Description,
	author=Author, author_email=Mail, url=Url,
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
	#console=[mainScript+'.py'],
	#windows=[GUI2Exe_Target],
	console=[GUI2Exe_Target],
	data_files=[('',['resource/nightmare.ico'])],
	#scripts=['main.py'],
	zipfile=None,
	zip_safe=True,
)
