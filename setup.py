#!/usr/bin/env python3

import os
import setuptools

try:
    import py2exe
except:
    py2exe = None

import nightmare
import pathlib


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# Create a __main__.py to be included in the egg
main_py = """#!/usr/bin/env python3

import nightmare.__main__

if __name__ == "__main__":
    nightmare.__main__.main()
"""
main = pathlib.Path("__main__.py")
main.write_text(main_py)

setuptools.setup(
    name="nightmare",
    version=nightmare.__version__,
    description="NIGHTMARE is of Generous Help when Testing; May Arnold be Remembered Eternally",
    author="Hanno Sternberg",
    author_email="hanno@almostintelligent.de",
    url="https://github.com/hastern/nightmare",
    license=read("LICENSE"),
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    py_modules=["__main__"],
    install_requires=["pyparsing"],
    entry_points={
        'setuptools.installation': [
            'eggsecutable = nightmare.__main__:main',
        ]
    },
    extras_require = {
        'gui': ["wxpython"]
    },
    data_files=[("", ["resource/nightmare.ico"])],
)

# And delete __main__.py (We don't want this to pollute or directory)
main.unlink()
