#!/usr/bin/env python
# Example Device Under Test

import sys

if __name__ == "__main__":
	argv = sys.argv
	argv.pop(0)
	if 'sleep' in argv:
		while True:
			i = 0
	for arg in argv:
		print arg
	exit(0)