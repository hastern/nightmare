#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import sys
import math
import subprocess

try:
	import pyparsing
except:
	pyparsing = None

#from threading import Thread

from pyTestUtils import TermColor, logger
from pyTest import Test, TestState
from pyTestSuite import TestSuite, TestSuiteMode
from arnold_converter import syntax, buildTestList

class TestRunner(object):
	"""Testrunner. Reads a testbench file and executes the testrun"""
	
	def __init__(self):
		"""Initialises the test runner"""
		#Thread.__init__(self)
		logger.log(
			  TermColor.colorText("NIGHTMARE I", TermColor.Red, style = TermColor.Bold) 
			+ TermColor.colorText("s of ", TermColor.White)
			+ TermColor.colorText("G", TermColor.Red, style = TermColor.Bold)
			+ TermColor.colorText("enerous ", TermColor.White)
			+ TermColor.colorText("H", TermColor.Red, style = TermColor.Bold)
			+ TermColor.colorText("elp when ", TermColor.White)
			+ TermColor.colorText("T", TermColor.Red, style = TermColor.Bold)
			+ TermColor.colorText("esting; ", TermColor.White)
			+ TermColor.colorText("M", TermColor.Red, style = TermColor.Bold)
			+ TermColor.colorText("ay ", TermColor.White)
			+ TermColor.colorText("A", TermColor.Red, style = TermColor.Bold)
			+ TermColor.colorText("rnold be ", TermColor.White)
			+ TermColor.colorText("R", TermColor.Red, style = TermColor.Bold)
			+ TermColor.colorText("emembered ", TermColor.White)
			+ TermColor.colorText("E", TermColor.Red, style = TermColor.Bold)
			+ TermColor.colorText("ternally", TermColor.White)
			)
		logger.log("Welcome to nightmare Version 2")
		self.suite = "suite"
		"""Test suite selector"""
		self.test = -1
		"""single test selector"""
		self.quiet = False
		"""Definition of the programs verbosity"""
		self.mode = None
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
		self.pipe = None
		self.out = None
		self.diff = None
		self.timeout = None
		self.linesep = os.linesep
		self.classpath = "."
		self.arnold = False
		self.relative = False
		
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
			if arg == "-c" or arg == "--continue":
				logger.log("\tI'm running in continuous mode now")
				self.mode = TestSuiteMode.Continuous
			elif arg == "-e" or arg == "--error":
				logger.log("\tI'm running in continuous mode now, but will halt if an error occurs")
				self.mode = TestSuiteMode.BreakOnError
			elif arg == "-q" or arg == "--quiet":
				self.quiet = True
			elif arg == "-v" or arg == "--verbose":
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
			elif arg == "--arnold":
				self.arnold = True
			elif arg.startswith("--crln"):
				self.linesep = "\r\n"
			elif arg.startswith("--ln"):
				self.linesep = "\n"
			elif arg.startswith("--cr"):
				self.linesep = "\r"
			elif arg == "-p" or arg == "--pipe-all":
				self.pipe = True
				logger.log("\tI will pipe all tests outputs to their respective streams")
			elif arg == "-o" or arg == "--output-fail":
				self.out = True
				logger.log("\tI will pipe failed tests outputs to their respective streams")
			elif arg == "-d" or arg == "--diff":
				self.diff = True
				logger.log("\tI will show the differences in output and expectations")
			elif arg == "-r" or arg == "--relative":
				self.relative = True
				
	def addTest(self):
		test = Test(name = "New Test", description = "Add a description", DUT = self.DUT)
		test.pipe = self.pipe
		test.outputOnFail = self.out
		test.linesep = self.linesep
		self.getSuite().addTest(test) 
		return test
	
	def loadArnold(self):
		if syntax is not None:
			logger.log("\t...using Arnold-Mode")
			syn = syntax()
			fileHnd = open(self.file)
			content = []
			for line in fileHnd:
				if not line.startswith("#") and not line.strip() == "":
					content.append(line.replace("ä","ae").replace("Ä","Ae").replace("ö","oe").replace("Ö","Oe").replace("ü","ue").replace("Ü","Ue").replace("ß","ss"))
			s = "".join(content)
			ast = syn.parseString(s)
			testList = buildTestList(ast)
			suite = TestSuite(*testList)
			suite.setDUT(self.DUT)
		else:
			logger.log("\t ... could not init arnold mode due to missing pyparsing package")
			suite = TestSuite()
		return suite
		
	def loadPython(self):
		glb = {"__builtins__":__builtins__, "parser":pyparsing, "os":os, "regex":re, "math":math, "Test":Test, "Suite":TestSuite, "Mode":TestSuiteMode, "State":TestState}
		ctx = {self.suite:None, "DUT":None}
		execfile(self.file, glb, ctx)
		if (self.suite in ctx):
			suite = None
			if (ctx[self.suite] != None):
				if ctx[self.suite].__class__ == TestSuite:
					suite = ctx[self.suite]
					suite.setDUT(self.DUT)
					if self.mode is None:
						self.mode = suite.mode
					elif suite.mode is None:
						suite.mode = self.mode
					if 'DUT' in ctx and ctx['DUT'] is not None and self.DUT is None:
						self.setDUT(ctx['DUT'])
				else:
					suite = TestSuite(*ctx[self.suite], **{'DUT':self.DUT, 'mode':self.mode})
			else:
				logger.log("Sorry, but I can't find any tests inside the suite '{}'".format(self.suite))
		else:
			logger.log("Sorry, but there was no test-suite in the file")
		return suite
	
	def loadSuite(self, fname = None):
		"""Loads a python based suite from a file"""
		if fname is not None:
			self.file = fname
		if self.file is not None and self.file != "" and os.path.exists(self.file):
			logger.log("\nReading testfile ...")
			if self.arnold:
				self.runsuite = self.loadArnold()
			else:
				self.runsuite = self.loadPython()
			self.runsuite.setAll(
				state=TestState.InfoOnly if self.infoOnly else TestState.Waiting, 
				pipe=self.pipe, 
				out=self.out, 
				diff=self.diff,
				timeout = self.timeout, 
				linesep = self.linesep
			)
			self.testCount = len(self.runsuite.testList)
			logger.log("I could load {} Testcase".format(self.testCount))
			if self.relative:
				os.chdir(os.path.dirname(os.path.abspath(self.file)))
				logger.log("Current Working Dir is: {}".format(os.getcwd()))
		else:
			logger.log("Sorry, but I couldn't find the file '{}'".format(self.file))
		logger.flush(self.quiet)
		return self.runsuite
		
	#def start(self, finished = None, test = -1):
	#	"""start the runner-thread"""
	#	self.finished = finished
	#	self.test = test
	#	Thread.start(self)
	
	def run(self):
		"""Thread run function"""
		if self.lengthOnly:
			print len(self.runsuite.getTests())
		else:
			logger.flush(self.quiet)
			self.runsuite.setMode(self.mode)
			if (self.test == -1):
				for test in self.runsuite.runAll(self.quiet):
					yield test
				self.runsuite.stats(self.quiet)
				logger.flush(self.quiet)
			else:
				self.runsuite.runOne(self.test)
				logger.flush(self.quiet)
		if self.finished != None:
			self.finished()
		#Thread.__init__(self) # This looks like a real dirty hack :/
		raise StopIteration()
		
	def countTests(self):
		return len(self.runsuite.testList)
		
	def __str__(self):
		self.toString()
		
	def toString(self):
		s = self.suite + ' = ' + self.runsuite.toString()
		