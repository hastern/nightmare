#!/usr/bin/env python

# ---------- ---------- ---------- ---------- ---------- ---------- ---------- #
#@file pyTest                                                                  #
# pyTest is a tool for testing commandline applications.                       #
#                                                                              #
#                                                                              #
#@author Hanno Sternberg <hanno@almostintelligent.de>                          #
#@date 29.10.2012                                                              #
#                                                                              #
# This software is licensed under the MIT License                              #
#                                                                              #
# Copyright (c) 2012 Hanno Sternberg                                           #
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


import sys
import os
import re
import time
import subprocess
import Tkinter as guitk
from Tkinter import LEFT, RIGHT, TOP, DISABLED, N, E, S, W, NE, SE, SW, NW, CENTER, X, Y, BOTH
from threading import Thread
import tkFileDialog as fileDiag
try:
	import colorama
except:
	colorama = None



__package__ = "pyTest"

# ---------- ---------- ---------- ---------- ---------- ---------- ---------- #
# Utility section                                                              #
#                                                                              #
# ---------- ---------- ---------- ---------- ---------- ---------- ---------- #

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

# ---------- ---------- ---------- ---------- ---------- ---------- ---------- #
# Test section                                                                 #
#                                                                              #
# ---------- ---------- ---------- ---------- ---------- ---------- ---------- #

  
class TestState:
	"""The test ist waiting for execution"""
	Success = 0
	"""The test was successful"""
	Fail = 1
	"""The test has failed"""
	Error = 2
	"""Enumeration of test states"""
	Waiting = 3
	"""The test has producsed an error"""
	Disabled = 4
	"""Disables the test"""
	InfoOnly = 5
	"""Display only the test information"""
	Timeout = 6
	"""The test has timed out"""
	
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
		if state == TestState.Disabled:
			return TermColor.colorText("DISABLED", TermColor.Blue)
		if state == TestState.InfoOnly:
			return TermColor.colorText("INFO", TermColor.White)		
		if state == TestState.Timeout:
			return TermColor.colorText("TIMEOUT", TermColor.Purple)
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

