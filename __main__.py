#!/usr/bin/env python

import sys

from test.testSuite import TestSuite
from test.testRunner import TestRunner
from test.utils import TermColor
from TestGui import TestRunnerGui



def printHelp():
	"""Print usage information for this tool"""
	print "pyTest"
	print ""
	print "A test tool for non-interactive commandline programms"
	print ""
	print "Usage: {} [OPTIONS]".format(os.path.relpath(sys.argv[0]))
	print "  OPTIONS:"
	print "    -bench:TESTBENCH"
	print "        Load the testbench form the file TESTBENCH."
	print "    -suite:SUITE"
	print "        Use the testsuite SUITE from the testbench."
	print "    -test:TEST"
	print "        Only run test number TEST."
	print "    -dut:DUT"
	print "        Set the device under test to the file DUT."
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
	print "        Verbose mode. The program gets chatty."
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
		runner.run()
		if not runner.lengthOnly and not runner.infoOnly and runner.test == -1:
			print "{:2.2f}%".format(suite.getRate())
		sys.exit(suite._lastResult)
	else:
		gui = TestRunnerGui()
	