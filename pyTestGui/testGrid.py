#!/usr/bin/env python

from Tkinter import *
from ttk import *

from pyTestCore.testState import TestState

from testEditButton import TestEditButton

class TestRow(Frame):
	"""The TestRow represents a single row inside the Testgrid"""
	def __init__(self, parent, runner, n, test):
		"""
		Initialise the row
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	runner: TestRunner
		@param	runner: The testrunner holding the test data
		
		@type 	n: int
		@param	n: Number of the test
		
		@type	test: Test
		@param	test: The testdata
		"""
		Frame.__init__(self, parent)
		self._runner = runner
		self._num = n
		self._test = test
		self._state = IntVar(self)
		self._state.set(False)
		Style().configure("Success.TLabel", foreground = "#000", background = "#0D0");
		Style().configure("Fail.TLabel", foreground = "#FFF", background = "#D00");
		Style().configure("Error.TLabel", foreground = "#000", background = "#DD0");
		Style().configure("Waiting.TLabel", foreground = "#000", background = "#FFF");
		Style().configure("Disabled.TLabel", foreground = "#888", background = "#000");
		self._edtBtn = TestEditButton(self, runner, "Edit", test, self._num)
		self._edtBtn.pack(side=LEFT)
		self._checkBtn = Checkbutton(self, command=self.clickCheck, variable=self._state)
		self._checkBtn.pack(side=LEFT)
		self._lblNum = Label(self, text="{:02}".format(n), width=3)
		self._lblNum.pack(side=LEFT)
		self._lblName = Label(self, text=test.name, width=20)
		self._lblName.pack(side=LEFT)
		self._lblDescr = Label(self, text=test.descr, width=40)
		self._lblDescr.pack(side=LEFT, expand=1, fill=X)
		
	def update(self):
		"""Updates the widgets"""
		if self._test.state == TestState.Success:
			self._lblNum.config(style="Success.TLabel")
			self._lblName.config(style="Success.TLabel")
			self._lblDescr.config(style="Success.TLabel")
		elif self._test.state == TestState.Fail:
			self._lblNum.config(style="Fail.TLabel")
			self._lblName.config(style="Fail.TLabel")
			self._lblDescr.config(style="Fail.TLabel")
		elif self._test.state == TestState.Error:
			self._lblNum.config(style="Error.TLabel")
			self._lblName.config(style="Error.TLabel")
			self._lblDescr.config(style="Error.TLabel")
		elif self._test.state == TestState.Waiting:
			self._lblNum.config(style="Waiting.TLabel")
			self._lblName.config(style="Waiting.TLabel")
			self._lblDescr.config(style="Waiting.TLabel")
		elif self._test.state == TestState.Disabled:
			self._lblNum.config(style="Disabled.TLabel")
			self._lblName.config(style="Disabled.TLabel")
			self._lblDescr.config(style="Disabled.TLabel")
	
		if self._test.state == TestState.Disabled:
			self._state.set(False)
		else:
			self._state.set(True)
		
	def clickCheck(self):
		"""Eventhandler for checkbutton click"""
		if self._test.state == TestState.Disabled:
			self._test.state = TestState.Waiting
			self._state.set(False)
		else:
			self._test.state = TestState.Disabled
			self._state.set(True)
		self.update()
		
		
class TestGrid(Frame):
	"""A TestGrid displays all tests and their result."""
	def __init__(self, parent, runner):
		"""
		Initialise the grid
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	runner: TestRunner
		@param	runner: The testrunner holding the test data
		"""
		Frame.__init__(self, parent)
		self._runner = runner
		self._rows = []
		self.createHead()
		self._visible = (0,9)
	
	def toggleAll(self):
		"""Eventhandler for header checkbutton"""
		self._runner.getSuite().setAll(disabled=self._toggleAllVar.get())
		self.update()
	
	def createHead(self):
		"""Create the head of the grid"""
		head = Frame(self)
		Button(head, text="+", command=self.scrollUp, width=3).pack(side=LEFT)
		Button(head, text="-", command=self.scrollDown, width=3).pack(side=LEFT)
		self._toggleAllVar = IntVar(head)
		self._toggleAllVar.set(False)
		self._toggleAll = Checkbutton(head, onvalue=False, offvalue=True, command=self.toggleAll, variable=self._toggleAllVar)
		self._toggleAll.pack(side=LEFT)
		Label(head, text="#", width=3).pack(side=LEFT)
		Label(head, text="Name", width=20).pack(side=LEFT)
		Label(head, text="Description", width=40).pack(side=LEFT, expand=1, fill=X)
		head.pack(side=TOP, expand=1, fill=BOTH, anchor=NW)
	
	def scrollUp(self):
		"""Scroll the grid one row up"""
		lower, upper = self._visible
		if upper < len(self._rows)-1:
			lower = lower + 1
			upper = upper + 1
			self._visible = lower, upper
			self.scroll()
	
	def scrollDown(self):
		"""Scroll the grid one row down"""
		lower, upper = self._visible
		if lower > 0:
			lower = lower - 1
			upper = upper - 1
			self._visible = lower, upper
			self.scroll()
	
	def addRow(self, test):
		"""
		Add a row to the gridd
		
		@type 	test: Test
		@param	test: Test with data for the row
		"""
		row = TestRow(self, self._runner, len(self._rows)+1, test)
		self._rows.append(row)
	
	def update(self):
		"""Update the grid"""
		i = 0
		for t in self._runner.getSuite().getTests():
			if i >= len(self._rows):
				self.addRow(t)
			else:
				self._rows[i].update()
			i = i + 1
			
	def scroll(self):
		"""Scroll through the grid"""
		lower, upper = self._visible
		if upper > len(self._rows):
			upper = len(self._rows)-1
		for row in self._rows:
			row.pack_forget()
		for i in range(lower, upper+1):
			self._rows[i].pack(side=TOP, expand=1, fill=BOTH, anchor=NW)
			
	def clear(self):
		"""remove all rows from the grid"""
		for row in self._rows:
			row.pack_forget()
			row.destroy()
		self._rows = []