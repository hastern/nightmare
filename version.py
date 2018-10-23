#!/usr/bin/env python
# -*- coding:utf-8 -*-

Major = 3
Minor = 0
Build = 0
Version = "{}.{}.{}".format(Major, Minor, Build)

if __name__ == "__main__":
    import sys
    content = open("version.py", "r").read()
    if "major" in sys.argv:
        content = content.replace("Major = {}".format(Major), "Major = {}".format(Major + 1))
        Major += 1
    if "minor" in sys.argv:
        content = content.replace("Minor = {}".format(Minor), "Minor = {}".format(Minor + 1))
        Minor += 1
    if "build" in sys.argv:
        content = content.replace("Build = {}".format(Build), "Build = {}".format(Build + 1))
        Build += 1
    print("Version", Version)
    open("version.py", "w").write(content)
