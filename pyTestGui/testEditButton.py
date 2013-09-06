#!/usr/bin/env python

from Tkinter import *
from ttk import *

from testEditForm import TestEditForm

class TestEditButton(Button):
	"""Button for editing a test"""
	def __init__(self, parent, runner, gui, caption, test, n):
		"""
		Initialise the test edit button
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	runner: TestRunner
		@param	runner: The TestRunner instance
		
		@type	caption: String
		@param	caption: The caption of the button
		
		@type	test: Test
		@param	test: The test to be edited
		
		@type 	n: int
		@param	n: The number of the test
		"""
		Button.__init__(self, parent, text=caption, command=self.editTest, width=7)
		self._test = test
		self._num = n
		self._runner = runner
		self._gui = gui
		
	def editTest(self):
		TestEditForm(self, self._num, self._test, self._runner, self._gui)

