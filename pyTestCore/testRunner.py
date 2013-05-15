#!/usr/bin/env python

import sys
import os
import subprocess

from threading import Thread

from utils import TermColor, logger
from testState import TestState
from testMode import TestSuiteMode
from test import Test
from testSuite import TestSuite
		
class TestRunner(Thread):
	"""Testrunner. Reads a testbench file and executes the testrun"""
	
	def __init__(self):
		"""Initialises the test runner"""
		Thread.__init__(self)
		logger.log("Welcome to pyTest Version 2")
		self.suite = "suite"
		"""Test suite selector"""
		self.test = -1
		"""single test selector"""
		self.quiet = False
		"""Definition of the programs verbosity"""
		self.mode = TestSuiteMode.BreakOnFail
		"""Mode for the test suite"""
		self.file = ""
		"""test bench file"""
		self.lengthOnly = False
		"""print only number of test"""
		self.infoOnly = False
		"""Print only the test information"""
		self.DUT = None
		self.testCount = 0
		self._runsuite = None
		self._finished = None
		self._pipe = False
		self._out = False
		self._timeout = None
		self._linesep = os.linesep
		self._classpath = "."
		
	def setDUT(self, DUT):
		"""
		set the Device under Test
		
		@type	DUT: String
		@param	DUT: Device Under Test
		"""		
		self.DUT = DUT
		if self._runsuite is not None:
			self._runsuite.setDUT(DUT)
	
	def getSuite(self):
		"""Returns the suite. If none is loaded a new one will be created"""
		if self._runsuite is None:
			self._runsuite = TestSuite(DUT = self.DUT, mode=self.mode)		
		return self._runsuite
	
	def parseArgv(self):
		"""Parses the argument vector"""
		argv = sys.argv
		for arg in argv:
			if arg == "-c":
				logger.log("\tI'm running in continuous mode now")
				self.mode = TestSuiteMode.Continuous
			elif arg == "-e":
				logger.log("\tI'm running in continuous mode now, but will halt if an error occurs")
				self.mode = TestSuiteMode.BreakOnError
			elif arg == "-q":
				self.quiet = True
			elif arg == "-v":
				self.quiet = False
			elif arg.startswith("-suite:"):
				self.suite = arg[7:]
				logger.log("\tI'm using the testsuite '{}'".format(suite))
			elif arg == "--no-color":
				TermColor.active = False
			elif arg.startswith("-test:"):
				self.test = int(arg[6:])
				logger.log("\tI'm only running test #{}".format(self.test))
			elif arg == "-l":
				self.lengthOnly = True
				logger.log("\tI will only print the number of tests");
			elif arg.startswith("-bench:"):
				self.file = str(arg[7:])
				logger.log("\tI'm using testbench '{}'".format(self.file))
			elif arg.startswith("-timeout:"):
				self._timeout = int(arg[9:])
				logger.log("\tSetting global timeout to {}".format(self._timeout))
			elif arg.startswith("-dut:") or arg.startswith("-DUT:"):
				self.setDUT(arg[5:])
				logger.log("\tDevice under Test is: {}".format(self.DUT))
			elif arg.startswith("--info-only"):
				self.infoOnly = True
				self.mode = TestSuiteMode.Continuous
				logger.log("\tI will only print the test information.")
			elif arg.startswith("--crln"):
				self._linesep = "\r\n"
			elif arg.startswith("--ln"):
				self._linesep = "\n"
			elif arg.startswith("--cr"):
				self._linesep = "\r"
			elif arg == "-p":
				self._pipe = True
				logger.log("\tI will pipe all tests outputs to their respective streams")
			elif arg == "-o":
				self._out = True
				logger.log("\tI will pipe failed tests outputs to their respective streams")
	
	def loadJUnitSuite(self):
		logger.log("\nReading JUnit file using wrapper ...")
		testList = []
		cmdStr = "java -ea -cp {} PyTestJUnitWrapper".format(self._classpath)
		cmd = cmdStr.split(" ")
		tests,err = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
		testCases = tests.strip().split(self._linesep)
		self._runsuite = TestSuite(mode= self.mode)
		logger.log("\tI found {} JUnit tests".format(len(testCases)))
		i = 0
		for t in testCases:
			self._runsuite.addTest(Test(name="{}".format(t), command="{} {}".format(cmdStr, i), DUT="", returnCode=0))
			self._runsuite.setAll(infoOnly=self.infoOnly, disabled = False, pipe=self._pipe, out=self._out, timeout = self._timeout, linesep = self._linesep)
			self.testCount = len(self._runsuite._testList)
			i += 1
		return self._runsuite
	
	def loadPythonSuite(self):
		"""Loads a python based suite from a file"""
		logger.log("\nReading testfile ...")
		glb = {"__builtins__":None, "Test":Test, "Suite":TestSuite}
		ctx = {self.suite:None, "DUT":None}
		self._runsuite = None
		execfile(self.file, glb, ctx)
		if (self.suite in ctx):
			if (ctx[self.suite] != None):
				self._runsuite = TestSuite(ctx[self.suite], DUT=self.DUT, mode=self.mode)
				self._runsuite.setAll(infoOnly=self.infoOnly, disabled = False, pipe=self._pipe, out=self._out, timeout = self._timeout, linesep = self._linesep)
				self.testCount = len(self._runsuite._testList)
				if "DUT" in ctx and ctx['DUT'] is not None and self.DUT is None:
					self.setDUT(ctx["DUT"])
			else:
				logger.log("Sorry, but I can't find any tests inside the suite '{}'".format(self.suite))
		else:
			logger.log("Sorry, but there was no test-suite in the file")
		return self._runsuite
		
	def loadSuite(self):
		"""Loads a testsuite from a file"""
		if self.file is not None and self.file.endswith(".py"):
			return self.loadPythonSuite()
		elif self.file is not None and self.file.startswith("java:"):
			self._classpath = self.file[5:]
			return self.loadJUnitSuite()
		elif self.DUT is not None and self.DUT.startswith("java:"):
			self._classpath = self.DUT[5:]
			return self.loadJUnitSuite()
		
	def start(self, finished = None, test = -1):
		"""start the runner-thread"""
		self._finished = finished
		self.test = test
		Thread.start(self)
	
	def run(self):
		"""Thread run function"""
		if self.lengthOnly:
			print len(self._runsuite.getTests())
		else:
			logger.flush(self.quiet)
			self._runsuite.setMode(self.mode)
			if (self.test == -1):
				self._runsuite.runAll(self.quiet)
				self._runsuite.stats(self.quiet)
				logger.flush(self.quiet)
			else:
				self._runsuite.runOne(self.test)
			logger.flush(self.quiet)
		if self._finished != None:
			self._finished()
		Thread.__init__(self) # This looks like a real dirty hack :/
		
	def countTests(self):
		return len(self._runsuite._testList)
		