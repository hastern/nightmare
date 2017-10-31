#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ---------- ---------- ---------- ---------- ---------- ---------- ---------- #
# @file pyTest                                                                 #
# @author Hanno Sternberg <hanno@almostintelligent.de>                         #
#                                                                              #
# This file contains the class defining a test case.                           #
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
import re
import sys
import signal
import difflib
import subprocess

from threading import Thread

from utils import isLambda, TermColor, logger


class TestState:
    """The test is waiting for execution"""
    Success = 0
    """The test was successful"""
    Fail = 1
    """The test has failed"""
    Error = 2
    """The test has produced an error"""
    Assertion = 3
    """The test has produced a assertion"""
    SegFault = 4
    """The test has produced a segmentation fault"""
    InfoOnly = 5
    """Display only the test information"""
    Timeout = 6
    """The test has timed out"""
    Waiting = 7
    """The test awaits execution"""
    Disabled = 8
    """Disables the test"""
    Clean = 10
    """BadWord come clean"""
    BadWord = 11
    """A BadWord was detected"""

    @staticmethod
    def toString(state):
        """
        Converts the enumeration value into a string

        @type    state: int
        @param    state: Enumeration value
        """
        if state == TestState.Waiting:
            return TermColor.colorText(" WAITING ", TermColor.White)
        if state == TestState.Success:
            return TermColor.colorText(" SUCCESS ", fg=TermColor.Black, bg=TermColor.Green)
        if state == TestState.Fail:
            return TermColor.colorText(" FAIL ", fg=TermColor.Black, bg=TermColor.Red)
        if state == TestState.Error:
            return TermColor.colorText(" ERROR ", fg=TermColor.Black, bg=TermColor.Red, style=TermColor.Bold)
        if state == TestState.SegFault:
            return TermColor.colorText(" SEGFAULT ", fg=TermColor.Black, bg=TermColor.Yellow)
        if state == TestState.Assertion:
            return TermColor.colorText(" ASSERTION ", fg=TermColor.Black, bg=TermColor.Yellow, style=TermColor.Bold)
        if state == TestState.InfoOnly:
            return TermColor.colorText(" INFO ", TermColor.White)
        if state == TestState.Timeout:
            return TermColor.colorText(" TIMEOUT ", TermColor.Purple)
        if state == TestState.Disabled:
            return TermColor.colorText(" DISABLED ", TermColor.Blue)
        if state == TestState.Clean:
            return TermColor.colorText(" CLEAN ", fg=TermColor.White, bg=TermColor.Green, style=TermColor.Bold)
        if state == TestState.BadWord:
            return TermColor.colorText(" BADWORD ", fg=TermColor.Yellow, bg=TermColor.Red, style=TermColor.Bold)
        return TermColor.colorText(" UNKNOWN ", TermColor.Yellow)


class Command:
    """Command execution"""
    def __init__(self, cmd, binary=False):
        """
        Initialises the command

        @type    cmd: str
        @param    cmd: Command
        """
        self.cmd = cmd
        self.proc = None
        self.thread = None
        self.out = ""
        self.err = ""
        self.ret = 0
        self.killed = False
        self.binary = binary

    def commandFunc(self):
        """command to be run in the thread"""
        self.proc = subprocess.Popen(self.cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=not self.binary, shell=True, cwd=os.getcwd())
        self.out, self.err = self.proc.communicate()
        self.ret = self.proc.wait()

    def execute(self, timeout):
        """
        executes the command

        @type    timeout: float
        @param    timeout: Timeout in seconds
        """
        self.thread = Thread(target=self.commandFunc)
        self.thread.start()
        self.thread.join(timeout)
        if self.proc is not None and self.proc.poll() is None:
            if sys.platform == "win32":
                subprocess.Popen(['taskkill', '/F', '/T', '/PID', str(self.proc.pid)]).communicate()
            else:
                childProc = int(subprocess.check_output("pgrep -P {}".format(self.proc.pid), shell=True, universal_newlines=True).strip())
                os.kill(childProc, signal.SIGKILL)
                if self.proc.poll() is None:
                    os.kill(self.proc.pid, signal.SIGTERM)
                # os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
            return TestState.Timeout
        return TestState.Success


