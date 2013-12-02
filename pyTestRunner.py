#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import sys
import math
import argparse
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
		self.options = dict()
		self.testCount= 0
		self.runsuite = None
		self.finished = None
		
	def setDUT(self, DUT):
		"""
		set the Device under Test
		
		@type	DUT: String
		@param	DUT: Device Under Test
		"""		
		self.options['dut'] = DUT
		if self.runsuite is not None:
			self.runsuite.setDUT(DUT)
	
	def getSuite(self):
		"""Returns the suite. If none is loaded a new one will be created"""
		if self.runsuite is None:
			self.runsuite = TestSuite(DUT = self.options['dut'], mode=self.options['mode'])		
		return self.runsuite
	
	def parseArgv(self):
		"""Parses the argument vector"""
		args = argparse.ArgumentParser(description="A test tool for non-interactive commandline programms")
		args.add_argument("--bench", action="store", nargs=1, help="File which contains the testbench.")
		args.add_argument("--suite", action="store", nargs=1, help="Use testsuite SUITE from the testbench.", metavar="SUITE")
		args.add_argument("--dut", "--DUT", action="store", nargs=1, help="Set the device under test.")
		args.add_argument("--test", action="store", nargs="+", type=int, help="Run only the specified tests")
		args.add_argument("--timeout", action="store", nargs=1, type=float, help="Set a global timeout for all tests.")
		args.add_argument("--continue", "-c", action="store_const", default=TestSuiteMode.BreakOnFail, const=TestSuiteMode.Continuous, dest="mode", help="Continuous mode (Don't halt on failed tests).")
		args.add_argument("--error", "-e", action="store_const", const=TestSuiteMode.BreakOnError, dest="mode", help="Same as '-c', but will halt if an error occurs.")
		args.add_argument("--quiet", "-q", action="store_const", const=True, default=False, dest="quiet", help="Quiet mode. There will be no output except results.")
		args.add_argument("--verbose", "-v", action="store_const", const=False, dest="quiet", help="Verbose mode. The program gets chatty (default).")
		args.add_argument("--length", "-l", action="store_true", default=False, dest="length", help="Print only the number of tests in the suite.")
		args.add_argument("--info-only", "-i", action="store_true", default=False, dest="info", help="Display only test information, but don't run them.")
		args.add_argument("--pipe-streams", "-p", action="store_true", dest="pipe", help="Redirect DUT output to their respective streams.")
		args.add_argument("--output-fails", "-o", action="store_true", dest="output", help="Redirect DUT output from failed tests to their respective streams.")
		args.add_argument("--diff-fails", "-d", action="store_true", dest="diff", help="Display the differences between output and expectation.")
		args.add_argument("--relative", "-r", action="store_true", default=False, dest="relative", help="Use a path relative to the testbench path.")
		args.add_argument("--arnold", "-a", action="store_true", default=False, dest="arnold", help="Use the arnold mode (requires pyparsing module)")
		args.add_argument("--no-color", action="store_false", default=True, dest="color", help="Don't use any colored output.")
		args.add_argument("--no-gui", action="store_true", default=False, dest="gui", help="Don't use the GUI.")
		args.add_argument("--cr", action="store_const", const="\r", dest="linesep", help="Force the line separation character (Mac OS).")
		args.add_argument("--ln", action="store_const", const="\n", dest="linesep", help="Force the line separation character (Unix / Mac OS-X).")
		args.add_argument("--crln", action="store_const", const="\r\n", dest="linesep", help="Force the line separation character (Windows).")
		args.set_defaults(linesep=os.linesep, bench=[""], suite=["suite"], dut=[""], test=[])
		
		self.options.update(vars(args.parse_args()))
		self.options['bench'] = self.options['bench'][0]
		self.options['suite'] = self.options['suite'][0]
		self.options['dut'] = self.options['dut'][0]
		self.options['timeout'] = self.options['timeout'][0]
		
		logMessages= [
			('mode', lambda v: "I'm running in continuous mode now" 
				if v == TestSuiteMode.Continuous 
				else "I'm running in continuous mode now, but will halt if an error occurs" 
				if v == TestSuiteMode.BreakOnError 
				else "I will halt on first fail."),
			('suite', lambda v: "I'm using the testsuite '{}'".format(v)),
			('test', lambda v: "I'm only running test {}".format(v) if v >= 0 else ""),
			('bench', lambda v: "I'm using testbench '{}'".format(v)),
			('timeout', lambda v: "Setting global timeout to {}".format(v)),
			('dut', lambda v: "Device under Test is: {}".format(v)),
			('length', lambda v: "I will only print the number of tests" if v else ""),
			('info', lambda v: "I will only print the test information." if v else ""),
			('pipe', lambda v: "I will pipe all tests outputs to their respective streams" if v else ""),
			('output', lambda v: "I will pipe failed tests outputs to their respective streams" if v else ""),
			('diff', lambda v: "I will show the differences in output and expectations" if v else ""),
		]
		for option,msgFunc in logMessages:
			if self.options[option] is not None:
				msg = msgFunc(self.options[option])
				if len(msg) > 0:
					logger.log("\t{}".format(msg))
		logger.flush(self.options['quiet'])
		
				
	def addTest(self):
		test = Test(name = "New Test", description = "Add a description", DUT = self.options['dut'])
		test.pipe = self.options['pipe']
		test.outputOnFail = self.options['output']
		test.linesep = self.options['linesep']
		self.getSuite().addTest(test) 
		return test
	
	def loadArnold(self):
		if syntax is not None:
			logger.log("\t...using Arnold-Mode")
			syn = syntax()
			fileHnd = open(self.options['bench'])
			content = []
			for line in fileHnd:
				if not line.startswith("#") and not line.strip() == "":
					content.append(line.replace("ä","ae").replace("Ä","Ae").replace("ö","oe").replace("Ö","Oe").replace("ü","ue").replace("Ü","Ue").replace("ß","ss"))
			s = "".join(content)
			ast = syn.parseString(s)
			testList = buildTestList(ast)
			suite = TestSuite(*testList)
			suite.setDUT(self.options['dut'])
		else:
			logger.log("\t ... could not init arnold mode due to missing pyparsing package")
			suite = None
		return suite
		
	def loadPython(self):
		glb = {"__builtins__":__builtins__, "parser":pyparsing, "os":os, "regex":re, "math":math, "Test":Test, "Suite":TestSuite, "Mode":TestSuiteMode, "State":TestState}
		ctx = {self.options['suite']:None, "DUT":None}
		execfile(self.options['bench'], glb, ctx)
		if (self.options['suite'] in ctx):
			suite = None
			if (ctx[self.options['suite']] != None):
				if ctx[self.options['suite']].__class__ == TestSuite:
					suite = ctx[self.options['suite']]
					suite.setDUT(self.options['dut'])
					if self.options['mode'] is None:
						self.options['mode'] = suite.mode
					elif suite.mode is None:
						suite.mode = self.options['mode']
					if 'DUT' in ctx and ctx['DUT'] is not None and self.options['dut'] is None:
						self.setDUT(ctx['DUT'])
				else:
					suite = TestSuite(*ctx[self.options['suite']], **{'DUT':self.options['dut'], 'mode':self.options['mode']})
			else:
				logger.log("Sorry, but I can't find any tests inside the suite '{}'".format(self.options['suite']))
		else:
			logger.log("Sorry, but there was no test-suite in the file")
		return suite
	
	def loadSuite(self, fname = None):
		"""Loads a python based suite from a file"""
		if fname is not None:
			self.options['bench'] = fname
		if self.options['bench'] is not None and self.options['bench'] != "" and os.path.exists(self.options['bench']):
			logger.log("\nReading testfile ...")
			if self.options['arnold']:
				self.runsuite = self.loadArnold()
			else:
				self.runsuite = self.loadPython()
			if self.runsuite is not None:
				self.runsuite.setAll(
					state=TestState.InfoOnly if self.options['info'] else TestState.Waiting, 
					pipe=self.options['pipe'], 
					out=self.options['output'], 
					diff=self.options['diff'],
					timeout = self.options['timeout'], 
					linesep = self.options['linesep']
				)
				self.testCount= len(self.runsuite.testList)
				logger.log("I could load {} Testcase".format(self.testCount))
				if self.options['relative']:
					os.chdir(os.path.dirname(os.path.abspath(self.options['bench'])))
					logger.log("Current Working Dir is: {}".format(os.getcwd()))
				
			else:
				logger.log("Sorry, but I failed to load the requested suite")
		else:
			logger.log("Sorry, but I couldn't find the file '{}'".format(self.options['bench']))
		logger.flush(self.options['quiet'])
		return self.runsuite
		
	#def start(self, finished = None, test = -1):
	#	"""start the runner-thread"""
	#	self.finished = finished
	#	self.options['test'] = test
	#	Thread.start(self)
	
	def run(self):
		"""Thread run function"""
		if self.options['length']:
			print len(self.runsuite.getTests())
		else:
			logger.flush(self.options['quiet'])
			self.runsuite.setMode(self.options['mode'])
			for test in self.runsuite.run(self.options['quiet'], tests=self.options['test']):
				yield test
			self.runsuite.stats(self.options['quiet'])
			logger.flush(self.options['quiet'])
		if self.finished != None:
			self.finished()
		#Thread.__init__(self) # This looks like a real dirty hack :/
		raise StopIteration()
		
	def countTests(self):
		return len(self.runsuite.testList)
		
	def __str__(self):
		self.toString()
		
	def toString(self):
		s = self.options['suite'] + ' = ' + self.runsuite.toString()
		