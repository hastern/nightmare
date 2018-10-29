#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ---------- ---------- ---------- ---------- ---------- ---------- ---------- #
# @file suite.py                                                               #
# @author Hanno Sternberg <hanno@almostintelligent.de>                         #
#                                                                              #
# This file contains the TestSuite for grouping Tests together.                #
#                                                                              #
# @license MIT                                                                 #
#                                                                              #
# This software is licensed under the MIT License                              #
#                                                                              #
# Copyright (c) 2012-2018 Hanno Sternberg                                      #
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

from typing import List

from enum import Enum

from .case import Test, TestState
from .utils import logger, TermColor


class TestSuiteMode(Enum):
    """Enumeration for testsuite modes """

    BreakOnFail = 0
    """Halt on first failed test"""
    BreakOnError = 1
    """Halt on first erroneous test"""
    Continuous = 2
    """Run all test"""

    def __str__(self):
        return {
            TestSuiteMode.BreakOnFail: "Break On Fail",
            TestSuiteMode.Continuous: "Continuous",
            TestSuiteMode.BreakOnError: "Break on Error",
        }.get(self, "Unknown mode")

    def __int__(self):
        return int(self.value)


class TestSuite:
    """A testsuite is a collection of tests"""

    def __init__(self, *tests: Test, **options):
        self.options = {
            "mode": TestSuiteMode.BreakOnFail,
            "pipe": None,
            "outputOnFail": None,
            "timeout": None,
            "DUT": None,
            "ignoreEmptyLines": None,
            "commands": False,
            "pipeLimit": None,
        }
        self.options.update(options)
        self.setMode(self.options["mode"])
        """The test suite mode"""
        self.testList = [t for t in tests]
        self.setAll(
            pipe=self.options["pipe"],
            out=self.options["outputOnFail"],
            timeout=self.options["timeout"],
            ignoreEmptyLines=self.options["ignoreEmptyLines"],
            pipeLimit=self.options["pipeLimit"],
        )
        self.setDUT(self.options["DUT"])
        """The collection of tests"""
        self.success = 0
        """The number of successful tests"""
        self.failed = 0
        """The number of failed tests"""
        self.count = 0
        """A counter for the executed tests"""
        self.error = 0
        """The number of errors occured during the testrun"""
        self.timedout = 0
        """The total number of timed out tests"""
        self.assertions = 0
        """The total number of tests that caused an assertion"""
        self.segfaults = 0
        """The total number of tests that caused a segfault"""
        self.lastResult = TestState.Waiting
        """The result of the last test"""
        self.rate = 0
        """The successrate of the testrun"""

    def __len__(self):
        return len(self.testList)

    def __iter__(self):
        for test in self.testList:
            yield test

    def __getitem__(self, key):
        return self.testList[key]

    def __setitem(self, key, val):
        self.testList[key] = val

    def getRate(self):
        """Returns the success rate"""
        return self.rate

    def setMode(self, mode):
        """
        Sets the mode of the testsuite
        """
        self.mode = mode

    def setDUT(self, DUT=None):
        """Define the 'Device under Test'"""
        if DUT is not None:
            self.DUT = DUT
            for t in self.testList:
                t.DUT = DUT
        else:
            self.DUT = None

    def addTest(self, test: Test):
        self.testList.append(test)

    def getTests(self):
        return self.testList

    def setAll(
        self,
        state=TestState.Waiting,
        pipe=None,
        out=None,
        diff=None,
        timeout=None,
        linesep=None,
        ignoreEmptyLines=None,
        pipeLimit=None,
    ):
        """
        Applies the suite options to all tests in the suite.
        """
        for t in self.testList:
            t.state = state
            if pipe is not None:
                t.pipe = pipe
            if out is not None:
                t.outputOnFail = out
            if diff is not None:
                t.diff = diff
            if timeout is not None:
                t.timeout = timeout
            if linesep is not None:
                t.linesep = linesep
            if ignoreEmptyLines is not None:
                t.ignoreEmptyLines = ignoreEmptyLines
            if pipeLimit is not None:
                t.pipeLimit = pipeLimit

    def _getTests(self, tests):
        if len(tests) == 0:
            tests = range(len(self))
        for t in tests:
            if t < len(self):
                yield self[t]

    def run(self, quiet=False, tests: List[int] = []):
        """
        Runs the tests in the suite.

        If no tests are selected, all tests will be run.
        """
        self.success = 0
        self.failed = 0
        self.count = 0
        self.error = 0
        self.lastResult = TestState.Waiting
        for t in self._getTests(tests):
            self.lastResult = t.run()
            if t.descr is not None:
                logger.log(f"{TermColor.colorText('Test', TermColor.Purple)}[{self.count: 03}] {t.name} - {t.descr}: {t.state}")
            else:
                logger.log(f"{TermColor.colorText('Test', TermColor.Purple)}[{self.count: 03}] {t.name}: {t.state}")
            if self.options["commands"]:
                logger.log(f" --> {t.cmd}", showTime=False)
            logger.flush(quiet)
            if self.lastResult in [TestState.Success, TestState.Clean]:
                self.success += 1
            elif self.lastResult == TestState.Fail:
                self.failed += 1
            elif self.lastResult == TestState.Error:
                self.error += 1
            elif self.lastResult == TestState.Timeout:
                self.timedout += 1
            elif self.lastResult == TestState.SegFault:
                self.segfaults += 1
            elif self.lastResult == TestState.Assertion:
                self.assertions += 1
            self.count = self.count + 1
            yield t
            if self.lastResult != TestState.Disabled:
                if (self.mode == TestSuiteMode.BreakOnFail) and (self.lastResult != TestState.Success):
                    break
                if (self.mode == TestSuiteMode.BreakOnError) and (self.lastResult == TestState.Error):
                    break

    def calcRate(self):
        """
        Calculate the success rate of a test run.
        """
        self.rate = float(self.success) / float(len(self)) * 100
        return self.rate

    def stats(self, quiet=False):
        """
        Displays the statistics of the test run on stdout.

        Might add a (possibly mean) comment on the overall result.
        """
        if self.lastResult != TestState.InfoOnly:
            logger.log(f"I ran {self.count} out of {len(self.testList)} tests in total")
            fails = self.count - self.success
            logger.log(TermColor.colorText(f"\tSuccess: {self.success}", TermColor.Green))
            if self.failed > 0:
                logger.log(TermColor.colorText(f"\tFailed: {self.failed}", TermColor.Red))
            if self.error > 0:
                logger.log(TermColor.colorText(f"\tErrors: {self.error}", TermColor.Yellow))
            if self.assertions > 0:
                logger.log(TermColor.colorText(f"\tAssertions: {self.assertions}", TermColor.Yellow))
            if self.segfaults > 0:
                logger.log(TermColor.colorText(f"\tSegFaults: {self.segfaults}", TermColor.Yellow))
            if self.timedout > 0:
                logger.log(TermColor.colorText(f"\tTimeouts: {self.timedout}", TermColor.Purple))
            # A little bit of fun
            if self.success == len(self) and self.count > 3:
                logger.log("\tCongratulations, you passed all tests!")
                logger.log(
                    "\t`grep` yourself a refreshing " + TermColor.colorText("Beer", TermColor.Yellow, style=TermColor.Bold)
                )
                logger.log("")
                logger.log("              \033[1;37m,%%%%.\033[0m")
                logger.log("              \033[1;37mi\033[36m====\033[1;37mi\033[1;36m_\033[0m")
                logger.log("              \033[1;36m|\033[1;33m####\033[36m| |\033[0m")
                logger.log("              \033[1;36m|\033[1;33m####\033[36m|-'\033[0m")
                logger.log("              \033[1;36m`-==-'\033[0m")
                logger.log("")
            elif self.success == 0 and self.count > 3 and self.failed > 0:
                logger.log("\tWhat is wrong with you, not even a single test?")
            elif fails > 0 and self.count > 3:
                if self.assertions / fails > 0.6:
                    logger.log("\tYou do realise that assertions do not replace error handling?")
                elif self.assertions / fails > 0.3:
                    logger.log("\tWe're a bit lazy with calling environments, aren't we?")
                if self.segfaults / fails > 0.6:
                    logger.log("\tMay the CPU-Gods have mercy with that poor memory management units soul!")
                elif self.segfaults / fails > 0.3:
                    logger.log("\tYou know, memory garbage doesn't collect itself?!")
        return self.calcRate()

    def __str__(self):
        self.toString(prefix="")

    def toString(self, prefix=""):
        s = prefix + "[\n"
        for test in self:
            s += prefix
            s += test.toString("\t")
            s += ",\n"
        s += prefix + "]\n"
