#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ---------- ---------- ---------- ---------- ---------- ---------- ---------- #
# @file pyTest                                                                 #
# pyTest is a tool for testing commandline applications.                       #
#                                                                              #
# It can be run from the commandline or by using the integrated graphical user #
# interface written with tkinter.                                              #
#                                                                              #
#                                                                              #
# @author Hanno Sternberg <hanno@almostintelligent.de>                         #
#                                                                              #
# This software is licensed under the MIT License                              #
#                                                                              #
# Copyright (c) 2012-2013 Hanno Sternberg                                      #
#                                                                              #
# Permission is hereby granted, free of charge, to any person obtaining a copy #
# of this software and associated documentation files (the "Software"), to     #
# deal in the Software without restriction, including without limitation the   #
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or  #
# sell copies of the Software, and to permit persons to whom the Software is   #
# furnished to do so, subject to the following conditions:                     #
#                                                                              #
# The above copyright notice and this permission notice shall be included in   #
# all copies or substantial portions of the Software.                          #
#                                                                              #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR   #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,     #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER       #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING      #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS #
# IN THE SOFTWARE.                                                             #
# ---------- ---------- ---------- ---------- ---------- ---------- ---------- #

import os
import sys

from pyTest import TestState
from pyTestSuite import TestSuite
from pyTestRunner import TestRunner
from pyTestUtils import TermColor

def printHelp():
	"""Print usage information for this tool"""
	print "pyTest"
	print ""
	print "A test tool for non-interactive commandline programms"
	print ""
	print "Usage: {} [OPTIONS]".format(os.path.relpath(sys.argv[0]))
	print "  OPTIONS:"
	print "    --bench=TESTBENCH"
	print "        Load the testbench form the file TESTBENCH."
	print "    --suite=SUITE"
	print "        Use the testsuite SUITE from the testbench."
	print "    --test=TEST"
	print "        Only run test number TEST."
	print "    --dut=DUT"
	print "        Set the device under test to the file DUT."
	print "    --timeout=SEC"
	print "        Set a global timeout for all tests."
	print "    -c"
	print "        Continuous mode (Don't halt on failed tests)."
	print "    -e"
	print "        Same as '-c', but will halt if an error occurs."
	print "    -l"
	print "        Print only the number of tests in the suite."
	print "    -p"
	print "        Redirect DUT output to their respective streams."
	print "    -o"
	print "        Redirect DUT output from failed tests to their respective streams."
	print "    --no-color"
	print "        Don't use any colored output."
	print "    --no-gui"
	print "        Don't use the GUI."
	print "    --info-only"
	print "        Display only test information, but don't run them."
	print "    -q"
	print "        Quiet mode. There will be no output except results."
	print "    -v"
	print "        Verbose mode. The program gets chatty (default)."
	print "    -h, --help, -?"
	print "        Print this help"
	exit(0)

def main():
	TermColor.init()
	if "-h" in sys.argv or "--help" in sys.argv or "-?" in sys.argv:
		printHelp()
	if "--no-gui" in sys.argv:
		# Capt. Obvious: We're running in console mode
		runner = TestRunner()
		runner.parseArgv()
		suite = runner.loadSuite()
		for testcase in runner.run():
			pass
		if not runner.lengthOnly and not runner.infoOnly and runner.test == -1:
			print "{:2.2f}%".format(suite.getRate())
		sys.exit(suite.lastResult if suite.lastResult not in [TestState.Waiting,TestState.InfoOnly] else 0)
	else:
		from pyTestGui import TestRunnerGui
		if len(sys.argv) > 1 and not sys.argv[1].startswith("-") and os.path.exists(sys.argv[1]):
			sys.argv[1] = '--bench='+sys.argv[1]
		gui = TestRunnerGui()	
		gui.buildWindow()
		gui.show()

if __name__ == "__main__":
	main()
	