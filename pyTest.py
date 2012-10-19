#!/usr/bin/env python

# ---------- ---------- ---------- ---------- ---------- ---------- ---------- #
#@file pyTest                                                                  #
# pyTest is a tool for testing commandline applications.                       #
#                                                                              #
#                                                                              #
#@author Hanno Sternberg <hanno@almostintelligent.de>                          #
#@date 18.10.2012                                                              #
# ---------- ---------- ---------- ---------- ---------- ---------- ---------- #


import sys
import os
import re
import time
import subprocess
try:
	import colorama
except:
	colorama = None



__package__ = "pyTest"

class TermColor:
	""" Print colored text """
	Black = 0
	"""Black color code"""
	Red = 1
	"""Red color code"""
	Green = 2
	"""Green color code"""
	Yellow = 3
	"""Yellow color code"""
	Blue = 4
	"""Blue color code"""
	Purple = 5
	"""Purple color code"""
	Cyan = 6
	"""Cyan color code"""
	White = 7
	"""White color code"""
	Normal = 0
	"""Normal text style"""
	Bold = 1
	"""Bold text style"""
	Dim = 2
	"""Dim text style"""
	Background = 40
	"""Change background color"""
	Text = 30
	"""Change text color"""
	
	active = True
	"""activate colorfull output"""
	
	
	@staticmethod
	def colorText(text, color = 7, where = 30, style = 0):
		if TermColor.active and ((colorama is not None) or (os.getenv('ANSI_COLORS_DISABLED') is not None)):
			colStr = str(where + color)
			styleStr = "{:02}".format(style)
			return "\033[{};{}m{}".format(styleStr, colStr, text)
		else:
			return text
			
	@staticmethod
	def init():
		if colorama is not None:
			colorama.init(autoreset=True)
		
		
def isLambda(v):
	""" 
	Test if a given value is a lambda function
	
	@type		v: Anything (preferable a lambda function)
	@param		v: Some value
	@rtype: 	Boolean
	@return:	True, if the value is a lambda function
	"""
	return isinstance(v, type(lambda: None)) and v.__name__ == '<lambda>'

class logger:
	"""Logger class"""
	_buffer = []
	"""Message buffer"""
	@staticmethod
	def log(str):
		"""
		Writes a log message to the buffer
		
		@type	str: String
		@param	str: Log message
		"""
		msg = "[{0}] {1}".format(time.strftime("%H:%M:%S") , str.strip("\r\n") )
		logger._buffer.append(msg)
		
	@staticmethod
	def flush(quiet = False):
		"""
		flushes the message buffer
		
		@type	quiet: Boolean
		@param	quiet: Flag if the buffer should be printed or not
		"""
		if not quiet:
			for b in logger._buffer:
				print b
			sys.stdout.flush()
		logger.clear()
	
	@staticmethod
	def clear():
		"""
		Clears the buffer
		"""
		logger._buffer = []

  
class TestState:
	"""Enumeration of test states"""
	Waiting = 0
	"""The test ist waiting for execution"""
	Success = 1
	"""The test was successful"""
	Fail = 2
	"""The test has failed"""
	Error = 3
	"""The test has producsed an error"""
	
	@staticmethod
	def toString(state):
		"""
		Converts the enumeration value into a string
		
		@type	state: int
		@param	state: Enumeration value
		"""
		if state == TestState.Waiting:
			return TermColor.colorText("WAITING", TermColor.White)
		if state == TestState.Success:
			return TermColor.colorText("SUCCESS", TermColor.Green, TermColor.Background)
		if state == TestState.Fail:
			return TermColor.colorText("FAIL", TermColor.Red, TermColor.Background)
		if state == TestState.Error:
			return TermColor.colorText("ERROR", TermColor.Red)
		return TermColor.colorText("UNKNOWN", TermColor.Yellow)
	
class TestSuiteMode:
	"""Enumeration for testsuite modes """
	Continuous = 0
	"""Run all test"""
	BreakOnFail = 1
	"""Halt on first failed test"""
	BreakOnError = 2
	"""Halt only on errors"""
	
	@staticmethod
	def toString(mode):
		"""
		Converts the enumeration value into a string
		
		@type	mode: int
		@param	mode: Enumeration value
		"""
		if mode == TestSuiteMode.BreakOnFail:
			return "Break On Fail"
		if mode == TestSuiteMode.Continuous:
			return "Continuous"
		if mode == TestSuiteMode.BreakOnError:
			return "Break on Error"
		return "Unknown mode"

