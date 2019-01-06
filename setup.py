#!/usr/bin/env python3

import os
from setuptools import setup

try:
    import py2exe
except:
    py2exe = None

import nightmare


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


packages = ["pyparsing", "nightmare"]
icon_resources = [(1, "resource/nightmare.ico")]
mainScript = "__main__"


setup(
    name="nightmare",
    version=nightmare.__version__,
    description="NIGHTMARE is of Generous Help when Testing; May Arnold be Remembered Eternally",
    author="Hanno Sternberg",
    author_email="hanno@almostintelligent.de",
    url="https://github.com/hastern/nightmare",
    license=read("LICENSE"),
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    install_requires=["pyparsing"],
    extras_require = {
        'gui': ["wxpython"]
    },
    data_files=[("", ["resource/nightmare.ico"])],
)
