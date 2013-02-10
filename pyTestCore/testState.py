#!/usr/bin/env python

from utils import TermColor

class TestState:
	#__slots__ = ["Success", "Fail", "Error", "Waiting", "Disabled", "InfoOnly", "Timeout"]

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