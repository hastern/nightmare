#!/usr/bin/env python
# -*- coding:utf-8 -*-


from pyTest import Test, TestState
from pyTestUtils import logger, TermColor

class TestSuiteMode:
	#__slots__ = ['Continuous', 'BreakOnFail', 'BreakOnError']
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

class TestSuite:
	"""A testsuite is a collection of tests"""
		
	def __init__(self, tests = [], DUT=None, mode=TestSuiteMode.BreakOnFail):
		"""
		Initialises a test suite
		
		@type	tests: List
		@param	tests: List of tests, default is an empty list
		
		@type	mode: TestSuiteMode
		@param	mode: The initial mode of the testsuite
		"""
		self.setMode(mode)
		"""The test suite mode"""
		self.testList = []
		"""The collection of tests"""
		for t in tests:
			if isinstance(t, Test):
				self.testList.append(t)
				t.DUT = str(DUT)
			else:
				self.addTest(t, DUT)
		self.success = 0
		"""The number of successful tests"""
		self.failed = 0
		"""The number of failed tests"""
		self.count = 0
		"""A counter for the executed tests"""
		self.error = 0
		"""The number of errors occured during the testrun"""
		self.timedout = 0
		"""The total number of timed out tests"""
		self.lastResult = TestState.Waiting
		"""The result of the last test"""
		self.rate = 0
		"""The successrate of the testrun"""
		
	def __len__(self):
		return len(self.testList)
		
	def __iter__(self):
		for test in self.testList:
			yield test
		raise StopIteration()
		
	def __getitem__(self, key):
		return self.testList[key]
		
	def __setitem(self, key, val):
		self.testList[key] = val

	def getRate(self):
		"""Returns the success rate"""
		return self.rate
		
	def setMode(self, mode):
		"""
		Sets the mode of the testsuite
		
		@type	mode: TestSuiteMode
		@param	mode: New mode
		"""
		self.mode = mode
		
	def setDUT(self, DUT):
		"""Define the 'Device under Test'"""
		if DUT is not None:
			self.DUT = DUT
			for t in self.testList:
				t.DUT = DUT
		
	def addTest(self, test):
		"""
		Adds a test to the suite
		
		@type	test: Test
		@param	test: Test to add
		"""
		self.testList.append(test)
		
	def getTests(self):
		return self.testList
		
	def setAll(self, infoOnly=False, disabled=False, pipe=False, out=False, timeout=None, linesep=None): 
		for t in self.testList:
			if disabled:
				t.state = TestState.Disabled
			else:
				t.state = TestState.Waiting
			
			if infoOnly:
				t.state = TestState.InfoOnly
			t.pipe = pipe
			t.outputOnFail = out
			if timeout is not None:
				t.timeout = timeout
			if linesep is not None:
				t.linesep = linesep
		
	def runOne(self, n):
		"""
		Run one single test
		
		@type	n: int
		@param	n: Number of the test
		"""
		if n < len(self):
			t = self.testList[n]
			self.lastResult = t.run()
			if t.descr is not None:
				logger.log("Test[{:02}] {} - {}: {}".format(n, t.name, t.descr, TestState.toString(t.state)))
			else:
				logger.log("Test[{:02}] {}: {}".format(n, t.name, TestState.toString(t.state)))
			return t
		else:
			logger.log("\tSorry but there is no test #{}".format(n))
			self.lastResult = TestState.Error
			return None
		
	def runAll(self, quiet = False, doYield = False):
		"""
		Runs the whole suite of tests
		
		@type	quiet: Boolean
		@param	quiet: Flag, passed along to the logger
		"""
		self.success = 0
		self.failed = 0
		self.count = 0
		self.error = 0
		self.lastResult = TestState.Waiting
		for t in self.testList:
			self.count = self.count + 1 
			self.lastResult = t.run()
			if t.descr is not None:
				logger.log("Test[{:02}] {} - {}: {}".format(self.count, t.name, t.descr, TestState.toString(t.state)))
			else:
				logger.log("Test[{:02}] {}: {}".format(self.count, t.name, TestState.toString(t.state)))
			logger.flush(quiet)
			if self.lastResult == TestState.Success:
				self.success = self.success + 1
			elif self.lastResult == TestState.Fail:
				self.failed = self.failed + 1
			elif self.lastResult == TestState.Error:
				self.error = self.error + 1
			elif self.lastResult == TestState.Timeout:
				self.timedout = self.timedout + 1
			if doYield:
				yield t
			if self.lastResult != TestState.Disabled:
				if (self.mode == TestSuiteMode.BreakOnFail) and (self.lastResult != TestState.Success):
					break
				if (self.mode == TestSuiteMode.BreakOnError) and (self.lastResult == TestState.Error):
					break
		if doYield:
			raise StopIteration()

	def calcRate(self):
		self.rate = float(self.success) / float(len(self)) * 100
		return self.rate
				
	def stats(self, quiet = False):
		"""
		Generate and write the stats
		
		@type	quiet: Boolean
		@param	quiet: Flag, passed along to the logger
		"""
		logger.log("I ran {} out of {} tests in total".format(self.count, len(self.testList)))
		logger.log(TermColor.colorText("\tSuccess: {}".format(self.success), TermColor.Green))
		if (self.failed > 0):
			logger.log(TermColor.colorText("\tFailed: {}".format(self.failed), TermColor.Red))
		if (self.error > 0):
			logger.log(TermColor.colorText("\tErrors: {}".format(self.error), TermColor.Yellow))
		if (self.timedout > 0):
			logger.log(TermColor.colorText("\tTimeouts: {}".format(self.timedout), TermColor.Purple))
		if (self.error == 0) and (self.failed == 0) and (self.timedout == 0):
			logger.log("\tCongratulations, you passed all tests!")
		return self.calcRate()