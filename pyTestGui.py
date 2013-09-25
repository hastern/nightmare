#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import time
import itertools

from pyTest import TestState
from pyTestSuite import TestSuiteMode
from pyTestRunner import TestRunner
from pyTestUtils import TermColor
from pyTestEditForm import TestEditForm

import wx
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
		CheckListCtrlMixin.__init__(self)
		ListCtrlAutoWidthMixin.__init__(self)

class TestRunnerGui(wx.App):
	"""Graphical User Interface"""
	modes = ["Continuous", "Halt of Fail", "Halt on Error"]
	filetypes = [('PyTest', 'py'), ('All Files', '*')]
	
	def suiteSave(self, fn):
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
		if self.runner.DUT is not None:
			fHnd.write("# Device Under Test\n")
			fHnd.write("DUT = \"{}\"\n\n".format(os.path.relpath(self.runner.DUT)))
		fHnd.write("# Test definitions\n")
		fHnd.write("suite = [\n")
		tests = []
		for test in self.runner.getSuite().getTests():
			tests.append("\t{}".format(test.toString()))
		fHnd.write(",\n".join(tests))
		fHnd.write("\n]\n")
		fHnd.close()
		
	def saveSuite(self):
		""" Savedialog execution before saving the suite"""
		fname = self.saveFileDialog(fileTypes = TestRunnerGui.filetypes)
		if fname is not None:
			self.suiteSave(fname)
	
	def loadSuite(self):
		""" Load a testsuite"""
		fname = self.loadFileDialog(fileTypes = TestRunnerGui.filetypes)
		if fname is not None:
			self.edtFile.SetValue(os.path.relpath(fname))
			self.runner.file = fname
			self.updateFromRunner()
			
	def updateFromRunner(self):
		self.runner.loadSuite()
		self.lstTests.DeleteAllItems()
		self.applyToList(self.runner.getSuite().getTests(), self.insertTest )
		self.edtDUT.SetValue(str(self.runner.DUT))
		self.edtTests.SetValue(str(self.runner.countTests()))
		self.grpMode.SetSelection(self.runner.getSuite().mode)
			
	def selectDut(self):
		"""Show filedialog and set the result as DUT"""
		fname = self.loadFileDialog(fileTypes = TestRunnerGui.filetypes)
		if fname is not None:
			self.runner.setDUT(fname)
			self.edtDUT.SetValue(os.path.relpath(fname))
		
			
	def applyToList(self, l, f, gauge = True):
		cnt = self.runner.countTests()
		if gauge:
			self.prgGauge.SetRange(cnt-1)
			self.prgGauge.SetValue(0)
		lastIdx = 0
		for idx, test in itertools.izip(xrange(cnt), l):
			lastIdx = idx
			if gauge:
				self.prgGauge.SetValue(idx)
				self.prgGauge.Update()
			if idx < self.lstTests.GetItemCount()-1:
				self.lstTests.SetStringItem(idx+1, 2, "RUNNING")
				self.lstTests.Update()
			f(idx, test)
			self.lstTests.Update()
		for i in  range(lastIdx+1,len(self.runner.getSuite())):
			self.lstTests.SetStringItem(i, 2, "CANCELED")
				
	def insertTest(self, idx, test):
		"""Insert a new test into the test-list
		
		@type	idx: int
		@param 	idx: The index of the test to add
		@type	test: pyTestCore.test.Test
		@param 	test: The test to add
		"""
		self.lstTests.InsertStringItem(idx, test.name)
		self.lstTests.CheckItem(idx)
		self.updateTest(idx, test)
		
	def updateTest(self, idx, test):
		"""Update the information on one test in the test-list
		
		@type	idx: int
		@param 	idx: The index of the test to change
		@type	test: pyTestCore.test.Test
		@param 	test: The test to change
		"""
		if test.state == TestState.Error:
			self.lstTests.CheckItem(idx, False)
			self.lstTests.SetItemBackgroundColour(idx, 'yellow')
		elif test.state == TestState.Success:
			self.lstTests.SetItemBackgroundColour(idx, 'green')
		elif test.state == TestState.Fail:
			self.lstTests.SetItemBackgroundColour(idx, 'red')
		elif test.state == TestState.Timeout:
			self.lstTests.SetItemBackgroundColour(idx, 'purple')
		elif test.state == TestState.Waiting:
			self.lstTests.SetItemBackgroundColour(idx, 'white')
		elif test.state == TestState.Disabled:
			self.lstTests.SetItemBackgroundColour(idx, 'gray')
		TermColor.active = False
		self.lstTests.SetStringItem(idx, 0, test.name)
		self.lstTests.SetStringItem(idx, 1, test.descr)
		self.lstTests.SetStringItem(idx, 2, TestState.toString(test.state))
		TermColor.active = True
		
	def setTestState(self, test, idx, state):
		"""Update the state of one test, but only if the test is not enabled"""
		if test.state != TestState.Disabled:
			test.state = state
		self.updateTest(idx, test)
	
	def onListCheck(self, idx, flag):
		"""Eventhandler for changes on the checkboxes in the list"""
		test = self.runner.getSuite()[idx]
		test.state = TestState.Waiting if flag else TestState.Disabled
		self.updateTest(idx, test)
		
	def run(self, testIdx = None):
		"""Run tests"""
		if testIdx is None:
			self.applyToList(self.runner.getSuite().getTests(), lambda i,t: self.setTestState(t, i, TestState.Waiting), gauge = False)
			self.applyToList(self.runner.run(doYield = True) , self.updateTest)
		else:
			test = self.runner.getSuite().runOne(testIdx)
			self.updateTest(testIdx, test)
			
	def addTest(self):
		newIdx = len(self.runner.getSuite())
		newTest = self.runner.addTest()
		self.insertTest(newIdx, newTest)
		TestEditForm(self.wHnd, newIdx, newTest, self.runner, self).show()
	
	def selectTest(self, event):
		idx = event.GetIndex()
		test = self.runner.getSuite()[idx]
		TestEditForm(self.wHnd, idx, test, self.runner, self).show()
	
	def __init__(self):
		"""Initialise the gui"""
		wx.App.__init__(self, redirect = False, useBestVisual=True)
		self.runner = TestRunner()
		self.runner.quiet = True
		self.runner.parseArgv()
		self.runner.mode = TestSuiteMode.Continuous
		
	def messageDialog(self, message, caption=wx.MessageBoxCaptionStr, style=wx.OK | wx.ICON_INFORMATION):
		dial = wx.MessageDialog(None, message, caption, style)
		return dial.ShowModal()
		
	def fileDialog(self, mode, message, fileTypes = None, dir = wx.EmptyString):
		if fileTypes is None:
			wc = wx.FileSelectorDefaultWildcardStr
		else:
			wc = "|".join([ descr + " (*" +  ext + ")|*" + ext for descr, ext in fileTypes])
		diag = wx.FileDialog(self.wHnd, message, defaultDir=dir, wildcard = wc, style=mode)
		diag.ShowModal()
		return os.path.join(diag.Directory,diag.Filename) if diag.Filename != "" else None
		
	def displayError(self, message, caption = 'An error occured'):
		return self.messageDialog(message, caption, wx.OK | wx.ICON_ERROR) == wx.OK
		
	def displayInformation(self, message, caption='Warning'):
		return self.messageDialog(message, caption, wx.OK | wx.ICON_INFORMATION) == wx.OK
		
	def displayQuestion(self, message, caption='Question'):
		return self.messageDialog(message, caption, wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
		
	def loadFileDialog(self, message = "Load File", fileTypes = None, dir = wx.EmptyString):
		return self.fileDialog(mode = wx.FD_OPEN, message= message, fileTypes = fileTypes, dir = dir)
		
	def saveFileDialog(self, message = "Save File", fileTypes = None, dir = wx.EmptyString):
		return self.fileDialog(mode = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, message= message, fileTypes = fileTypes, dir = dir)
		
	def buildWindow(self):
		"""Creates the window with all its components"""
		self.wHnd = wx.Frame(None, wx.DEFAULT_FRAME_STYLE, title = "pyTest GUI", size=(500,400))
		self.SetTopWindow(self.wHnd)
		
		panel = wx.Panel(self.wHnd)
		sizer = wx.GridBagSizer(3, 3)
		# Create Controls
		self.btnLoad   = wx.Button(panel, label="Load", id = wx.ID_OPEN)
		self.btnSave   = wx.Button(panel, label="Save", id = wx.ID_SAVE)
		self.lblDUT    = wx.StaticText(panel, label="DUT")
		self.lblFile   = wx.StaticText(panel, label="File")
		self.lblTests  = wx.StaticText(panel, label="Tests")
		self.edtDUT    = wx.TextCtrl(panel)
		self.edtFile   = wx.TextCtrl(panel)
		self.edtTests  = wx.TextCtrl(panel)
		self.btnSelect = wx.Button(panel, label="...")
		self.btnAdd    = wx.Button(panel, label="+", id = wx.ID_ADD)
		self.grpMode   = wx.RadioBox(panel, choices=TestRunnerGui.modes, style=wx.RA_VERTICAL)
		self.prgGauge  = wx.Gauge(panel)
		self.btnRun    = wx.Button(panel, label="Run")
		self.lstTests  = CheckListCtrl(panel)
		# Feature for wxPython 2.9 (currently in development)
		if hasattr(self.btnSave, 'SetBitmap'):
			self.btnSave.SetBitmap(wx.ART_FILE_OPEN)
			self.btnLoad.SetBitmap(wx.ART_FILE_LOAD)
		# Disable TextCtrl
		self.edtFile.Disable()
		self.edtTests.Disable()
		# Insert Columns into list and hook up the checkboxes
		self.lstTests.InsertColumn(0, 'Test', width=140)
		self.lstTests.InsertColumn(1, 'Description', width=220)
		self.lstTests.InsertColumn(2, 'State', width=100)
		self.lstTests.OnCheckItem = self.onListCheck 
		# Create Layout
		sizer.Add(self.btnLoad,   pos=(0,0), span=(3,1), border=5, flag=wx.LEFT|wx.TOP|wx.EXPAND)
		sizer.Add(self.btnSave,   pos=(0,1), span=(3,1), border=5, flag=wx.TOP|wx.EXPAND)
		sizer.Add(self.lblDUT,    pos=(0,2), span=(1,1), border=5, flag=wx.RIGHT|wx.LEFT|wx.TOP|wx.EXPAND)
		sizer.Add(self.lblFile,   pos=(1,2), span=(1,1), border=5, flag=wx.RIGHT|wx.LEFT|wx.EXPAND)
		sizer.Add(self.lblTests,  pos=(2,2), span=(1,1), border=5, flag=wx.RIGHT|wx.LEFT|wx.EXPAND)
		sizer.Add(self.edtDUT,    pos=(0,3), span=(1,1), border=5, flag=wx.TOP|wx.EXPAND)
		sizer.Add(self.edtFile,   pos=(1,3), span=(1,1), border=5, flag=wx.EXPAND)
		sizer.Add(self.edtTests,  pos=(2,3), span=(1,1), border=5, flag=wx.EXPAND)
		sizer.Add(self.btnSelect, pos=(0,4), span=(1,1), border=5, flag=wx.TOP)
		sizer.Add(self.btnAdd,    pos=(2,4), span=(1,1), border=5, )
		sizer.Add(self.grpMode,   pos=(0,5), span=(3,1), border=5, flag=wx.TOP|wx.RIGHT|wx.EXPAND)
		sizer.Add(self.prgGauge,  pos=(3,0), span=(1,5), border=5, flag=wx.LEFT|wx.EXPAND)
		sizer.Add(self.btnRun,    pos=(3,5), span=(1,1), border=5, flag=wx.RIGHT|wx.EXPAND)
		sizer.Add(self.lstTests,  pos=(4,0), span=(1,6), border=5, flag=wx.ALL|wx.EXPAND)
		sizer.AddGrowableCol(3)
		sizer.AddGrowableRow(4)
		panel.SetSizerAndFit(sizer)
		# Hook up window events
		self.wHnd.Bind(wx.EVT_BUTTON, lambda e:self.loadSuite(), id = self.btnLoad.GetId())
		self.wHnd.Bind(wx.EVT_BUTTON, lambda e:self.saveSuite(), id = self.btnSave.GetId())
		self.wHnd.Bind(wx.EVT_BUTTON, lambda e:self.run(), id = self.btnRun.GetId())
		self.wHnd.Bind(wx.EVT_BUTTON, lambda e:self.selectDut(), id = self.btnSelect.GetId())
		self.wHnd.Bind(wx.EVT_BUTTON, lambda e:self.addTest(), id = self.btnAdd.GetId())
		self.wHnd.Bind(wx.EVT_RADIOBOX, lambda e:self.runner.__setattr__("mode",self.grpMode.GetSelection()), id = self.grpMode.GetId())
		self.wHnd.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
		self.wHnd.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
		self.lstTests.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.selectTest, id = self.lstTests.GetId())
		# Change the DUT after the user left the associated TextCtrl
		self.edtDUT.Bind(wx.EVT_KILL_FOCUS, lambda e: self.runner.setDUT(self.edtDUT.GetValue()), id = self.edtDUT.GetId())
		#
		self.updateFromRunner()

	def OnKeyDown(self, e):
		"""Handler for key events"""
		if e.CmdDown and e.GetUniChar() == 'q':
			self.Destroy()
		e.Skip()
		
	def OnCloseWindow(self, e):
		"""Handler to make sure the window doesn't gets close by accident"""
		ret = self.displayQuestion('Are you sure, you want to quit?')
		if ret == wx.ID_YES:
			self.wHnd.Destroy()
		else:
			e.Veto()
	
	def show(self):
		self.wHnd.Centre()
		self.wHnd.Show()
		self.MainLoop()
		
if __name__ == "__main__":
	gui = TestRunnerGui()
	gui.buildWindow()
	gui.show()