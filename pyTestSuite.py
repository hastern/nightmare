#!/usr/bin/env python
# -*- coding:utf-8 -*-


from pyTest import Test, TestState
from pyTestUtils import logger, TermColor

class TestSuiteMode:
	#__slots__ = ['Continuous', 'BreakOnFail', 'BreakOnError']
	"""Enumeration for testsuite modes """
	BreakOnFail = 0
	"""Halt on first failed test"""
	BreakOnError = 1
	"""Halt on first erroneous test"""
	Continuous = 2
	"""Run all test"""
	
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

class TestSuite(object):
	"""A testsuite is a collection of tests"""
		
	def __init__(self, *tests, **options):
		"""
		Initialises a test suite
		
		@type	tests: List
		@param	tests: List of tests, default is an empty list
		
		@type	mode: TestSuiteMode
		@param	mode: The initial mode of the testsuite
		@type	DUT: str
		@param 	DUT: The path to the Device Under Test
		@type	timeout: float
		@param	timeout: The time out be before the DUT gets killed
		@type	pipe: Boolean
		@param	pipe: Flag, set if the output streams should be piped
		@type	outputOnFail: Boolean
		@param	outputOnFail: Flag, set if the output streams should be piped on failed test
		"""
		opts = {'mode': TestSuiteMode.BreakOnFail, 'pipe':None, 'outputOnFail':None, 'timeout':None, 'DUT':None}
		opts.update(options)
		self.setMode(opts['mode'])
		"""The test suite mode"""
		self.testList = [t for t in tests]
		self.setAll(pipe = opts['pipe'], out = opts['outputOnFail'], timeout = opts['timeout'])
		self.setDUT(opts['DUT'])
		"""The collection of tests"""
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
		self.assertions = 0
		"""The total number of tests that caused an assertion"""
		self.segfaults = 0
		"""The total number of tests that caused a segfault""" 
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
		
	def setDUT(self, DUT = None):
		"""Define the 'Device under Test'"""
		if DUT is not None:
			self.DUT = DUT
			for t in self.testList:
				t.DUT = DUT
		else:
			self.DUT = None
		
	def addTest(self, test):
		"""
		Adds a test to the suite
		
		@type	test: Test
		@param	test: Test to add
		"""
		self.testList.append(test)
		
	def getTests(self):
		return self.testList
		
	def setAll(self, state=TestState.Waiting, pipe=None, out=None, diff=None, timeout=None, linesep=None): 
		for t in self.testList:
			t.state = state
			if pipe is not None:
				t.pipe = pipe
			if out is not None:
				t.outputOnFail = out
			if diff is not None:
				t.diff = diff
			if timeout is not None:
				t.timeout = timeout
			if linesep is not None:
				t.linesep = linesep
		
	def runSelected(self, tests):
		for test in tests:
			yield self.runOne(test)
		
	def _getTests(self, tests):
		if len(tests) == 0:
			tests = xrange(len(self))
		for t in tests:
			if t < len(self):
				yield self[t]
		raise StopIteration()
		
	def run(self, quiet = False, tests = []):
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
		for t in self._getTests(tests):
			self.count = self.count + 1 
			self.lastResult = t.run()
			if t.descr is not None:
				logger.log("{}[{:03}] {} - {}: {}".format(TermColor.colorText("Test", TermColor.Purple), self.count, t.name, t.descr, TestState.toString(t.state)))
			else:
				logger.log("{}[{:03}] {}: {}".format(TermColor.colorText("Test", TermColor.Purple), self.count, t.name, TestState.toString(t.state)))
			logger.flush(quiet)
			if self.lastResult == TestState.Success:
				self.success += 1
			elif self.lastResult == TestState.Fail:
				self.failed += 1
			elif self.lastResult == TestState.Error:
				self.error += 1
			elif self.lastResult == TestState.Timeout:
				self.timedout += 1
			elif self.lastResult == TestState.SegFault:
				self.segfaults += 1
			elif self.lastResult == TestState.Assertion:
				self.assertions += 1
			yield t
			if self.lastResult != TestState.Disabled:
				if (self.mode == TestSuiteMode.BreakOnFail) and (self.lastResult != TestState.Success):
					break
				if (self.mode == TestSuiteMode.BreakOnError) and (self.lastResult == TestState.Error):
					break
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
		if (self.lastResult != TestState.InfoOnly):
			logger.log("I ran {} out of {} tests in total".format(self.count, len(self.testList)))
			fails = self.count - self.success
			logger.log(TermColor.colorText("\tSuccess: {}".format(self.success), TermColor.Green))
			if (self.failed > 0):
				logger.log(TermColor.colorText("\tFailed: {}".format(self.failed), TermColor.Red))
			if (self.error > 0):
				logger.log(TermColor.colorText("\tErrors: {}".format(self.error), TermColor.Yellow))
			if (self.assertions > 0):
				logger.log(TermColor.colorText("\tAssertions: {}".format(self.assertions), TermColor.Yellow))
			if (self.segfaults > 0):
				logger.log(TermColor.colorText("\tSegFaults: {}".format(self.segfaults), TermColor.Yellow))
				
			if (self.timedout > 0):
				logger.log(TermColor.colorText("\tTimeouts: {}".format(self.timedout), TermColor.Purple))
			# A little bit of fun
			if (self.success == len(self)):
				logger.log("\tCongratulations, you passed all tests!")
				logger.log("\tgrep yourself a refreshing " + TermColor.colorText("Beer", TermColor.Yellow, style = TermColor.Bold))
				logger.log("")
				logger.log("              \033[1;37m,%%%%.\033[0m")
				logger.log("              \033[1;37mi\033[36m====\033[1;37mi\033[1;36m_\033[0m")
				logger.log("              \033[1;36m|\033[1;33m####\033[36m| |\033[0m")
				logger.log("              \033[1;36m|\033[1;33m####\033[36m|-'\033[0m")
				logger.log("              \033[1;36m`-==-'\033[0m")
				logger.log("")
			elif (self.success == 0 and self.failed > 0):
				logger.log("\tWhat is wrong with you, not even a single test?")
			elif fails > 0:
				if self.assertions/fails > 0.6:
					logger.log("\tYou do realise that assertions do not replace error handling?")
				elif self.assertions/fails > 0.3:
					logger.log("\tWe're a bit lazy with calling environments, aren't we?")
				if self.segfaults/fails > 0.6:
					logger.log("\tMay the CPU-Gods have mercy with that poor memory management units soul!")
				elif self.segfaults/fails > 0.3:
					logger.log("\tYou know, memory garbage doesn't collects itself?!")
		return self.calcRate()
		
	def __str__(self):
		self.toString(prefix = "")
		
	def toString(self, prefix = ""):
		s = prefix+'[\n'
		for test in self:
			s += prefix
			s += test.toString("\t")
			s += ",\n"
		s += prefix + ']\n'