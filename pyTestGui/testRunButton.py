#!/usr/bin/env python

from Tkinter import *
from ttk import *

class TestRunButton(Button):
	"""Button to start one test run"""
	def __init__(self, parent, caption, n, runner, finishCB, mode):
		"""
		Initialise the button
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	n: int 
		@param	n: Number of the test
		
		@type	caption: String
		@param 	caption: Caption of the button
		
		@type	runner: TestRunner
		@param	runner: The test runner
		"""
		Button.__init__(self, parent, text=caption, command=self.runTest, width=7)
		self._num = n
		self._runner = runner
		self._cb = finishCB
		self._mode = mode
		
	def runTest(self):
		"""Run the test(s)"""
		self._runner.mode = self._mode.get()
		if self._num == -1:
			self._runner.start(self._cb)
		else:
			self._runner.start(self._cb, self._num)

