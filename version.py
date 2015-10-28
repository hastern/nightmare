#!/usr/bin/env python
# -*- coding:utf-8 -*-

Version = "2.0"
Build = 16

if __name__ == "__main__":
	content = open("version.py", "r").read()
	content = content.replace("Build = {}".format(Build), "Build = {}".format(Build+1))
	print "Version", Version, "Build", Build+1
	open("version.py","w").write(content)
