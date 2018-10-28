#!/usr/bin/env python3
# -*- coding:utf-8 -*-

Major = 3
Minor = 0
Build = 0
Version = f"{Major}.{Minor}.{Build}"

if __name__ == "__main__":
    import sys

    content = open("version.py", "r").read()
    if "major" in sys.argv:
        content = content.replace(f"Major = {Major}", f"Major = {Major + 1}")
        Major += 1
    if "minor" in sys.argv:
        content = content.replace(f"Minor = {Minor}", f"Minor = {Minor + 1}")
        Minor += 1
    if "build" in sys.argv:
        content = content.replace(f"Build = {Build}", f"Build = {Build + 1}")
        Build += 1
    print("Version", Version)
    open("version.py", "w").write(content)