class Test:
	"""A single test"""
	_name = ""
	"""The name of the test"""
	_descr = ""
	"""The description of the game"""
	_cmd = None
	"""The command to be executed"""
	_expectOutput = ""
	"""The expected output"""
	_expectRetCode = 0
	"""The expected return code"""
	_output = ""
	"""The output"""
	_retCode = 0
	"""The return code"""
	_state = TestState.Waiting
	"""The state of the game"""
	
	def __init__(self, data):
		"""
		Initalises a test
		
		@type	data: Dictionary
		@param	data: Dictionary with test definitions
		"""
		if 'name' in data:
			self._name = data['name']
		if 'descr' in data:
			self._descr = data['descr']
		if "cmd" in data:
			self._cmd = data['cmd']
		else:
			self._state = TestState.Error
		if 'expect' in data:
			self._expectOutput = data['expect']
		else:
			self._expectOutput = ""
		if 'returnCode' in data:
			self._expectRetCode = data['returnCode']
		else:
			self._expectRetCode = 0
			
	def getName(self):
		"""Returns the name of the test"""
		return self._name
		
	def getDescription(self):
		"""Returns the description of the test"""
		return self._descr
		
	def getCommand(self):
		"""Returns the command of the test"""
		return self._cmd
		
	def getState(self):
		"""Returns the current test state"""
		return self._state
		
	def getOutput(self):
		"""Returns the output"""
		return self._output
		
	def getExpect(self):
		"""Returns the expected output"""
		return self._expectOutput
		
	def _check(self, exp, out):
		"""
		Test an expectation against an output
		If it's a lambda function, it will be executed with the output
		If it's a string, it will be treated as a regular expression.
		If it's an integer, it gets compared with the output
		@type	exp: String, Int, lambda 
		@param	exp: Expected result
		@type 	out: String, Int
		@param	out: output The output
		@rtype:	Boolean
		@return: Result of the comparison
		"""
		if (isLambda(exp)):
			return exp(out)
		elif (isinstance(exp, int) and isinstance(out, int)):
			return exp == out
		elif isinstance(exp, str):
			patCode = re.compile(exp, re.IGNORECASE)
			return (patCode.match(str(out)) != None)
		return False
	
	def run(self):
		"""Runs the test"""
		if self._cmd != None:
			try:
				self._output = subprocess.check_output(self._cmd, stderr=subprocess.STDOUT, shell=True)
				self._retCode = 0
			except subprocess.CalledProcessError as e:
				self._output = e.output
				self._retCode = e.returncode
			if self._check(self._expectRetCode, self._retCode) and self._check(self._expectOutput,self._output):
				self._state = TestState.Success
			else:
				self._state = TestState.Fail
		else:
			self._state = TestState.Error
		return self._state

