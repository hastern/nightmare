#!/usr/bin/env python

from Tkinter import *
from ttk import *

class TestSaveButton(Button):
	"""Button to the save the test data"""
	def __init__(self, parent, test, callback):
		"""
		Initialise the button
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	callback: Callback
		@param	callback: Update callback function
		
		@type	test: Test
		@param	test: The test data
		"""
		Button.__init__(self, parent, text="Save", command=self.saveTest, width=7)
		self._test = test
		self._parentForm = parent
		self._cb = callback
		
	def saveTest(self):
		"""Save the test"""
		name = str(self._parentForm._varname.get())
		descr = str(self._parentForm._vardescr.get())
		cmd = str(self._parentForm._varcmd.get())
		out = str(self._parentForm._expOut.get(1.0, 'end')).strip()
		err = str(self._parentForm._expErr.get(1.0, 'end')).strip()
		ret = str(self._parentForm._varexpRet.get()).strip()
		self._test.name = name
		self._test.descr = descr
		self._test.cmd = cmd
		if out != "":
			self._test.expectStdout = out
		else:
			self._test.expectStdout = None
		if err != "":
			self._test.expectStderr = err
		else:
			self._test.expectStderr = None
		if ret != "":
			self._test.expectRetCode = ret
		else:
			self._test.expectRetCode = None
		if self._cb is not None:
			self._cb()
		