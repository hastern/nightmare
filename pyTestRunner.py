#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import subprocess

from threading import Thread

from pyTestUtils import TermColor, logger
from pyTest import Test, TestState
from pyTestSuite import TestSuite, TestSuiteMode
		
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
		self.runsuite = None
		self.finished = None
		self.pipe = False
		self.out = False
		self.timeout = None
		self.linesep = os.linesep
		self.classpath = "."
		
	def setDUT(self, DUT):
		"""
		set the Device under Test
		
		@type	DUT: String
		@param	DUT: Device Under Test
		"""		
		self.DUT = DUT
		if self.runsuite is not None:
			self.runsuite.setDUT(DUT)
	
	def getSuite(self):
		"""Returns the suite. If none is loaded a new one will be created"""
		if self.runsuite is None:
			self.runsuite = TestSuite(DUT = self.DUT, mode=self.mode)		
		return self.runsuite
	
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
			elif arg.startswith("--suite="):
				self.suite = arg[8:]
				logger.log("\tI'm using the testsuite '{}'".format(self.suite))
			elif arg == "--no-color":
				TermColor.active = False
			elif arg.startswith("--test="):
				self.test = int(arg[7:])
				logger.log("\tI'm only running test #{}".format(self.test))
			elif arg == "-l":
				self.lengthOnly = True
				logger.log("\tI will only print the number of tests");
			elif arg.startswith("--bench="):
				self.file = str(arg[8:])
				logger.log("\tI'm using testbench '{}'".format(self.file))
			elif arg.startswith("--timeout="):
				self.timeout = int(arg[10:])
				logger.log("\tSetting global timeout to {}".format(self.timeout))
			elif arg.startswith("--dut=") or arg.startswith("--DUT="):
				self.setDUT(arg[6:])
				logger.log("\tDevice under Test is: {}".format(self.DUT))
			elif arg.startswith("--info-only"):
				self.infoOnly = True
				self.mode = TestSuiteMode.Continuous
				logger.log("\tI will only print the test information.")
			elif arg.startswith("--crln"):
				self.linesep = "\r\n"
			elif arg.startswith("--ln"):
				self.linesep = "\n"
			elif arg.startswith("--cr"):
				self.linesep = "\r"
			elif arg == "-p":
				self.pipe = True
				logger.log("\tI will pipe all tests outputs to their respective streams")
			elif arg == "-o":
				self.out = True
				logger.log("\tI will pipe failed tests outputs to their respective streams")
				
	def addTest(self):
		test = Test(name = "New Test", description = "Add a description", DUT = self.DUT)
		test.pipe = self.pipe
		test.outputOnFail = self.out
		test.linesep = self.linesep
		self.getSuite().addTest(test) 
		return test
	
	def loadSuite(self, fname = None):
		"""Loads a python based suite from a file"""
		logger.log("\nReading testfile ...")
		if fname is not None:
			self.file = fname
		if self.file is not None and self.file != "" and os.path.exists(self.file):
			glb = {"__builtins__":__builtins__, "Test":Test, "Suite":TestSuite}
			ctx = {self.suite:None, "DUT":None}
			self.runsuite = None
			execfile(self.file, glb, ctx)
			if (self.suite in ctx):
				if (ctx[self.suite] != None):
					self.runsuite = TestSuite(ctx[self.suite], DUT=self.DUT, mode=self.mode)
					self.runsuite.setAll(infoOnly=self.infoOnly, disabled = False, pipe=self.pipe, out=self.out, timeout = self.timeout, linesep = self.linesep)
					self.testCount = len(self.runsuite.testList)
					if "DUT" in ctx and ctx['DUT'] is not None and self.DUT is None:
						self.setDUT(ctx["DUT"])
				else:
					logger.log("Sorry, but I can't find any tests inside the suite '{}'".format(self.suite))
			else:
				logger.log("Sorry, but there was no test-suite in the file")
			return self.runsuite
		
	def start(self, finished = None, test = -1):
		"""start the runner-thread"""
		self.finished = finished
		self.test = test
		Thread.start(self)
	
	def run(self, doYield = False):
		"""Thread run function"""
		if self.lengthOnly:
			print len(self.runsuite.getTests())
		else:
			logger.flush(self.quiet)
			self.runsuite.setMode(self.mode)
			if (self.test == -1):
				if doYield:
					for test in self.runsuite.runAll(self.quiet, doYield):
						yield test
					raise StopIteration()
				else:
					self.runsuite.runAll(self.quiet)
				self.runsuite.stats(self.quiet)
				logger.flush(self.quiet)
			else:
				self.runsuite.runOne(self.test)
			logger.flush(self.quiet)
		if self.finished != None:
			self.finished()
		Thread.__init__(self) # This looks like a real dirty hack :/
		
	def countTests(self):
		return len(self.runsuite.testList)
		
	def __str__(self):
		self.toString()
		
	def toString(self):
		s = self.suite + ' = ' + self.runsuite.toString()
		