class Expectation(object):
    def __call__(self):
        return True


class ExpectFile(Expectation):
    def __init__(self, fname):
        self.exp = open(fname, "rb").read()

    def __call__(self, out):
        return self.exp == out

    def __str__(self):
        return self.exp


class Stringifier(object):
    def __init__(self, expectation):
        self.exp = expectation.encode("utf8", errors="ignore")

    def __call__(self, output):
        out = output.encode("utf8", errors="ignore")
        return self.exp.strip().splitlines(), out.strip().splitlines()

    def __str__(self):
        return self.exp


class StringifiedFile(Stringifier):
    def __init__(self, fname):
        Stringifier.__init__(self, open(fname).read())


class CompareFiles(Expectation):
    def __init__(self, expect_file, out_file):
        self.expect = expect_file
        self.out = out_file

    def __call__(self, whatever):
        # Since we want to compare files, actual output is ignored
        expect = open(self.expect, "rb").read()
        out = open(self.out, "rb").read()
        return expect == out


class Test(object):
    """A single test"""

    def __init__(self,
                 DUT=None,
                 name="",
                 description="",
                 command=None,
                 stdout=None,
                 stderr=None,
                 returnCode=None,
                 timeout=5.0,
                 outputOnFail=False,
                 pipe=False,
                 diff=None,
                 state=TestState.Waiting,
                 binary=False):
        """
        Initalises a test

        @type    DUT: str
        @param     DUT: The path to the Device Under Test
        @type    name: str
        @param    name: The name of the test case
        @type    description: str
        @param    description: The description of the test case
        @type    command: str
        @param    command: The command to be executed by the test case
        @type    stdout: str
        @param    stdout: The expected output on stdout
        @type    stderr: str
        @param    stderr: The expected output on stderr
        @type    returnCode: int
        @param    returnCode: The expected return code
        @type    timeout: float
        @param    timeout: The time out be before the DUT gets killed
        @type    pipe: Boolean
        @param    pipe: Flag, set if the output streams should be piped
        @type    outputOnFail: Boolean
        @param    outputOnFail: Flag, set if the output streams should be piped on failed test
        """
        self.name = name
        """The name of the test"""
        self.descr = description
        """The description of the test"""
        self.cmd = command
        """The description of the game"""
        self.expectStdout = stdout
        """The description of the game"""
        self.expectStderr = stderr
        """The expected output on stderr"""
        self.expectRetCode = returnCode
        self.timeout = timeout
        """The expected return code"""
        self.DUT = DUT
        """The Device under Test - could be None"""
        self.output = ""
        """The stdout"""
        self.error = ""
        """The stderr"""
        self.retCode = 0
        """The return code"""
        self.state = TestState.Waiting
        """The state of the game"""
        self.pipe = pipe
        """Flag, set if the output streams should be piped"""
        self.outputOnFail = outputOnFail
        """Flag, set if the output streams should be piped on failed test"""
        self.diff = diff
        """Flag, show comparison between input and string-expectation"""
        self.timeout = timeout
        """Timeout after the DUT gets killed"""
        self.linesep = os.linesep
        """Force a specific line ending"""
        self.ignoreEmptyLines = False
        """Ignore empty lines Flag"""
        self.pipeLimit = 2000
        """Work in binary mode"""
        self.binary = binary

    def lineComparison(self, expLines, outLines, stream=""):
        same = True
        if self.ignoreEmptyLines:
            while expLines.count("") > 0:
                expLines.remove("")
            while outLines.count("") > 0:
                outLines.remove("")
        for line in difflib.unified_diff(expLines, outLines, stream, "expectation"):
            col = TermColor.White
            if line.startswith(" + "):
                same = False
                col = TermColor.Green
            elif line.startswith("-"):
                same = False
                col = TermColor.Red
            elif line.startswith("@"):
                same = False
                col = TermColor.Cyan
            if self.diff:
                logger.log(TermColor.colorText(line.rstrip(), col))
        return same

    def check(self, exp, out, stream="returnCode"):
        """
        Test an expectation against an output
        If it's a lambda function, it will be executed with the output
        If it's a string, it will be treated as a regular expression.
        @type    exp: String, lambda
        @param    exp: Expected result
        @type     out: String
        @param    out: output The output
        @rtype:    Boolean
        @return: Result of the comparison
        """
        if exp is None:
            return True
        elif isLambda(exp) or isinstance(exp, Expectation):
            return exp(out)
        elif isinstance(exp, Stringifier):
            return self.lineComparison(*(exp(out)), stream=stream)
        elif isinstance(exp, int) and isinstance(out, int):
            return exp == out
        elif isinstance(exp, list):
            return self.checkList(exp, out)
        elif isinstance(exp, set):
            return self.checkSet(exp, out)
        elif isinstance(exp, bytes):
            return exp == out
        elif isinstance(exp, str):
            if exp.startswith("lambda"):
                f = eval(exp)
                return f(out)
            if exp.startswith("regex:"):
                patCode = re.compile(exp[6:].replace("$n", self.linesep), re.IGNORECASE)
                return (patCode.match(str(out)) != None)
            else:
                expLines = exp.replace("$n", self.linesep).splitlines()
                outLines = str(out).rstrip().splitlines()
                return self.lineComparison(expLines, outLines, stream)
        return False

    def checkList(self, lst, out):
        """
        Tests a list of expectations against an output
        all elements in the list must match to be successful
        @type    lst: List
        @param    lst: List with expectation
        @type     out: String, Int
        @param    out: output The output
        @rtype:    Boolean
        @return: Result of the comparison
        """
        for exp in lst:
            if not self.check(exp, out):
                return False
        return True

    def checkSet(self, st, out):
        """
        Tests a set of expectations against an output
        one element in the set must match to be successful
        @type    lst: List
        @param    lst: List with expectation
        @type     out: String, Int
        @param    out: output The output
        @rtype:    Boolean
        @return: Result of the comparison
        """
        for exp in st:
            if self.check(exp, out):
                return True
        return False

    def pipeOutputStream(self, stream, lines, color):
        bytes = 0
        for line in lines:
            bytes += len(line)
            stream.write(TermColor.colorText(line + " ", fg=color) + "\n")
            if bytes > self.pipeLimit:
                stream.write(TermColor.colorText("Stopped after {} Bytes".format(bytes), fg=TermColor.Yellow) + "\n")
                break

    def runCmd(self, command):
        if "$DUT" in command:
            if self.DUT is None:
                self.state = TestState.Error
                return
            else:
                _cmd = Command(cmd=str(command).replace("$DUT", self.DUT), binary=self.binary)
        else:
            _cmd = Command(cmd=str(command))
        cmdRet = _cmd.execute(self.timeout)
        if cmdRet == TestState.Success:
            self.output = _cmd.out
            self.error  = _cmd.err
            self.retCode = _cmd.ret
            if (self.check(self.expectRetCode, self.retCode) and
                    self.check(self.expectStdout, self.output, "stdout") and
                    self.check(self.expectStderr, self.error, "stderr")):
                self.state = TestState.Success
            else:
                if 'Assertion' in self.error or 'assertion' in self.error:
                    self.state = TestState.Assertion
                elif "stackdump" in self.error or "coredump" in self.error or "Segmentation Fault" in self.error or self.retCode < 0:
                    self.state = TestState.SegFault
                else:
                    self.state = TestState.Fail
            if (self.pipe) or (self.outputOnFail and self.state is TestState.Fail):
                sys.stdout.write(TermColor.colorText("{}".format(self.retCode), fg=TermColor.Yellow) + " ")
                self.pipeOutputStream(sys.stdout, self.output.splitlines(), TermColor.Green)
                self.pipeOutputStream(sys.stderr, self.error.splitlines(), TermColor.Red)
        else:
            self.state = cmdRet

    def run(self):
        """Runs the test"""
        if self.state == TestState.Disabled:
            return TestState.Disabled
        if self.state == TestState.InfoOnly:
            if self.descr is None:
                print("{}".format(self.name))
            else:
                print("{} - {}".format(self.name, self.descr))
            return TestState.InfoOnly
        if self.name == "Badword":
            # Bad Word Detection Mode
            # Description holds a matching file patterns
            # Recursive look through the directory of DUT
            # Treat command as a list of Badwords
            words = [re.compile(s) for s in self.cmd]
            searchpath = os.path.abspath(os.path.dirname(self.DUT))
            searchpattern = re.compile(self.descr)
            hits = []
            for dirpath, dirnames, filenames in os.walk(searchpath):
                for file in filenames:
                    if searchpattern.match(file) is not None:
                        fname = os.path.join(dirpath, file)
                        with open(fname, "r") as fHnd:
                            for nr, line in enumerate(fHnd.readlines()):
                                for word in words:
                                    if word.search(line) is not None:
                                        hits.append((os.path.relpath(fname), nr, line.rstrip(), word.pattern))
            if len(hits) > 0:
                for file, lineno, text, pattern in hits:
                    logger.log("{} {}[{}]: '{}' matches '{}'".format(TestState.toString(TestState.BadWord), file, lineno, text, pattern))
                self.state = TestState.BadWord
            else:
                self.state = TestState.Clean
            return self.state
        if self.cmd is not None:
            if isinstance(self.cmd, list):
                for cmd_ in self.cmd:
                    self.runCmd(cmd_)
            else:
                self.runCmd(self.cmd)
        else:
            self.state = TestState.Error
        return self.state

    def __str__(self):
        return self.toString(prefix="")

    def toString(self, prefix="\t"):
        """
        Creates a textual representation of the test.
        The output can be saved to a file.

        @rtype:     String
        """
        fields = []
        fields.append("{}\tname = '{:s}'".format(prefix, self.name))
        if self.descr is not None and self.descr != "":
            fields.append("{}\tdescription = '{:s}'".format(prefix, self.descr))
        fields.append("{}\tcommand = '{:s}'".format(prefix, self.cmd))
        if self.expectStdout is not None:
            fields.append("{}\tstdout = \"\"\"{}\"\"\"".format(prefix, self.expectStdout))
        if self.expectStderr is not None:
            fields.append("{}\tstderr = \"\"\"{}\"\"\"".format(prefix, self.expectStderr))
        if self.expectRetCode is not None:
            fields.append("{}\treturnCode = \"{}\"".format(prefix, self.expectRetCode))
        if self.timeout is not None:
            fields.append("{}\ttimeout = {:.1f}".format(prefix, self.timeout))
        return "Test (\n{}\n{})".format(",\n".join(fields), prefix)

