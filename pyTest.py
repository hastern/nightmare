#!/usr/bin/env python


import sys
import os
import re
from subprocess import *

def isLambda(v):
  return isinstance(v, type(lambda: None)) and v.__name__ == '<lambda>'

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
		elif (isinstance(self.expectRetCode, str)):
			patCode = re.compile(self.expectRetCode)
			return patCode.match(self.retCode) != None
		elif (isinstance(self.expectRetCode, int)):
			return self.expectRetCode == self.retCode
		return True
		
	def checkOutput(self):
		patOut = re.compile(self.expectOutput)
		return patOut.match(self.output, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.DEBUG) != None
	
	def run(self):
		if self.cmd != None:
			try:
				self.output = check_output(self.cmd, stderr=STDOUT, shell=True)
				self.retCode = "0"
			except CalledProcessError as e:
				self.output = e.output
				self.retCode = e.returncode
			if self.checkReturnCode and self.checkOutput:
				self.state = TestState.Success
			else:
				self.state = TestState.Fail
		else:
			self.state = TestState.Error
		return self.state

class TestSuite:
	testList = []
	mode = TestSuiteMode.Single
	
	def __init__(self, tests = [], mode=TestSuiteMode.Single):
		self.setMode(mode)
		for t in tests:
			self.addTest(t)
	
	def setMode(self, mode):
		self.mode = mode
		
	def addTest(self, data):
		self.testList.append(Test(data))
		
	def runAll(self):
		success = 0
		failed = 0
		count = 0
		error = 0
		lastResult = TestState.Waiting
		for t in self.testList:
			count = count + 1 
			lastResult = t.run()
			print "Test[{:02}] {} - {}: {}".format(count, t.getName(), t.getDescription(), TestState.toString(t.getState()))
			if (lastResult == TestState.Success):
				success = success + 1
			elif (lastResult == TestState.Fail):
				#print "\tOutput was: {}".format(t.getOutput().strip())
				#print "\tExpected was: {}".format(t.getExpect().strip())
				failed = failed + 1
			elif (lastResult == TestState.Error):
				error = error + 1
			if (self.mode == TestSuiteMode.Single) and (lastResult != TestState.Success):
				break
			if (self.mode == TestSuiteMode.BreakOnError) and (lastResult == TestState.Error):
				break
		
		print "All finished!"
		print "I ran {} out of {} tests in total".format(count, len(self.testList))
		print "\tSuccess: {}".format(success)
		if (failed > 0):
			print "\tFailed: {}".format(failed)
		if (error > 0):
			print "\tErrors: {}".format(error)
		if (error == 0) and (failed == 0):
			print "\tCongratulations, you passed all tests!"
		
class TestRunner:

	def __init__(self):
		print "Welcome to pyTest Version 1"
		argv = sys.argv
		argv.pop(0)
		mode = TestSuiteMode.Single
		suite = 'suite'
		for arg in argv:
			if (arg == "-c"):
				print "\tI'm running in continuous mode now"
				mode = TestSuiteMode.Continuous
			elif (arg == "-e"):
				print "\tI'm running in continuous mode now, but will halt if an error occurs"
				mode = TestSuiteMode.BreakOnError
			elif (arg.startswith("-s")):
				suite = arg[2:]
				print "\tI'm using the testsuite '{}'".format(suite)
			else:
				f = arg
		
		print "\nReading testfile ..."
		glb = {"__builtins__":None}
		ctx = {suite:None}
		execfile(f, glb, ctx)
		if (suite in ctx):
			if (ctx[suite] != None):
				TestSuite(ctx[suite], mode).runAll()
			else:
				print "Sorry, but I can't find any tests inside the suite '{}'".format(suite)
		else:
			print "Sorry, but there was no test-suite in the file"
		
if __name__ == "__main__":
	TestRunner()

			