class TestSuite:
	"""A testsuite is a collection of tests"""
	_success = 0
	"""The number of successful tests"""
	_failed = 0
	"""The number of failed tests"""
	_count = 0
	"""A counter for the executed tests"""
	_error = 0
	"""The number of errors occured during the testrun"""
	_lastResult = TestState.Waiting
	"""The result of the last test"""
	_rate = 0
	"""The successrate of the testrun"""
	_len = 0
	"""The total number of tests in the suite"""
	
	_testList = []
	"""The collection of tests"""
	_mode = TestSuiteMode.BreakOnFail
	"""The test suite mode"""
	
	def __init__(self, tests = [], mode=TestSuiteMode.BreakOnFail):
		"""
		Initialises a test suite
		
		@type	tests: List
		@param	tests: List of tests, default is an empty list
		
		@type	mode: TestSuiteMode
		@param	mode: The initial mode of the testsuite
		"""
		self.setMode(mode)
		for t in tests:
			self.addTest(t)
		self._len = len(self._testList)
	
	def setMode(self, mode):
		"""
		Sets the mode of the testsuite
		
		@type	mode: TestSuiteMode
		@param	mode: New mode
		"""
		self._mode = mode
		
	def addTest(self, data):
		"""
		Adds a test to the suite
		
		@type	data: Test
		@param	data: Test to add
		"""
		self._testList.append(Test(data))
		
	def runOne(self, n):
		"""
		Run one single test
		
		@type	n: int
		@param	n: Number of the test
		"""
		if (n < self._len):
			result = self._testList[n].run()
			print TestState.toString(result)
			return result
		logger.log("\tSorry but there is no test #{}".format(n))
		print TestState.toString(TestState.Error)
		return TestState.Error
		
	def runAll(self, quiet = False):
		"""
		Runs the whole suite of tests
		
		@type	quiet: Boolean
		@param	quiet: Flag, passed along to the logger
		"""
		self._success = 0
		self._failed = 0
		self._count = 0
		self._error = 0
		self._lastResult = TestState.Waiting
		for t in self._testList:
			self._count = self._count + 1 
			self._lastResult = t.run()
			logger.log("Test[{:02}] {} - {}: {}".format(self._count, t.getName(), t.getDescription(), TestState.toString(t.getState())))
			logger.flush(quiet)
			if (self._lastResult == TestState.Success):
				self._success = self._success + 1
			elif (self._lastResult == TestState.Fail):
				self._failed = self._failed + 1
			elif (self._lastResult == TestState.Error):
				self._error = self._error + 1
			if (self._mode == TestSuiteMode.BreakOnFail) and (self._lastResult != TestState.Success):
				break
			if (self._mode == TestSuiteMode.BreakOnError) and (self._lastResult == TestState.Error):
				break

	def stats(self, quiet = False):
		"""
		Generate and write the stats
		
		@type	quiet: Boolean
		@param	quiet: Flag, passed along to the logger
		"""
		logger.log("I ran {} out of {} tests in total".format(self._count, len(self._testList)))
		logger.log(TermColor.colorText("\tSuccess: {}".format(self._success), TermColor.Green))
		if (self._failed > 0):
			logger.log(TermColor.colorText("\tFailed: {}".format(self._failed), TermColor.Red))
		if (self._error > 0):
			logger.log(TermColor.colorText("\tErrors: {}".format(self._error), TermColor.Yellow))
		if (self._error == 0) and (self._failed == 0):
			logger.log("\tCongratulations, you passed all tests!")
		self._rate = float(self._success) / float(self._len) * 100
		return self._rate
		
class TestRunner:
	"""Testrunner. Reads a testbench file and executes the testrun"""

	def __init__(self):
		"""Initialises the test runner"""
		logger.log("Welcome to pyTest Version 1")
		argv = sys.argv
		argv.pop(0)
		mode = TestSuiteMode.BreakOnFail
		suite = 'suite'
		test = -1
		quiet = False
		for arg in argv:
			if (arg == "-c"):
				logger.log("\tI'm running in continuous mode now")
				mode = TestSuiteMode.Continuous
			elif (arg == "-e"):
				logger.log("\tI'm running in continuous mode now, but will halt if an error occurs")
				mode = TestSuiteMode.BreakOnError
			elif (arg == "-q"):
				quiet = True
			elif (arg == "-v"):
				quiet = False
			elif (arg.startswith("-s")):
				suite = arg[2:]
				logger.log("\tI'm using the testsuite '{}'".format(suite))
			elif (arg == "--no-color"):
				TermColor.active = False
			elif (arg.startswith("-t")):
				test = int(arg[2:])
				logger.log("\tI'm only running test #{}".format(test))
			else:
				f = arg
				logger.log("\tI'm using testbench '{}'".format(f))
		
		logger.log("\nReading testfile ...")
		logger.flush(quiet)
		glb = {"__builtins__":None}
		ctx = {suite:None}
		execfile(f, glb, ctx)
		if (suite in ctx):
			if (ctx[suite] != None):
				testsuite = TestSuite(ctx[suite], mode)
				if (test == -1):
					testsuite.runAll(quiet)
					rate = testsuite.stats(quiet)
					logger.flush(quiet)
					print "{:2.2f}%".format(rate)
				else:
					testsuite.runOne(test)
			else:
				logger.log("Sorry, but I can't find any tests inside the suite '{}'".format(suite))
		else:
			logger.log("Sorry, but there was no test-suite in the file")
		logger.flush(quiet)
		
if __name__ == "__main__":
	TermColor.init()
	TestRunner()

			