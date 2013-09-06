#!/usr/bin/env python


from Tkinter import *
from ttk import *

from pyTestCore.test import Test
from pyTestCore.testRunner import TestRunner
from testRunButton import TestRunButton
from testSaveButton import TestSaveButton

class TestEditForm(Toplevel):
	"""Form for editing one test"""
	def __init__(self, parent, n, test, runner, gui):
		"""
		Initialises the form
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	n: int 
		@param	n: Number of the test
		
		@type	test: Test
		@param 	test: The test to be edited
		
		@type	runner: TestRunner
		@param	runner: The test runner
		"""
		Toplevel.__init__(self, parent)
		self.title("Edit test {}".format(n))
		self._test = test
		# Variables
		self._varname = StringVar(self, self._test.name)
		self._vardescr = StringVar(self, self._test.descr)
		self._varcmd = StringVar(self, self._test.cmd)
		self._varret = StringVar(self, self._test.retCode)
		self._varexpRet = StringVar(self, self._test.expectRetCode)
		# Widgets
		Label(self, text="Name").grid(row=0, column=0, columnspan=2)
		Entry(self, width=50, textvariable=self._varname).grid(row=1, column=0, columnspan=2, sticky=N+E+S+W)
		Label(self, text="Description").grid(row=0, column=2, columnspan=4)
		Entry(self, width=70, textvariable=self._vardescr).grid(row=1, column=2, columnspan=4, sticky=N+E+S+W)
		Label(self, text="Command").grid(row=2, column=0, columnspan=6)
		Entry(self, width=120, textvariable=self._varcmd).grid(row=3, column=0, columnspan=6, sticky=N+E+S+W)
		Label(self, text="Expected stdout").grid(row=4, column=0, columnspan=3)
		self._expOut = Text(self, width=50, height=5)
		self._expOut.grid(row=5, column=0, columnspan=3, sticky=N+E+S+W)
		Label(self, text="stdout").grid(row=4, column=3, columnspan=3)
		self._out = Text(self, width=50, height=5)
		self._out.grid(row=5, column=3, columnspan=3, sticky=N+E+S+W)
		Label(self, text="Expected Stderr").grid(row=6, column=0, columnspan=3)
		self._expErr = Text(self, width=50, height=5)
		self._expErr.grid(row=7, column=0, columnspan=3, sticky=N+E+S+W)
		Label(self, text="stderr").grid(row=6, column=3, columnspan=3)
		self._err = Text(self, width=50, height=5)
		self._err.grid(row=7, column=3, columnspan=3, sticky=N+E+S+W)
		Label(self, text="Expected Returncode").grid(row=8, column=0, columnspan=2)
		Entry(self, width=30, textvariable=self._varexpRet).grid(row=9, column=0, columnspan=2, sticky=N+E+S+W)
		Label(self, text="Returncode").grid(row=8, column=2, columnspan=2)
		Entry(self, width=30, textvariable=self._varret, state=DISABLED).grid(row=9, column=2, columnspan=2, sticky=N+E+S+W)
		TestRunButton(self, gui, "Run", n-1, runner).grid(row=9, column=4)
		TestSaveButton(self, test, gui).grid(row=9, column=5)
		# Fill data
		if not isLambda(self._test.expectStdout) and self._test.expectStdout is not None:
			self._expOut.insert(INSERT, str(self._test.expectStdout))
		if not isLambda(self._test.expectStderr) and self._test.expectStderr is not None:
			self._expErr.insert(INSERT, str(self._test.expectStderr))
		if self._test.output != "":
			self._out.insert(INSERT, str(self._test.output))
		if self._test.error != "":
			self._err.insert(INSERT, str(self._test.error))
