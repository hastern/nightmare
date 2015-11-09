#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ---------- ---------- ---------- ---------- ---------- ---------- ---------- #
# @file pyTestGui                                                              #
# @author Hanno Sternberg <hanno@almostintelligent.de>                         #
#                                                                              #
# This file contains the GUI classes.                                          #
#                                                                              #
# @license MIT                                                                 #
#                                                                              #
# This software is licensed under the MIT License                              #
#                                                                              #
# Copyright (c) 2012-2015 Hanno Sternberg                                      #
#                                                                              #
# Permission is hereby granted, free of charge, to any person obtaining a copy #
# of this software and associated documentation files (the "Software"), to     #
# deal in the Software without restriction, including without limitation the   #
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or  #
# sell copies of the Software, and to permit persons to whom the Software is   #
# furnished to do so, subject to the following conditions:                     #
#                                                                              #
# The above copyright notice and this permission notice shall be included in   #
# all copies or substantial portions of the Software.                          #
#                                                                              #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR   #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,     #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER       #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING      #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS #
# IN THE SOFTWARE.                                                             #
# ---------- ---------- ---------- ---------- ---------- ---------- ---------- #

import os
import sys
import time
import threading
import itertools

from pyTest import TestState
from pyTestSuite import TestSuiteMode
from pyTestRunner import TestRunner
from pyTestUtils import TermColor, logger
from pyTestEditForm import TestEditForm

import wx
import wx.html
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin


class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)


class LogWindow(wx.Frame):
    """Window to show the log output"""
    def __init__(self, parent, prevLog=[]):
        wx.Frame.__init__(self, parent, size=(600, 400))
        self.log = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.TE_READONLY)
        map(self.add, prevLog)
        id = wx.NewId()
        self.acceleratorTable = wx.AcceleratorTable([
            (wx.ACCEL_CTRL,  ord('l'), id),
            (wx.ACCEL_CTRL,  ord('w'), id),
        ])
        self.SetAcceleratorTable(self.acceleratorTable)
        self.Bind(wx.EVT_CLOSE, lambda e: self.Hide())
        self.Bind(wx.EVT_MENU, lambda e: self.Hide(), id=id)

    def add(self, line):
        self.log.AppendText(line + "\n")


