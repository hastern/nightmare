#!/usr/bin/env python

import os

from Tkinter import *
from ttk import *
import tkFileDialog as fileDiag

from pyTestCore.testMode import TestSuiteMode
from pyTestCore.testRunner import TestRunner

from labeledEntry import LabeledEntry
from fileLoaderButton import FileLoaderButton
from testCreateButton import TestCreateButton
from testRunButton import TestRunButton
from testGrid import TestGrid

class TestRunnerGui():
	"""Graphical User Interface"""
	
	def _handleSuiteLoad(self, fn):
		"""
		Load a testsuite
		
		@type	fn: String
		@param 	fn: The filename
		"""
		dut = os.path.abspath(self._DUT.get())
		os.chdir(os.path.dirname(fn))
		self._DUT.set(os.path.relpath(dut))
		#print os.getcwd()
		self._runner.suite = self._suite.get()
		self._runner.file = os.path.relpath(fn)
		self._runner.mode = self._mode.get()
		self._runner.loadSuite()
		if self._runner.DUT is not None:
			self._DUT.set(self._runner.DUT)
		self._tests.set(self._runner.countTests())
		self._filename.set(os.path.relpath(fn))
		self.dataGrid.clear()
		self.dataGrid.update()
		self.dataGrid.scroll()
		
	def _handleSelectDUT(self, fn):
		"""
		Select a device under test
		
		@type	fn: String
		@param 	fn: The device under test (DUT)
		"""
		self._runner.setDUT(fn)
		self._DUT.set(os.path.relpath(fn))
		
	def _handleSuiteSave(self, fn):
		"""
		Save the testsuite into a file
		
		@type	fn: String
		@param 	fn: The filename
		"""
		fHnd = open(fn,"w")
		fHnd.write("#!/usr/bin/env python\n\n")
		fHnd.write("# pyTest - Testbench\n")
		fHnd.write("# Saved at {}\n".format(time.strftime("%H:%M:%S")))
		fHnd.write("# \n\n")
		#fHnd.write("# Author: {}\n".format())
		if self._runner.DUT is not None:
			fHnd.write("# Device Under Test\n")
			fHnd.write("DUT = \"{}\"\n\n".format(os.path.relpath(self._runner.DUT)))
		fHnd.write("# Test definitions\n")
		fHnd.write("{} = [\n".format(self._suite.get()))
		tests = []
		for test in self._runner.getSuite().getTests():
			tests.append("\t{}".format( test.toString()))
		fHnd.write(",\n".join(tests))
		fHnd.write("\n]\n")
		fHnd.close()
	
	def __init__(self):
		"""Initialise the gui"""
		self._runner = TestRunner()
		self._runner.parseArgv()
		self._whnd = Tk()
		self._whnd.title("pyTest GUI")
		
		# Frames
		cfgFrame = Frame(self._whnd)
		suiteFrame = LabelFrame(cfgFrame, text="Suite")
		suiteInfoFrame = Frame(suiteFrame)
		actionFrame = LabelFrame(cfgFrame, text="Mode")
		
		# Variables
		self._suite = StringVar(suiteInfoFrame, self._runner.suite)
		self._tests = StringVar(suiteInfoFrame, self._runner.testCount)
		self._filename = StringVar(suiteInfoFrame, "")
		self._DUT = StringVar(suiteInfoFrame, "")
		self._mode = IntVar(actionFrame, TestSuiteMode.BreakOnFail)
		
		# Components
		self.dataGrid = TestGrid(self._whnd, self._runner)
		self._suiteFile = LabeledEntry(suiteInfoFrame, lbl="File", var=self._filename)
		self._suiteFile.entry.configure(state=DISABLED)
		self._suiteName = LabeledEntry(suiteInfoFrame, lbl="Name", var=self._suite)
		self._suiteTests = LabeledEntry(suiteInfoFrame, lbl="Tests", var=self._tests)
		self._suiteTests.entry.configure(state=DISABLED)
		self._DUTName = LabeledEntry(suiteInfoFrame, lbl="DUT", var=self._DUT)
		self._DUTName.entry.configure(state=DISABLED) 
		self._loadSuite = FileLoaderButton(suiteFrame, "Load Testsuite", self._handleSuiteLoad, filetypes=[("Python Script","*.py"), ("pyTest Testbench","*.test.py")], defaultExt=".test.py")
		self._saveSuite = FileLoaderButton(suiteFrame, "Save Testsuite", self._handleSuiteSave, fileDiag.asksaveasfilename, filetypes=[("Python Script","*.py"), ("pyTest Testbench","*.test.py")], defaultExt=".test.py")
		self._addTest = TestCreateButton(suiteFrame, self.dataGrid.update, "Add Test", self._runner)
		self._loadDUT = FileLoaderButton(actionFrame, "Select DUT", self._handleSelectDUT)
		self._runBtn = TestRunButton(actionFrame, caption="Run All", n=-1, runner=self._runner, finishCB=lambda: self.dataGrid.update() and self.dataGrid.scroll(), mode=self._mode)
		# Pack all widgets
		
		self._loadDUT.pack(side=LEFT, expand=1, fill=Y, anchor=NW)
		self._runBtn.pack(side=LEFT, expand=1, fill=Y, anchor=NW)
		Radiobutton(actionFrame, text="Continuous", variable=self._mode, value=TestSuiteMode.Continuous).pack()
		Radiobutton(actionFrame, text="Halt on Fail", variable=self._mode, value=TestSuiteMode.BreakOnFail).pack()
		Radiobutton(actionFrame, text="Halt on Error", variable=self._mode, value=TestSuiteMode.BreakOnError).pack()
		
		self._loadSuite.pack(side=LEFT, expand=1, fill=Y, anchor=NW)
		self._saveSuite.pack(side=LEFT, expand=1, fill=Y, anchor=NW)
		self._DUTName.pack(side=TOP, expand=1, fill=X, anchor=NW)
		self._suiteFile.pack(side=TOP, expand=1, fill=X, anchor=NW)
		self._suiteName.pack(side=TOP, expand=1, fill=X, anchor=NW)
		self._suiteTests.pack(side=TOP, expand=1, fill=X, anchor=NW)
		suiteInfoFrame.pack(side=LEFT, expand=1, fill=X, anchor=NW)
		self._addTest.pack(side=LEFT, expand=1, fill=Y, anchor=NW)
		suiteFrame.pack(side=LEFT, anchor=NW)
		actionFrame.pack(side=RIGHT, anchor=NE)
		cfgFrame.pack(side=TOP, expand=1, fill=X, anchor=N)
		# create and pack datagrid
		self.dataGrid.pack(side=TOP, expand=1, fill=X, anchor=NW)
		
		self._whnd.mainloop()