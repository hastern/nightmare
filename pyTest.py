#!/usr/bin/env python


import sys
import os
import re
import time
from subprocess import *

def isLambda(v):
  return isinstance(v, type(lambda: None)) and v.__name__ == '<lambda>'

class logger:
	buffer = []
	@staticmethod
	def log(str):
		"""
		Writes a log message
		
		@type	str: String
		@param	str: Log message
		"""
		msg = "[{0}] {1}".format(time.strftime("%H:%M:%S") , str.strip("\r\n") )
		logger.buffer.append(msg)
		
	@staticmethod
	def flush(quiet = False):
		if not quiet:
			for b in logger.buffer:
				print b
			sys.stdout.flush()
		logger.clear()
	
	@staticmethod
	def clear():
		logger.buffer = []

  
class TestState:
	Waiting = 0
	Success = 1
	Fail = 2
	Error = 3
	
	@staticmethod
	def toString(state):
		if state == TestState.Waiting:
			return "WAITING"
		if state == TestState.Success:
			return "SUCCESS"
		if state == TestState.Fail:
			return "FAIL"
		if state == TestState.Error:
			return "ERROR"
		return "UNKNOWN"
	
class TestSuiteMode:
	Single = 0
	Continuous = 1
	BreakOnError = 2
	
	@staticmethod
	def toString(mode):
		if mode == TestSuiteMode.Single:
			return "SINGLE"
		if mode == TestSuiteMode.Continuous:
			return "CONTINUOUS"
		if mode == TestSuiteMode.BreakOnError:
			return "BREAK ON ERROR"
		return "UNKNOWN"

class Test:
	name = ""
	descr = ""
	cmd = None
	expectOutput = ""
	expectRetCode = "0"
	output = ""
	retCode = "0"
	state = TestState.Waiting
	
	def __init__(self, data):
		if 'name' in data:
			self.name = data['name']
		if 'descr' in data:
			self.descr = data['descr']
		if "cmd" in data:
			self.cmd = data['cmd']
		else:
			self.state = TestState.Error
		if 'expect' in data:
			self.expectOutput = data['expect']
		else:
			self.expectOutput = ""
		if 'returnCode' in data:
			self.expectRetCode = data['returnCode']
		else:
			self.expectRetCode = "0"
			
	def getName(self):
		return self.name
		
	def getDescription(self):
		return self.descr
		
	def getCommand(self):
		return self.cmd
		
	def getState(self):
		return self.state
		
	def getOutput(self):
		return self.output
		
	def getExpect(self):
		return self.expectOutput
		
	def checkReturnCode(self):
		if (isLambda(self.expectRetCode)):
			return self.expectRetCode(self.retCode)
		elif (isinstance(self.expectRetCode, int) and isinstance(self.RetCode, int)):
			return self.expectRetCode == self.retCode
		elif (isinstance(self.expectRetCode, str)):
			patCode = re.compile(self.expectRetCode, re.IGNORECASE)
			return (patCode.match(str(self.retCode)) != None)
		return True
		
	def checkOutput(self):
		patOut = re.compile(self.expectOutput, re.IGNORECASE | re.DOTALL)
		return (patOut.match(self.output) != None)
	
	def run(self):
		if self.cmd != None:
			try:
				self.output = check_output(self.cmd, stderr=STDOUT, shell=True)
				self.retCode = 0
			except CalledProcessError as e:
				self.output = e.output
				self.retCode = e.returncode
			if self.checkReturnCode() and self.checkOutput():
				self.state = TestState.Success
			else:
				self.state = TestState.Fail
		else:
			self.state = TestState.Error
		return self.state

class TestSuite:
	success = 0
	failed = 0
	count = 0
	error = 0
	lastResult = TestState.Waiting
	rate = 0
	len = 0
	
	testList = []
	mode = TestSuiteMode.Single
	
	def __init__(self, tests = [], mode=TestSuiteMode.Single):
		self.setMode(mode)
		for t in tests:
			self.addTest(t)
		self.len = len(self.testList)
	
	def setMode(self, mode):
		self.mode = mode
		
	def addTest(self, data):
		self.testList.append(Test(data))
		
	def runOne(self, n):
		if (n < self.len):
			result = self.testList[n].run()
			print TestState.toString(result)
			return result
		logger.log("\tSorry but there is no test #{}".format(n))
		print TestState.toString(TestState.Error)
		return TestState.Error
		
	def runAll(self, quiet = False):
		self.success = 0
		self.failed = 0
		self.count = 0
		self.error = 0
		lastResult = TestState.Waiting
		for t in self.testList:
			self.count = self.count + 1 
			self.lastResult = t.run()
			logger.log("Test[{:02}] {} - {}: {}".format(self.count, t.getName(), t.getDescription(), TestState.toString(t.getState())))
			logger.flush(quiet)
			if (self.lastResult == TestState.Success):
				self.success = self.success + 1
			elif (self.lastResult == TestState.Fail):
				self.failed = self.failed + 1
			elif (self.lastResult == TestState.Error):
				self.error = self.error + 1
			if (self.mode == TestSuiteMode.Single) and (self.lastResult != TestState.Success):
				break
			if (self.mode == TestSuiteMode.BreakOnError) and (self.lastResult == TestState.Error):
				break

	def stats(self, quiet = False):
		logger.log("I ran {} out of {} tests in total".format(self.count, len(self.testList)))
		logger.log("\tSuccess: {}".format(self.success))
		if (self.failed > 0):
			logger.log("\tFailed: {}".format(self.failed))
		if (self.error > 0):
			logger.log("\tErrors: {}".format(self.error))
		if (self.error == 0) and (self.failed == 0):
			logger.log("\tCongratulations, you passed all tests!")
		self.rate = float(self.success) / float(self.len) * 100
		return self.rate
		
class TestRunner:

	def __init__(self):
		logger.log("Welcome to pyTest Version 1")
		argv = sys.argv
		argv.pop(0)
		mode = TestSuiteMode.Single
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
	TestRunner()

			