class TestRunnerGui(wx.App):
    """Graphical User Interface"""
    modes = ["Continuous", "Halt on Fail", "Halt on Error"]
    benchtypes = [('nightmare', 'py'), ('All Files', '*')]
    duttypes = [('All Files', '*'), ('Executables', '*.exe')]

    def suiteSave(self, fn):
        self.runner.saveToFile(fn)

    def loadIcon(self, frame):
        try:
            if sys.platform == 'win32':
                exeName = sys.executable
                icon = wx.Icon(exeName + ';0', wx.BITMAP_TYPE_ICO)
                frame.SetIcon(icon)
        except:
            pass

    def saveSuite(self):
        """ Savedialog execution before saving the suite"""
        fname = self.saveFileDialog(fileTypes=TestRunnerGui.benchtypes)
        if fname is not None:
            self.suiteSave(fname)

    def loadSuite(self):
        """ Load a testsuite"""
        fname = self.loadFileDialog(fileTypes=TestRunnerGui.benchtypes)
        if fname is not None:
            self.edtFile.SetValue(os.path.relpath(fname))
            self.runner.options['bench'] = fname
            self.updateFromRunner()

    def updateFromRunner(self):
        self.runner.loadSuite()
        self.lstTests.DeleteAllItems()
        self.applyToList(self.runner.getSuite().getTests(), self.insertTest)
        self.edtDUT.SetValue(str(self.runner.options['dut']))
        self.edtTests.SetValue(str(self.runner.countTests()))
        self.grpMode.SetSelection(self.runner.getSuite().mode)

    def selectDut(self):
        """Show filedialog and set the result as DUT"""
        fname = self.loadFileDialog(fileTypes=TestRunnerGui.duttypes)
        if fname is not None:
            self.runner.setDUT(fname)
            self.edtDUT.SetValue(os.path.relpath(fname))

    def applyToList(self, l, f, gauge=True):
        cnt = self.runner.countTests()
        if gauge:
            self.prgGauge.SetRange(cnt - 1)
            self.prgGauge.SetValue(0)
        lastIdx = 0
        for idx, test in itertools.izip(xrange(cnt), l):
            lastIdx = idx
            if gauge:
                self.prgGauge.SetValue(idx)
                self.prgGauge.Update()
            if idx < self.lstTests.GetItemCount() - 1:
                self.lstTests.SetStringItem(idx + 1, 2, "RUNNING")
                self.lstTests.Update()
            f(idx, test)
            self.lstTests.Update()
        for i in range(lastIdx + 1, len(self.runner.getSuite())):
            self.lstTests.SetStringItem(i, 2, "CANCELED")

    def insertTest(self, idx, test):
        """Insert a new test into the test-list

        @type    idx: int
        @param     idx: The index of the test to add
        @type    test: pyTestCore.test.Test
        @param     test: The test to add
        """
        self.lstTests.InsertStringItem(idx, test.name)
        self.lstTests.CheckItem(idx)
        self.updateTest(idx, test)

    def updateTest(self, idx, test):
        """Update the information on one test in the test-list

        @type    idx: int
        @param     idx: The index of the test to change
        @type    test: pyTestCore.test.Test
        @param     test: The test to change
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

    def __runthread(self, testIdx=None):
        """Run tests"""
        if testIdx is None:
            self.applyToList(self.runner.getSuite().getTests(), lambda i, t: self.setTestState(t, i, TestState.Waiting), gauge=False)
            self.applyToList(self.runner.run(), self.updateTest)
        else:
            test, = self.runner.getSuite().run(tests=[testIdx])
            self.updateTest(testIdx, test)
        self.testthread = None
        """Unset yourself for further processing"""

    def run(self, testIdx=None):
        """start running thread"""
        if self.testthread is None:
            self.testthread = threading.Thread(target=self.__runthread, args=(testIdx,))
            self.testthread.start()
        else:
            self.displayError("Test is already running!")

    def addTest(self):
        newIdx = len(self.runner.getSuite())
        newTest = self.runner.addTest()
        self.insertTest(newIdx, newTest)
        self.editTest(newIdx)

    def selectTest(self, event):
        self.editTest(event.GetIndex())

    def editTest(self, testIdx):
        test = self.runner.getSuite()[testIdx]
        if self.editForm is None:
            self.editForm = TestEditForm(self.wHnd, testIdx, test, self.runner, self)
            self.loadIcon(self.editForm)
        else:
            self.editForm.updateTest(testIdx)
        self.editForm.Show()

    def __init__(self):
        """Initialise the gui"""
        wx.App.__init__(self, redirect=False, useBestVisual=True)
        logger.logListener = self.addLog
        TermColor.active = False
        self.wHnd = None
        self.testthread = None
        self.editForm = None
        self.log = []
        self.logForm = None
        self.runner = TestRunner()
        self.runner.options['quiet'] = True
        self.runner.parseArgv()
        self.runner.options['mode'] = TestSuiteMode.Continuous

    def addLog(self, line):
        self.log.append(line)
        if self.logForm is not None:
            self.logForm.add(line)

    def showLog(self):
        if self.logForm is None:
            self.logForm = LogWindow(self.wHnd, self.log)
        if self.logForm.IsShown():
            self.logForm.Hide()
        else:
            self.logForm.Show()

    def messageDialog(self, message, caption=wx.MessageBoxCaptionStr, style=wx.OK | wx.ICON_INFORMATION):
        dial = wx.MessageDialog(None, message, caption, style)
        return dial.ShowModal()

    def fileDialog(self, mode, message, fileTypes=None, dir=wx.EmptyString):
        if fileTypes is None:
            wc = wx.FileSelectorDefaultWildcardStr
        else:
            wc = " | ".join([descr + " (*" + ext + ") | *" + ext for descr, ext in fileTypes])
        diag = wx.FileDialog(self.wHnd, message, defaultDir=dir, wildcard=wc, style=mode)
        diag.ShowModal()
        return os.path.join(diag.Directory, path=diag.Filename) if diag.Filename != "" else None

    def displayError(self, message, caption='An error occured'):
        return self.messageDialog(message, caption, wx.OK | wx.ICON_ERROR) == wx.OK

    def displayInformation(self, message, caption='Warning'):
        return self.messageDialog(message, caption, wx.OK | wx.ICON_INFORMATION) == wx.OK

    def displayQuestion(self, message, caption='Question'):
        return self.messageDialog(message, caption, wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

    def loadFileDialog(self, message="Load File", fileTypes=None, dir=wx.EmptyString):
        return self.fileDialog(mode=wx.FD_OPEN, message=message, fileTypes=fileTypes, dir=dir)

    def saveFileDialog(self, message="Save File", fileTypes=None, dir=wx.EmptyString):
        return self.fileDialog(mode=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, message=message, fileTypes=fileTypes, dir=dir)

    def buildWindow(self):
        """Creates the window with all its components"""
        self.wHnd = wx.Frame(None, style=wx.DEFAULT_FRAME_STYLE, title="nightmare GUI-Modus", size=(600, 400))
        self.SetTopWindow(self.wHnd)
        self.loadIcon(self.wHnd)

        panel = wx.Panel(self.wHnd)
        sizer = wx.GridBagSizer(3, 3)
        # Create Controls
        self.btnLoad   = wx.Button(panel, label="Load", id=wx.ID_OPEN)
        self.btnSave   = wx.Button(panel, label="Save", id=wx.ID_SAVE)
        self.lblDUT    = wx.StaticText(panel, label="DUT")
        self.lblFile   = wx.StaticText(panel, label="File")
        self.lblTests  = wx.StaticText(panel, label="Tests")
        self.edtDUT    = wx.TextCtrl(panel)
        self.edtFile   = wx.TextCtrl(panel)
        self.edtTests  = wx.TextCtrl(panel)
        self.btnSelect = wx.Button(panel, label="...")
        self.btnAdd    = wx.Button(panel, label=" + ", id=wx.ID_ADD)
        self.grpMode   = wx.RadioBox(panel, choices=TestRunnerGui.modes, style=wx.RA_VERTICAL)
        self.prgGauge  = wx.Gauge(panel)
        self.btnRun    = wx.Button(panel, label="Run")
        self.lstTests  = CheckListCtrl(panel)
        # Feature for wxPython 2.9 (currently in development)
        if hasattr(self.btnSave, 'SetBitmap'):
            self.btnSave.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE))
            self.btnLoad.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN))
        # Disable TextCtrl
        self.edtFile.Disable()
        self.edtTests.Disable()
        # Insert Columns into list and hook up the checkboxes
        self.lstTests.InsertColumn(0, 'Test', width=140)
        self.lstTests.InsertColumn(1, 'Description', width=220)
        self.lstTests.InsertColumn(2, 'State', width=100)
        self.lstTests.OnCheckItem = self.onListCheck
        # Create Layout
        sizer.Add(self.btnLoad,   pos=(0, 0), span=(3, 1), border=5, flag=wx.LEFT | wx.TOP | wx.EXPAND)
        sizer.Add(self.btnSave,   pos=(0, 1), span=(3, 1), border=5, flag=wx.TOP | wx.EXPAND)
        sizer.Add(self.lblDUT,    pos=(0, 2), span=(1, 1), border=5, flag=wx.RIGHT | wx.LEFT | wx.TOP | wx.EXPAND)
        sizer.Add(self.lblFile,   pos=(1, 2), span=(1, 1), border=5, flag=wx.RIGHT | wx.LEFT | wx.EXPAND)
        sizer.Add(self.lblTests,  pos=(2, 2), span=(1, 1), border=5, flag=wx.RIGHT | wx.LEFT | wx.EXPAND)
        sizer.Add(self.edtDUT,    pos=(0, 3), span=(1, 1), border=5, flag=wx.TOP | wx.EXPAND)
        sizer.Add(self.edtFile,   pos=(1, 3), span=(1, 1), border=5, flag=wx.EXPAND)
        sizer.Add(self.edtTests,  pos=(2, 3), span=(1, 1), border=5, flag=wx.EXPAND)
        sizer.Add(self.btnSelect, pos=(0, 4), span=(1, 1), border=5, flag=wx.TOP)
        sizer.Add(self.btnAdd,    pos=(2, 4), span=(1, 1), border=5, )
        sizer.Add(self.grpMode,   pos=(0, 5), span=(3, 1), border=5, flag=wx.TOP | wx.RIGHT | wx.EXPAND)
        sizer.Add(self.prgGauge,  pos=(3, 0), span=(1, 5), border=5, flag=wx.LEFT | wx.EXPAND)
        sizer.Add(self.btnRun,    pos=(3, 5), span=(1, 1), border=5, flag=wx.RIGHT | wx.EXPAND)
        sizer.Add(self.lstTests,  pos=(4, 0), span=(1, 6), border=5, flag=wx.ALL | wx.EXPAND)
        sizer.AddGrowableCol(3)
        sizer.AddGrowableRow(4)
        panel.SetSizerAndFit(sizer)
        # Hook up window events
        self.wHnd.Bind(wx.EVT_BUTTON, lambda e: self.loadSuite(), id=self.btnLoad.GetId())
        self.wHnd.Bind(wx.EVT_BUTTON, lambda e: self.saveSuite(), id=self.btnSave.GetId())
        self.wHnd.Bind(wx.EVT_BUTTON, lambda e: self.run(), id=self.btnRun.GetId())
        self.wHnd.Bind(wx.EVT_BUTTON, lambda e: self.selectDut(), id=self.btnSelect.GetId())
        self.wHnd.Bind(wx.EVT_BUTTON, lambda e: self.addTest(), id=self.btnAdd.GetId())
        self.wHnd.Bind(wx.EVT_RADIOBOX, lambda e: self.runner.options.__setitem__("mode", self.grpMode.GetSelection()), id=self.grpMode.GetId())
        self.wHnd.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.lstTests.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.selectTest, id=self.lstTests.GetId())
        # Some Shortcuts
        shortcuts = [
            (wx.ACCEL_CTRL,  ord('q'), self.OnCloseWindow),
            (wx.ACCEL_CTRL,  ord('r'), lambda e:self.run()),
            (wx.ACCEL_CTRL,  ord('o'), lambda e:self.loadSuite()),
            (wx.ACCEL_CTRL,  ord('d'), lambda e:self.selectDut()),
            (wx.ACCEL_CTRL,  ord('n'), lambda e:self.addTest()),
            (wx.ACCEL_CTRL,  ord('e'), lambda e:self.addTest()),
            (wx.ACCEL_CTRL,  ord('l'), lambda e:self.showLog()),
        ]
        entries = []
        for special, key, func in shortcuts:
            id = wx.NewId()
            entries.append((special, key, id))
            self.wHnd.Bind(wx.EVT_MENU, func, id=id)
        self.acceleratorTable = wx.AcceleratorTable(entries)
        self.wHnd.SetAcceleratorTable(self.acceleratorTable)
        # Change the DUT after the user left the associated TextCtrl
        self.edtDUT.Bind(wx.EVT_KILL_FOCUS, lambda e: self.runner.setDUT(self.edtDUT.GetValue()), id=self.edtDUT.GetId())
        #
        self.updateFromRunner()

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
