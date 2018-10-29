#!/usr/bin/env python3
# -*- coding:utf - 8 -*-

# ---------- ---------- ---------- ---------- ---------- ---------- ---------- #
# @file editform.py                                                            #
# @author Hanno Sternberg <hanno@almostintelligent.de>                         #
#                                                                              #
# This file holds the form for editing a single test in the GUI.               #
#                                                                              #
# @license MIT                                                                 #
#                                                                              #
# This software is licensed under the MIT License                              #
#                                                                              #
# Copyright (c) 2012 - 2018 Hanno Sternberg                                    #
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

from .case import Test
from .runner import TestRunner

import wx


class TestEditForm(wx.Frame):
    """Form for editing one test"""

    def __init__(self, parent, idx, test, runner, gui):
        """
        Initialises the form

        @type    idx: int
        @param    idx: Number of the test

        @type    test: pyTestcore.test.Test
        @param     test: The test to be edited

        @type    runner: pyTestRunner.TestRunner
        @param    runner: The test runner

        @type    gui: pyTestGui.TestRunnerGui
        @param    gui: The gui
        """
        wx.Frame.__init__(self, parent, size=(600, 400))
        # self.title("Edit test {}".format(test.name))
        self.test = test
        self.runner = runner
        self.gui = gui
        self.idx = idx
        self.Centre()

        self.panel = wx.Panel(self)
        self.sizer = wx.GridBagSizer(3, 3)
        # Create components
        self.lblName = wx.StaticText(self.panel, label="Name")
        self.edtName = wx.TextCtrl(self.panel)
        self.lblDescr = wx.StaticText(self.panel, label="Description")
        self.edtDescr = wx.TextCtrl(self.panel)
        self.lblCommand = wx.StaticText(self.panel, label="Command")
        self.edtCommand = wx.TextCtrl(self.panel)
        self.lblTimeout = wx.StaticText(self.panel, label="Timeout")
        self.edtTimeout = wx.TextCtrl(self.panel)
        self.line1 = wx.StaticLine(self.panel)
        # Expectations Box
        self.boxExpect = wx.StaticBox(self.panel, label="Expectations")
        self.szrExpect = wx.StaticBoxSizer(self.boxExpect, wx.VERTICAL)
        self.lblExpOut = wx.StaticText(self.panel, label="Stdout")
        self.edtExpOut = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE)
        self.lblExpErr = wx.StaticText(self.panel, label="Stderr")
        self.edtExpErr = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE)
        self.lblExpCode = wx.StaticText(self.panel, label="Returncode")
        self.edtExpCode = wx.TextCtrl(self.panel)
        # Results Box
        self.boxResult = wx.StaticBox(self.panel, label="Results")
        self.szrResult = wx.StaticBoxSizer(self.boxResult, wx.VERTICAL)
        self.lblResOut = wx.StaticText(self.panel, label="Stdout")
        self.edtResOut = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.lblResErr = wx.StaticText(self.panel, label="Stderr")
        self.edtResErr = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.lblResCode = wx.StaticText(self.panel, label="Returncode")
        self.edtResCode = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
        # Buttons
        self.line2 = wx.StaticLine(self.panel)
        self.btnCancel = wx.Button(self.panel, label="Cancel", id=wx.ID_CANCEL)
        self.btnPrevious = wx.Button(self.panel, label="Previous")
        self.btnNext = wx.Button(self.panel, label="Next")
        self.btnRun = wx.Button(self.panel, label="Run")
        self.btnSave = wx.Button(self.panel, label="Save", id=wx.ID_SAVE)
        # Layout - Main Components
        self.sizer.Add(self.lblName, pos=(0, 0), span=(1, 1), border=5, flag=wx.TOP | wx.LEFT)
        self.sizer.Add(self.edtName, pos=(0, 1), span=(1, 1), border=5, flag=wx.TOP | wx.RIGHT | wx.EXPAND)
        self.sizer.Add(self.lblDescr, pos=(0, 2), span=(1, 1), border=5, flag=wx.TOP | wx.LEFT)
        self.sizer.Add(self.edtDescr, pos=(0, 3), span=(1, 5), border=5, flag=wx.TOP | wx.RIGHT | wx.EXPAND)
        self.sizer.Add(self.lblCommand, pos=(1, 0), span=(1, 1), border=5, flag=wx.LEFT)
        self.sizer.Add(self.edtCommand, pos=(1, 1), span=(1, 5), border=5, flag=wx.RIGHT | wx.EXPAND)
        self.sizer.Add(self.lblTimeout, pos=(1, 6), span=(1, 1), border=5, flag=wx.LEFT | wx.EXPAND)
        self.sizer.Add(self.edtTimeout, pos=(1, 7), span=(1, 1), border=5, flag=wx.RIGHT | wx.EXPAND)
        self.sizer.Add(self.line1, pos=(2, 0), span=(1, 8), border=5, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND)
        self.sizer.Add(self.szrExpect, pos=(3, 0), span=(1, 4), border=5, flag=wx.LEFT | wx.EXPAND)
        self.sizer.Add(self.szrResult, pos=(3, 4), span=(1, 4), border=5, flag=wx.RIGHT | wx.EXPAND)
        self.sizer.Add(self.line2, pos=(4, 0), span=(1, 8), border=5, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND)
        self.sizer.Add(self.btnCancel, pos=(5, 0), span=(1, 1), border=5, flag=wx.LEFT | wx.BOTTOM | wx.EXPAND)
        self.sizer.Add(self.btnPrevious, pos=(5, 1), span=(1, 1), border=5, flag=wx.BOTTOM | wx.EXPAND)
        self.sizer.Add(self.btnNext, pos=(5, 2), span=(1, 2), border=5, flag=wx.BOTTOM | wx.EXPAND)
        self.sizer.Add(self.btnRun, pos=(5, 6), span=(1, 1), border=5, flag=wx.BOTTOM | wx.EXPAND)
        self.sizer.Add(self.btnSave, pos=(5, 7), span=(1, 1), border=5, flag=wx.RIGHT | wx.BOTTOM | wx.EXPAND)
        # Layout - Expectations and Result Boxes
        self.szrExpect.Add(self.lblExpOut, 0, border=5, flag=wx.TOP | wx.LEFT)
        self.szrExpect.Add(self.edtExpOut, 1, border=5, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND)
        self.szrExpect.Add(self.lblExpErr, 0, border=5, flag=wx.LEFT)
        self.szrExpect.Add(self.edtExpErr, 1, border=5, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND)
        self.szrExpect.Add(self.lblExpCode, 0, border=5, flag=wx.LEFT)
        self.szrExpect.Add(self.edtExpCode, 0, border=5, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND)
        self.szrResult.Add(self.lblResOut, 0, border=5, flag=wx.TOP | wx.LEFT)
        self.szrResult.Add(self.edtResOut, 1, border=5, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND)
        self.szrResult.Add(self.lblResErr, 0, border=5, flag=wx.LEFT)
        self.szrResult.Add(self.edtResErr, 1, border=5, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND)
        self.szrResult.Add(self.lblResCode, 0, border=5, flag=wx.LEFT)
        self.szrResult.Add(self.edtResCode, 0, border=5, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND)
        #
        self.sizer.AddGrowableCol(1)
        self.sizer.AddGrowableCol(3)
        self.sizer.AddGrowableCol(4)
        self.sizer.AddGrowableCol(5)
        self.sizer.AddGrowableRow(3)
        self.panel.SetSizer(self.sizer)
        # Some Shortcuts
        self.acceleratorTable = wx.AcceleratorTable(
            [
                (wx.ACCEL_CTRL, ord("w"), self.btnCancel.GetId()),
                (wx.ACCEL_CTRL, ord("s"), self.btnSave.GetId()),
                (wx.ACCEL_CTRL, ord("r"), self.btnRun.GetId()),
                (wx.ACCEL_NORMAL, wx.WXK_PAGEUP, self.btnPrevious.GetId()),
                (wx.ACCEL_NORMAL, wx.WXK_PAGEDOWN, self.btnNext.GetId()),
            ]
        )
        self.SetAcceleratorTable(self.acceleratorTable)
        # Event handling
        self.Bind(wx.EVT_BUTTON, lambda e: self.Hide(), id=self.btnCancel.GetId())
        self.Bind(wx.EVT_BUTTON, lambda e: self.run(), id=self.btnRun.GetId())
        self.Bind(wx.EVT_BUTTON, lambda e: self.save(), id=self.btnSave.GetId())
        self.Bind(wx.EVT_BUTTON, lambda e: self.updateTest(self.idx - 1), id=self.btnPrevious.GetId())
        self.Bind(wx.EVT_BUTTON, lambda e: self.updateTest(self.idx + 1), id=self.btnNext.GetId())
        self.Bind(wx.EVT_CLOSE, lambda e: self.Hide())
        # Shortcut bindings
        self.Bind(wx.EVT_MENU, lambda e: self.Hide(), id=self.btnCancel.GetId())
        self.Bind(wx.EVT_MENU, lambda e: self.run(), id=self.btnRun.GetId())
        self.Bind(wx.EVT_MENU, lambda e: self.save(), id=self.btnSave.GetId())
        self.Bind(wx.EVT_MENU, lambda e: self.updateTest(self.idx - 1), id=self.btnPrevious.GetId())
        self.Bind(wx.EVT_MENU, lambda e: self.updateTest(self.idx + 1), id=self.btnNext.GetId())
        # Fill test data
        self.updateValues()

    def run(self):
        self.save()
        self.gui.run(self.idx)
        self.updateValues()

    def updateTest(self, newIdx):
        self.idx = min(max(0, newIdx), len(self.gui.runner.getSuite()) - 1)
        if self.idx == 0:
            self.btnPrevious.Disable()
        else:
            self.btnPrevious.Enable()
        if self.idx == len(self.gui.runner.getSuite()) - 1:
            self.btnNext.Disable()
        else:
            self.btnNext.Enable()
        self.test = self.gui.runner.getSuite()[self.idx]
        self.updateValues()

    def updateValues(self):
        self.edtName.SetValue(self.test.name)
        self.edtDescr.SetValue(self.test.descr if self.test.descr is not None else "")
        self.edtCommand.SetValue(str(self.test.cmd) if self.test.cmd is not None else "")
        self.edtTimeout.SetValue(str(self.test.timeout))
        self.edtExpOut.SetValue(str(self.test.expectStdout) if self.test.expectStdout is not None else "")
        self.edtExpErr.SetValue(str(self.test.expectStderr) if self.test.expectStderr is not None else "")
        self.edtExpCode.SetValue(str(self.test.expectRetCode) if self.test.expectRetCode is not None else "")
        self.edtResOut.SetValue(self.test.output)
        self.edtResErr.SetValue(self.test.error)
        self.edtResCode.SetValue(str(self.test.retCode))

    def save(self):
        self.test.name = self.edtName.GetValue()
        self.test.descr = self.edtDescr.GetValue()
        self.test.cmd = self.edtCommand.GetValue()
        self.test.timeout = float(self.edtTimeout.GetValue())
        self.test.expectStdout = self.edtExpOut.GetValue() if self.edtExpOut.GetValue().strip() != "" else None
        self.test.expectStderr = self.edtExpErr.GetValue() if self.edtExpErr.GetValue().strip() != "" else None
        self.test.expectRetCode = self.edtExpCode.GetValue() if self.edtExpCode.GetValue().strip() != "" else None
        self.gui.updateTest(self.idx, self.test)
