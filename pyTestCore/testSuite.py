#!/usr/bin/env python


from test import Test
from utils import logger, TermColor
from testMode import TestSuiteMode
from testState import TestState

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
		self._testList = []
		"""The collection of tests"""
		for t in tests:
			if isinstance(t, Test):
				self._testList.append(t)
				t.DUT = str(DUT)
			else:
				self.addTest(t, DUT)
		self._success = 0
		"""The number of successful tests"""
		self._failed = 0
		"""The number of failed tests"""
		self._count = 0
		"""A counter for the executed tests"""
		self._error = 0
		"""The number of errors occured during the testrun"""
		self._timedout = 0
		"""The total number of timed out tests"""
		self._lastResult = TestState.Waiting
		"""The result of the last test"""
		self._rate = 0
		"""The successrate of the testrun"""
		self._len = len(self._testList)
		"""The total number of tests in the suite"""

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
		self._len = len(self._testList)
		
	def getTests(self):
		return self._testList
		
	def setAll(self, infoOnly=False, disabled=False, pipe=False, out=False, timeout=None, linesep=None): 
		for t in self._testList:
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
		if (n < self._len):
			t = self._testList[n]
			self._lastResult = t.run()
			logger.log("Test[{:02}] {} - {}: {}".format(n, t.name, t.descr, TestState.toString(t.state)))
			return self._lastResult
		else:
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