class TestGroup:

    def __init__(self, *tests, name=None):
        self.tests = [t for t in tests]
        self._name = name
        self.state = TestState.Waiting

    @property
    def name(self):
        if self._name is None:
            return "Group of {} tests".format(len(self.tests))
        return self._name

    @property
    def descr(self):
        return None

    @property
    def cmd(self):
        return " --> ".join(t.cmd for t in self.tests)

    def run(self):
        success = True
        for nr, t in enumerate(self.tests):
            if t.run() != TestState.Success:
                success = False
            if t.descr is not None:
                logger.log("  {}[{: 03}] {} - {}: {}".format(TermColor.colorText("Test", TermColor.Purple), nr, t.name, t.descr, TestState.toString(t.state)))
            else:
                logger.log("  {}[{: 03}] {}: {}".format(TermColor.colorText("Test", TermColor.Purple), nr, t.name, TestState.toString(t.state)))
        self.state = TestState.Success if success else TestState.Fail
        return self.state


    def toString(self, prefix="\t"):
        """
        Creates a textual representation of the testgroup.
        The output can be saved to a file.
        """
        tests = [t.toString(prefix+"\t") for t in self.tests]
        if (self._name is not None):
            tests += ["name='{}'".format(self.name)]
        return "Group(\n{}\t{}\n{})".format(
            prefix,
            ",\n{}\t".format(prefix).join(tests),
            prefix,
        )

