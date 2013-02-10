#!/usr/bin/env python

from Tkinter import *
from ttk import *

from testEditForm import TestEditForm
		
class TestCreateButton(Button):
	"""Button for creating a new test"""
	def __init__(self, parent, cb, caption, runner):
		"""
		Initialise the test edit button
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	cb: Callback
		@param	cb: Callback for grid update
		
		@type	caption: String
		@param	caption: The caption of the button
		
		@type	test: Test
		@param	test: The test to be edited
		
		@type 	n: int
		@param	n: The number of the test
		"""
		Button.__init__(self, parent, text=caption, command=self.createTest)
		self._cb = cb
		self._runner = runner
		
	def createTest(self):
		"""Eventhandler for button click"""
		test = Test()
		self._runner.getSuite().getTests().append(test)
		if self._cb is not None:
			self._cb()
		TestEditForm(self, len(self._runner.getSuite().getTests()), test, self._runner)