class Command():
	"""Command execution"""
	def __init__(self, cmd):
		"""
		Initialises the command
		
		@type	cmd: str
		@param	cmd: Command
		"""
		self._cmd = cmd
		self._process = None
		self._thread = None
		self.out = ""
		self.err = ""
		self.ret = 0
		self.killed = False

	def commandFunc(self):
		"""command to be run in the thread"""
		self._process = subprocess.Popen(self._cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
		self.out, self.err = self._process.communicate()
		self.ret = self._process.wait()
		
	def execute(self, timeout):
		"""
		executes the command
				
		@type	timeout: float
		@param	timeout: Timeout in seconds
		"""
		self._thread = Thread(target=self.commandFunc)
		self._thread.start()
		self._thread.join(timeout)
		if self._thread.isAlive():
			if sys.platform == "win32":
				subprocess.Popen(['taskkill', '/F', '/T', '/PID', str(self._process.pid)]).communicate()
			else:
				os.killgp(self._process.pid)
			self._thread.join()
			return False
		return True
	
class Test:
	"""A single test"""
	name = ""
	"""The name of the test"""
	descr = ""
	"""The description of the game"""
	cmd = None
	"""The command to be executed"""
	expectStdout = ""
	"""The expected output on stdout"""
	expectStderr = ""
	"""The expected output on stderr"""
	expectRetCode = 0
	"""The expected return code"""
	output = ""
	"""The stdout"""
	error = ""
	"""The stderr"""
	retCode = 0
	"""The return code"""
	state = TestState.Waiting
	"""The state of the game"""
	pipe = False
	"""Flag, set if the output streams should be piped"""
	timeout = 60.0
	"""Timeout after the DUT gets killed"""
	
	def __init__(self, data=None, DUT=None, name=None, description=None, command=None, stdout=None, stderr=None, returnCode=None, timeout=60.0):
		"""
		Initalises a test
		
		@type	data: Dictionary
		@param	data: Dictionary with test definitions
		"""
		if data is not None:
			if 'name' in data:
				self.name = data['name']
			if 'descr' in data:
				self.descr = data['descr']
			if "cmd" in data:
				self.cmd = data['cmd']
			else:
				self.state = TestState.Error
			if 'stdout' in data:
				self.expectStdout = data['stdout']
			else:
				self.expectStdout = None
			if 'stderr' in data:
				self.expectStderr = data['stderr']
			else:
				self.expectStderr = None
			if 'returnCode' in data:
				self.expectRetCode = data['returnCode']
			else:
				self.expectRetCode = None
		else:
			self.name = name
			self.descr = description
			self.cmd = command
			self.expectStdout = stdout
			self.expectStderr = stderr
			self.expectRetCode = returnCode
			self.timeout = timeout
		if DUT is not None:
			self.DUT = DUT
		self.output = ""
		self.error = ""
		self.state = TestState.Waiting
		self.pipe = False
			
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
			if exp.startswith("lambda"):
				f = eval(exp)
				return f(out)
			if exp.startswith("regex:"):
				patCode = re.compile(exp[6:].strip(), re.IGNORECASE)
				return (patCode.match(str(out).strip()) != None)
			else:
				return exp == str(out).rstrip()
		elif exp is None:
			return True
		return False
	
	def run(self):
		"""Runs the test"""
		if self.state == TestState.Disabled:
			return TestState.Disabled
		if self.state == TestState.InfoOnly:
			print "{} - {}".format(self.name, self.descr)
			return TestState.InfoOnly
		if self.cmd is not None and self.DUT is not None:
			cmd_ = Command(cmd=str(self.cmd).replace("$DUT", self.DUT))
			if cmd_.execute(self.timeout):
				self.output = cmd_.out
				self.error = cmd_.err
				self.retCode = cmd_.ret
				if (self.pipe):
					print >> sys.stdout, self.output.rstrip()
					print >> sys.stderr, self.error.rstrip()
				if self._check(self.expectRetCode, self.retCode) and self._check(self.expectStdout,self.output.rstrip()) and self._check(self.expectStderr,self.error.rstrip()):
					self.state = TestState.Success
				else:
					self.state = TestState.Fail
			else:
				self.state = TestState.Timeout
		else:
			self.state = TestState.Error
		return self.state
		
	def toString(self, prefix="\t"):
		"""
		Creates a textual representation of the test.
		The output can be saved to a file.
		
		@rtype: 	String
		"""
		fields = []
		fields.append("{}\tname = \"{:s}\"".format(prefix, self.name))
		if self.descr is not None and self.descr != "":
			fields.append("\t\tdescription = \"{:s}\"".format(prefix, self.descr))
		fields.append("\t\tcommand = \"{:s}\"".format(prefix, self.cmd))
		if self.expectStdout is not None:
			fields.append("\t\tstdout = \"{}\"".format(prefix, self.expectStdout))
		if self.expectStderr is not None:
			fields.append("\t\tstderr = \"{}\"".format(prefix, self.expectStderr))
		if self.expectRetCode is not None:
			fields.append("\t\treturnCode = \"{}\"".format(prefix, self.expectRetCode))
		return "Test (\n{}\n{})".format(",\n".join(fields), prefix)

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
	_timedout = 0
	"""The total number of timed out tests"""
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
	
	def __init__(self, tests = [], DUT=None, mode=TestSuiteMode.BreakOnFail):
		"""
		Initialises a test suite
		
		@type	tests: List
		@param	tests: List of tests, default is an empty list
		
		@type	mode: TestSuiteMode
		@param	mode: The initial mode of the testsuite
		"""
		self.setMode(mode)
		self._testList = []
		for t in tests:
			if isinstance(t, Test):
				self._testList.append(t)
				t.DUT = str(DUT)
			else:
				self.addTest(t, DUT)
		self._len = len(self._testList)
		self._succes = TestSuite._success
		self._failed = TestSuite._failed
		self._count = TestSuite._count
		self._error = TestSuite._error
		self._timedout = TestSuite._timedout
		self._lastResult = TestSuite._lastResult
		self._rate = TestSuite._rate
	
	def getRate(self):
		"""Returns the success rate"""
		return self._rate
		
	def setMode(self, mode):
		"""
		Sets the mode of the testsuite
		
		@type	mode: TestSuiteMode
		@param	mode: New mode
		"""
		self._mode = mode
		
	def setDUT(self, DUT):
		"""Define the 'Device under Test'"""
		if DUT is not None:
			self.DUT = DUT
			for t in self._testList:
				t.DUT = DUT
		
	def addTest(self, data, DUT):
		"""
		Adds a test to the suite
		
		@type	data: Test
		@param	data: Test to add
		"""
		self._testList.append(Test(data, DUT))
		
	def getTests(self):
		return self._testList
		
	def setAll(self, infoOnly=False, disabled=False, pipe=False): 
		for t in self._testList:
			if disabled:
				t.state = TestState.Disabled
			elif infoOnly:
				t.state = TestState.InfoOnly
			t.pipe = pipe
		
	def runOne(self, n):
		"""
		Run one single test
		
		@type	n: int
		@param	n: Number of the test
		"""
		if (n < self._len):
			t = self._testList[n]
			self._lastResult = t.run()
			logger.log("Test[{:02}] {} - {}: {}".format(n, t.name, t.descr, TestState.toString(t.state)))
			return self._lastResult
		logger.log("\tSorry but there is no test #{}".format(n))
		self._lastResult = TestState.Error
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
			logger.log("Test[{:02}] {} - {}: {}".format(self._count, t.name, t.descr, TestState.toString(t.state)))
			logger.flush(quiet)
			if self._lastResult == TestState.Success:
				self._success = self._success + 1
			elif self._lastResult == TestState.Fail:
				self._failed = self._failed + 1
			elif self._lastResult == TestState.Error:
				self._error = self._error + 1
			elif self._lastResult == TestState.Timeout:
				self._timedout = self._timedout + 1
			if self._lastResult != TestState.Disabled:
				if (self._mode == TestSuiteMode.BreakOnFail) and (self._lastResult != TestState.Success):
					break
				if (self._mode == TestSuiteMode.BreakOnError) and (self._lastResult == TestState.Error):
					break

	def calcRate(self):
		self._rate = float(self._success) / float(self._len) * 100
		return self._rate
				
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
		if (self._timedout > 0):
			logger.log(TermColor.colorText("\tTimeouts: {}".format(self._timedout), TermColor.Purple))
		if (self._error == 0) and (self._failed == 0) and (self._timedout == 0):
			logger.log("\tCongratulations, you passed all tests!")
		return self.calcRate()
		
class TestRunner(Thread):
	"""Testrunner. Reads a testbench file and executes the testrun"""
	suite = "suite"
	"""Test suite selector"""
	test = -1
	"""single test selector"""
	quiet = False
	"""Definition of the programs verbosity"""
	mode = TestSuiteMode.BreakOnFail
	"""Mode for the test suite"""
	file = ""
	"""test bench file"""
	tests = 0
	"""Specific test selection"""
	lengthOnly = False
	"""print only number of test"""
	infoOnly = False
	"""Print only the test information"""
	
	def __init__(self):
		"""Initialises the test runner"""
		Thread.__init__(self)
		logger.log("Welcome to pyTest Version 1")
		self.suite = TestRunner.suite
		self.test = TestRunner.test
		self.quiet = TestRunner.quiet
		self.mode = TestRunner.mode
		self.file = TestRunner.file
		self.lengthOnly = False
		self._runsuite = None
		self.DUT = None
		self._finished = None
		self._pipe = False
		
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
			elif arg.startswith("-dut:") or arg.startswith("-DUT:"):
				self.setDUT(arg[5:])
				logger.log("\tDevice under Test is: {}".format(self.DUT))
			elif arg.startswith("--info-only"):
				self.infoOnly = True
				self.mode = TestSuiteMode.Continuous
				logger.log("\tI will only print the test information.")
			elif arg == "-p":
				self._pipe = True
				logger.log("\tI will pipe all tests outputs to their respective streams")
	
	def loadSuite(self):
		"""Loads the suite from a file"""
		logger.log("\nReading testfile ...")
		glb = {"__builtins__":None, "Test":Test, "Suite":TestSuite}
		ctx = {self.suite:None, "DUT":None}
		self._runsuite = None
		execfile(self.file, glb, ctx)
		if (self.suite in ctx):
			if (ctx[self.suite] != None):
				self._runsuite = TestSuite(ctx[self.suite], DUT=self.DUT, mode=self.mode)
				self._runsuite.setAll(infoOnly=self.infoOnly, disabled = False, pipe=self._pipe)
				self.tests = len(self._runsuite._testList)
				if "DUT" in ctx and ctx['DUT'] is not None and self.DUT is None:
					self.setDUT(ctx["DUT"])
			else:
				logger.log("Sorry, but I can't find any tests inside the suite '{}'".format(self.suite))
		else:
			logger.log("Sorry, but there was no test-suite in the file")
		return self._runsuite
		
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
		if self._finished != None:
			self._finished()
		Thread.__init__(self) # This looks like a real dirty hack :/
	
	
# ---------- ---------- ---------- ---------- ---------- ---------- ---------- #
# GUI section                                                                  #
#                                                                              #
# ---------- ---------- ---------- ---------- ---------- ---------- ---------- #

class TestRunButton(guitk.Button):
	"""Button to start one test run"""
	def __init__(self, parent, gui, caption, n, runner):
		"""
		Initialise the button
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	gui: TK
		@param	gui: The main window
		
		@type	n: int 
		@param	n: Number of the test
		
		@type	caption: String
		@param 	caption: Caption of the button
		
		@type	runner: TestRunner
		@param	runner: The test runner
		"""
		guitk.Button.__init__(self, parent, text=caption, command=self.runTest, width=7)
		self._num = n
		self._runner = runner
		self._gui = gui
		
	def runTest(self):
		"""Run the test(s)"""
		self._runner.mode = self._gui._mode.get()
		if self._num == -1:
			self._runner.start(self.finishHandler)
		else:
			self._runner.start(self.finishHandler, self._num)

	def finishHandler(self):
		"""Handler for updating the datagrid after the test run"""
		self._gui.dataGrid.update()
		
		
class TestSaveButton(guitk.Button):
	"""Button to the save the test data"""
	def __init__(self, parent, test, gui):
		"""
		Initialise the button
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	gui: TK
		@param	gui: The main window
		
		@type	test: Test
		@param	test: The test data
		"""
		guitk.Button.__init__(self, parent, text="Save", command=self.saveTest, width=7)
		self._test = test
		self._parentForm = parent
		self._gui = gui
		
	def saveTest(self):
		"""Save the test"""
		self._test.name = self._parentForm._varname.get()
		self._test.descr = self._parentForm._vardescr.get()
		self._test.cmd = self._parentForm._varcmd.get()
		out = self._parentForm._expOut.get(1.0, 'end').rstrip()
		err = self._parentForm._expErr.get(1.0, 'end').rstrip()
		if out != "":
			self._test.expectStdout = out
		if err != "":
			self._test.expectStderr = err
		self._test.expectRetCode = self._parentForm._varexpRet.get()
		self._gui.dataGrid.update()
		
class TestEditForm(guitk.Toplevel):
	"""Form for editing one test"""
	def __init__(self, parent, n, test, runner, gui):
		"""
		Initialises the form
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	gui: TK
		@param	gui: The main window
		
		@type	n: int 
		@param	n: Number of the test
		
		@type	test: Test
		@param 	test: The test to be edited
		
		@type	runner: TestRunner
		@param	runner: The test runner
		"""
		guitk.Toplevel.__init__(self, parent)
		self.title("Edit test {}".format(n))
		self._test = test
		self._gui = gui
		# Variables
		self._varname = guitk.StringVar(self, self._test.name)
		self._vardescr = guitk.StringVar(self, self._test.descr)
		self._varcmd = guitk.StringVar(self, self._test.cmd)
		self._varret = guitk.StringVar(self, self._test.retCode)
		self._varexpRet = guitk.StringVar(self, self._test.expectRetCode)
		# Widgets
		guitk.Label(self, text="Name").grid(row=0, column=0, columnspan=2)
		guitk.Entry(self, width=50, textvariable=self._varname).grid(row=1, column=0, columnspan=2, sticky=N+E+S+W)
		guitk.Label(self, text="Description").grid(row=0, column=2, columnspan=4)
		guitk.Entry(self, width=70, textvariable=self._vardescr).grid(row=1, column=2, columnspan=4, sticky=N+E+S+W)
		guitk.Label(self, text="Command").grid(row=2, column=0, columnspan=6)
		guitk.Entry(self, width=120, textvariable=self._varcmd).grid(row=3, column=0, columnspan=6, sticky=N+E+S+W)
		guitk.Label(self, text="Expected stdout").grid(row=4, column=0, columnspan=3)
		self._expOut = guitk.Text(self, width=50, height=5)
		self._expOut.grid(row=5, column=0, columnspan=3, sticky=N+E+S+W)
		guitk.Label(self, text="stdout").grid(row=4, column=3, columnspan=3)
		self._out = guitk.Text(self, width=50, height=5)
		self._out.grid(row=5, column=3, columnspan=3, sticky=N+E+S+W)
		guitk.Label(self, text="Expected Stderr").grid(row=6, column=0, columnspan=3)
		self._expErr = guitk.Text(self, width=50, height=5)
		self._expErr.grid(row=7, column=0, columnspan=3, sticky=N+E+S+W)
		guitk.Label(self, text="stderr").grid(row=6, column=3, columnspan=3)
		self._err = guitk.Text(self, width=50, height=5)
		self._err.grid(row=7, column=3, columnspan=3, sticky=N+E+S+W)
		guitk.Label(self, text="Expected Returncode").grid(row=8, column=0, columnspan=2)
		guitk.Entry(self, width=30, textvariable=self._varexpRet).grid(row=9, column=0, columnspan=2, sticky=N+E+S+W)
		guitk.Label(self, text="Returncode").grid(row=8, column=2, columnspan=2)
		guitk.Entry(self, width=30, textvariable=self._varret, state=DISABLED).grid(row=9, column=2, columnspan=2, sticky=N+E+S+W)
		TestRunButton(self, gui, "Run", n-1, runner).grid(row=9, column=4)
		TestSaveButton(self, test, gui).grid(row=9, column=5)
		# Fill data
		if not isLambda(self._test.expectStdout) and self._test.expectStdout is not None:
			self._expOut.insert(guitk.INSERT, str(self._test.expectStdout))
		if not isLambda(self._test.expectStderr) and self._test.expectStderr is not None:
			self._expErr.insert(guitk.INSERT, str(self._test.expectStderr))
		if self._test.output != "":
			self._out.insert(guitk.INSERT, str(self._test.output))
		if self._test.error != "":
			self._err.insert(guitk.INSERT, str(self._test.error))

		
class TestEditButton(guitk.Button):
	"""Button for editing a test"""
	def __init__(self, parent, gui, caption, test, n):
		"""
		Initialise the test edit button
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	gui: TK
		@param	gui: The main window
		
		@type	caption: String
		@param	caption: The caption of the button
		
		@type	test: Test
		@param	test: The test to be edited
		
		@type 	n: int
		@param	n: The number of the test
		"""
		guitk.Button.__init__(self, parent, text=caption, command=self.editTest, width=7)
		self._test = test
		self._gui = gui
		self._num = n
		
	def editTest(self):
		TestEditForm(self, self._num, self._test, self._gui._runner, self._gui)
		
class TestCreateButton(guitk.Button):
	"""Button for creating a new test"""
	def __init__(self, parent, gui, caption, runner):
		"""
		Initialise the test edit button
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	gui: TK
		@param	gui: The main window
		
		@type	caption: String
		@param	caption: The caption of the button
		
		@type	test: Test
		@param	test: The test to be edited
		
		@type 	n: int
		@param	n: The number of the test
		"""
		guitk.Button.__init__(self, parent, text=caption, command=self.createTest)
		self._gui = gui
		self._runner = runner
		
	def createTest(self):
		"""Eventhandler for button click"""
		test = Test()
		self._runner.getSuite().getTests().append(test)
		self._gui.dataGrid.update()
		self._gui.dataGrid.scroll()
		TestEditForm(self, len(self._runner.getSuite().getTests()), test, self._runner, self._gui)
		
class FileLoaderButton(guitk.Button):
	"""Button for handling file selection"""
	def __init__(self, parent, caption, callback, func=fileDiag.askopenfilename, filetypes=[("All files","*")], defaultExt=""):
		"""
		Initialises the button
		
		@type 	parent: Widget
		@param	parent: Parent widget
		
		@type	caption: String
		@param	caption: Caption for the button
		
		@type	callback: Function
		@param 	callback: Callback function, called after successfull selection
		
		@type	func: Function
		@param	func: Function to be called for file selection
		"""
		guitk.Button.__init__(self, parent, text=caption, command=self.selectFile)
		self._callback = callback
		self._func = func
		self._caption = caption
		self._filetypes = filetypes
		self._defaultExt = defaultExt
	
	def selectFile(self):
		"""Eventhandler for button click"""
		if self._func is not None:
			fn = self._func(initialdir=".", filetypes=self._filetypes, defaultextension=self._defaultExt, title=self._caption)
			if fn != "":
				self._callback(fn)
	
class LabeledEntry(guitk.Frame):
	def __init__(self, parent, gui, lbl, var, pos=LEFT, anch=NW):
		"""
		Initialise the labeled entry
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	gui: TK
		@param	gui: The main window
		
		@type	lbl: String
		@param	lbl: The caption for the label
		
		@type	var: StringVar
		@param	var: The variable holding the content in the entry field
		
		@param	pos: Packing position for both widgets
		@param	anch: Packing anchor for both widgets
		"""
		guitk.Frame.__init__(self, parent)
		self._gui = gui
		self.label = guitk.Label(self, text=lbl, width=10, justify=LEFT)
		self.entry = guitk.Entry(self, textvariable=var, width=20, justify=LEFT)
		self.label.pack(side=pos, anchor=anch)
		self.entry.pack(side=pos, anchor=anch, fill=X, expand=1)
		
class TestRow(guitk.Frame):
	"""The TestRow represents a single row inside the Testgrid"""
	def __init__(self, parent, gui, runner, n, test):
		"""
		Initialise the row
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	gui: TK
		@param	gui: The main window
		
		@type	runner: TestRunner
		@param	runner: The testrunner holding the test data
		
		@type 	n: int
		@param	n: Number of the test
		
		@type	test: Test
		@param	test: The testdata
		"""
		guitk.Frame.__init__(self, parent)
		self._gui = gui
		self._runner = runner
		self._num = n
		self._test = test
		self._bgcol = "#FFF"
		self._fgcol = "#000"
		self.setColor()
		self._edtBtn = TestEditButton(self, self._gui, "Edit", test, self._num)
		self._edtBtn.pack(side=LEFT)
		self._checkBtn = guitk.Checkbutton(self, command=self.clickCheck)
		self._checkBtn.pack(side=LEFT)
		self._checkBtn.select()
		self._lblNum = guitk.Label(self, text="{:02}".format(n), bg=self._bgcol, fg=self._fgcol, width=3)
		self._lblNum.pack(side=LEFT)
		self._lblName = guitk.Label(self, text=test.name, bg=self._bgcol, fg=self._fgcol, width=20)
		self._lblName.pack(side=LEFT)
		self._lblDescr = guitk.Label(self, text=test.descr, bg=self._bgcol, fg=self._fgcol, width=40)
		self._lblDescr.pack(side=LEFT, expand=1, fill=X)
		
	def setColor(self):
		"""Set colors based on TestState"""
		if self._test.state == TestState.Success:
			self._bgcol = "#0D0"
			self._fgcol = "#000"
		elif self._test.state == TestState.Fail:
			self._bgcol = "#D00"
			self._fgcol = "#FFF"
		elif self._test.state == TestState.Error:
			self._bgcol = "#DD0"
			self._fgcol = "#000"
		elif self._test.state == TestState.Waiting:
			self._bgcol = "#FFF"
			self._fgcol = "#000"
		elif self._test.state == TestState.Disabled:
			self._bgcol = "#FFF"
			self._fgcol = "#888"
	
	def update(self):
		"""Updates the widgets"""
		self.setColor()
		self._lblNum.config(fg=self._fgcol, bg=self._bgcol)
		self._lblName.config(fg=self._fgcol, bg=self._bgcol, text=self._test.name)
		self._lblDescr.config(fg=self._fgcol, bg=self._bgcol, text=self._test.descr)
		
	def clickCheck(self):
		"""Eventhandler for checkbutton click"""
		if self._test.state == TestState.Disabled:
			self._test.state = TestState.Waiting
			self._checkBtn.select()
		else:
			self._test.state = TestState.Disabled
			self._checkBtn.deselect()
		
		
class TestGrid(guitk.Frame):
	"""A TestGrid displays all tests and their result."""
	def __init__(self, parent, gui, runner):
		"""
		Initialise the grid
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	gui: TK
		@param	gui: The main window
		
		@type	runner: TestRunner
		@param	runner: The testrunner holding the test data
		"""
		guitk.Frame.__init__(self, parent)
		self._gui = gui
		self._runner = runner
		self._rows = []
		self.createHead()
		self._visible = (0,9)
	
	def createHead(self):
		"""Create the head of the grid"""
		head = guitk.Frame(self)
		guitk.Button(head, text="+", command=self.scrollUp, width=3).pack(side=LEFT)
		guitk.Button(head, text="-", command=self.scrollDown, width=3).pack(side=LEFT)
		self._toggleAll = guitk.Checkbutton(head)
		self._toggleAll.pack(side=LEFT)
		guitk.Label(head, text="#", width=3).pack(side=LEFT)
		guitk.Label(head, text="Name", width=20).pack(side=LEFT)
		guitk.Label(head, text="Description", width=40).pack(side=LEFT, expand=1, fill=X)
		head.pack(side=TOP, expand=1, fill=BOTH, anchor=NW)
	
	def scrollUp(self):
		"""Scroll the grid one row up"""
		lower, upper = self._visible
		if upper < len(self._rows)-1:
			lower = lower + 1
			upper = upper + 1
			self._visible = lower, upper
			self.scroll()
	
	def scrollDown(self):
		"""Scroll the grid one row down"""
		lower, upper = self._visible
		if lower > 0:
			lower = lower - 1
			upper = upper - 1
			self._visible = lower, upper
			self.scroll()
	
	def addRow(self, test):
		"""
		Add a row to the gridd
		
		@type 	test: Test
		@param	test: Test with data for the row
		"""
		row = TestRow(self, self._gui, self._runner, len(self._rows)+1, test)
		self._rows.append(row)
	
	def update(self):
		"""Update the grid"""
		i = 0
		for t in self._runner.getSuite().getTests():
			if i >= len(self._rows):
				self.addRow(t)
			else:
				self._rows[i].update()
			i = i + 1
			
	def scroll(self):
		"""Scroll through the grid"""
		lower, upper = self._visible
		if upper > len(self._rows):
			upper = len(self._rows)-1
		for row in self._rows:
			row.pack_forget()
		for i in range(lower, upper+1):
			self._rows[i].pack(side=TOP, expand=1, fill=BOTH, anchor=NW)
			
	def clear(self):
		"""remove all rows from the grid"""
		for row in self._rows:
			row.pack_forget()
			row.destroy()
		self._rows = []
		
class TestRunnerGui(Thread):
	"""Graphical User Interface"""
	
	def _handleSuiteLoad(self, fn):
		"""
		Load a testsuite
		
		@type	fn: String
		@param 	fn: The filename
		"""
		dut = os.path.abspath(self._DUT.get())
		os.chdir(os.path.dirname(fn))
		self._DUT.set(os.path.relpath(dut))
		#print os.getcwd()
		self._runner.suite = self._suite.get()
		self._runner.file = os.path.relpath(fn)
		self._runner.mode = self._mode.get()
		self._runner.loadSuite()
		if self._runner.DUT is not None:
			self._DUT.set(self._runner.DUT)
		self._tests.set(self._runner.tests)
		self._filename.set(os.path.relpath(fn))
		self.dataGrid.clear()
		self.dataGrid.update()
		self.dataGrid.scroll()
		
	def _handleSelectDUT(self, fn):
		"""
		Select a device under test
		
		@type	fn: String
		@param 	fn: The device under test (DUT)
		"""
		self._runner.setDUT(fn)
		self._DUT.set(os.path.relpath(fn))
		
	def _handleSuiteSave(self, fn):
		"""
		Save the testsuite into a file
		
		@type	fn: String
		@param 	fn: The filename
		"""
		fHnd = open(fn,"w")
		fHnd.write("#!/usr/bin/env python\n\n")
		fHnd.write("# pyTest - Testbench\n")
		fHnd.write("# Saved at {}\n".format(time.strftime("%H:%M:%S")))
		fHnd.write("# \n\n")
		#fHnd.write("# Author: {}\n".format())
		if self._runner.DUT is not None:
			fHnd.write("# Device Under Test\n")
			fHnd.write("DUT = \"{}\"\n\n".format(os.path.relpath(self._runner.DUT)))
		fHnd.write("# Test definitions\n")
		fHnd.write("{} = [\n".format(self._suite.get()))
		tests = []
		for test in self._runner.getSuite().getTests():
			tests.append("\t{}".format( test.toString()))
		fHnd.write(",\n".join(tests))
		fHnd.write("\n]\n")
		fHnd.close()
	
	def __init__(self):
		"""Initialise the gui"""
		Thread.__init__(self)
		self._runner = TestRunner()
		self._runner.parseArgv()
		self._whnd = guitk.Tk()
		self._whnd.title("pyTest GUI")
		
		# Frames
		cfgFrame = guitk.Frame(self._whnd)
		suiteFrame = guitk.LabelFrame(cfgFrame, text="Suite")
		suiteInfoFrame = guitk.Frame(suiteFrame)
		actionFrame = guitk.LabelFrame(cfgFrame, text="Mode")
		# Variables
		self._suite = guitk.StringVar(suiteInfoFrame, self._runner.suite)
		self._tests = guitk.StringVar(suiteInfoFrame, self._runner.tests)
		self._filename = guitk.StringVar(suiteInfoFrame, "")
		self._DUT = guitk.StringVar(suiteInfoFrame, "")
		self._mode = guitk.IntVar(actionFrame, TestSuiteMode.BreakOnFail)
		# Suite info
		self._suiteFile = LabeledEntry(suiteInfoFrame, self, lbl="File", var=self._filename)
		self._suiteFile.entry.configure(state=DISABLED)
		self._suiteName = LabeledEntry(suiteInfoFrame, self, lbl="Name", var=self._suite)
		self._suiteTests = LabeledEntry(suiteInfoFrame, self, lbl="Tests", var=self._tests)
		self._suiteTests.entry.configure(state=DISABLED)
		self._DUTName = LabeledEntry(suiteInfoFrame, self, lbl="DUT", var=self._DUT)
		self._DUTName.entry.configure(state=DISABLED) 
		self._loadSuite = FileLoaderButton(suiteFrame, "Load Testsuite", self._handleSuiteLoad, filetypes=[("Python Script","*.py"), ("pyTest Testbench","*.test.py")], defaultExt=".test.py")
		self._saveSuite = FileLoaderButton(suiteFrame, "Save Testsuite", self._handleSuiteSave, fileDiag.asksaveasfilename, filetypes=[("Python Script","*.py"), ("pyTest Testbench","*.test.py")], defaultExt=".test.py")
		self._addTest = TestCreateButton(suiteFrame, self, "Add Test", self._runner)
		self._loadDUT = FileLoaderButton(actionFrame, "Select DUT", self._handleSelectDUT)
		self._runBtn = TestRunButton(actionFrame, self, caption="Run All", n=-1, runner=self._runner)
		# Pack all widgets
		
		self._loadDUT.pack(side=LEFT, expand=1, fill=Y, anchor=NW)
		self._runBtn.pack(side=LEFT, expand=1, fill=Y, anchor=NW)
		guitk.Radiobutton(actionFrame, text="Continuous", variable=self._mode, value=TestSuiteMode.Continuous).pack()
		guitk.Radiobutton(actionFrame, text="Halt on Fail", variable=self._mode, value=TestSuiteMode.BreakOnFail).pack()
		guitk.Radiobutton(actionFrame, text="Halt on Error", variable=self._mode, value=TestSuiteMode.BreakOnError).pack()
		
		self._loadSuite.pack(side=LEFT, expand=1, fill=Y, anchor=NW)
		self._saveSuite.pack(side=LEFT, expand=1, fill=Y, anchor=NW)
		self._DUTName.pack(side=TOP, expand=1, fill=X, anchor=NW)
		self._suiteFile.pack(side=TOP, expand=1, fill=X, anchor=NW)
		self._suiteName.pack(side=TOP, expand=1, fill=X, anchor=NW)
		self._suiteTests.pack(side=TOP, expand=1, fill=X, anchor=NW)
		suiteInfoFrame.pack(side=LEFT, expand=1, fill=X, anchor=NW)
		self._addTest.pack(side=LEFT, expand=1, fill=Y, anchor=NW)
		suiteFrame.pack(side=LEFT, anchor=NW)
		actionFrame.pack(side=RIGHT, anchor=NE)
		cfgFrame.pack(side=TOP, expand=1, fill=X, anchor=N)
		# create and pack datagrid
		self.dataGrid = TestGrid(self._whnd, self, self._runner)
		self.dataGrid.pack(side=TOP, expand=1, fill=X, anchor=NW)
		
	def run(self):
		"""Run function for the gui thread"""
		self._whnd.mainloop()

# ---------- ---------- ---------- ---------- ---------- ---------- ---------- #
# handle script start                                                          #
#                                                                              #
# ---------- ---------- ---------- ---------- ---------- ---------- ---------- #

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
	

if __name__ == "__main__":
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
		gui.start()
	
			