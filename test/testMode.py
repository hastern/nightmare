#!/usr/bin/env python

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