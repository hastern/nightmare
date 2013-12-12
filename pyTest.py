#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import sys
import signal
import subprocess

from threading import Thread

from pyTestUtils import isLambda, TermColor, logger

class TestState:
	#__slots__ = ["Success", "Fail", "Error", "Waiting", "Disabled", "InfoOnly", "Timeout"]

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
	
	
	@staticmethod
	def toString(state):
		"""
		Converts the enumeration value into a string
		
		@type	state: int
		@param	state: Enumeration value
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
		return TermColor.colorText(" UNKNOWN ", TermColor.Yellow)


class Command():
	#__slots__ = ['_cmd', '_process', '_thread', 'out', 'err', 'ret', 'killed']
	"""Command execution"""
	def __init__(self, cmd):
		"""
		Initialises the command
		
		@type	cmd: str
		@param	cmd: Command
		"""
		self.cmd = cmd
		self.proc = None
		self.thread = None
		self.out = ""
		self.err = ""
		self.ret = 0
		self.killed = False

	def commandFunc(self):
		"""command to be run in the thread"""
		self.proc = subprocess.Popen(self.cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True, shell=True, cwd=os.getcwd())
		self.out, self.err = self.proc.communicate()
		self.ret = self.proc.wait()
		
	def execute(self, timeout):
		"""
		executes the command
				
		@type	timeout: float
		@param	timeout: Timeout in seconds
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
				#os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
			return TestState.Timeout
		return TestState.Success
	
class Expectation(object):
	def __call__(self):
		return True

class ExpectFile(Expectation):
	def __init__(self, fname):
		self.exp = open(fname).read()
	def __call__(self, out):
		return exp == out
	def __str__(self):
		return self.exp
	
class Test(object):
	"""A single test"""
	
	def __init__(self, DUT=None, name="", description="", command=None, stdout=None, stderr=None, returnCode=None, timeout=5.0, outputOnFail = False, pipe = False, diff = None, state=TestState.Waiting):
		"""
		Initalises a test
		
		@type	DUT: str
		@param 	DUT: The path to the Device Under Test
		@type	name: str
		@param	name: The name of the test case
		@type	description: str
		@param	description: The description of the test case
		@type	command: str
		@param	command: The command to be executed by the test case
		@type	stdout: str
		@param	stdout: The expected output on stdout
		@type	stderr: str
		@param	stderr: The expected output on stderr
		@type	returnCode: int
		@param	returnCode: The expected return code
		@type	timeout: float
		@param	timeout: The time out be before the DUT gets killed
		@type	pipe: Boolean
		@param	pipe: Flag, set if the output streams should be piped
		@type	outputOnFail: Boolean
		@param	outputOnFail: Flag, set if the output streams should be piped on failed test
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
			
	def check(self, exp, out, stream="returnCode"):
		"""
		Test an expectation against an output
		If it's a lambda function, it will be executed with the output
		If it's a string, it will be treated as a regular expression.
		@type	exp: String, lambda 
		@param	exp: Expected result
		@type 	out: String
		@param	out: output The output
		@rtype:	Boolean
		@return: Result of the comparison
		"""
		if isLambda(exp) or isinstance(exp, Expectation):
			return exp(out)
		elif isinstance(exp, int) and isinstance(out, int):
			return exp == out
		elif isinstance(exp, list):
			return self.checkList(exp, out)
		elif isinstance(exp, set):
			return self.checkSet(exp, out)
		elif isinstance(exp, str):
			if exp.startswith("lambda"):
				f = eval(exp)
				return f(out)
			if exp.startswith("regex:"):
				patCode = re.compile(exp[6:].replace("$n", self.linesep), re.IGNORECASE)
				return (patCode.match(str(out)) != None)
			else:
				comp = exp.replace("$n", self.linesep) == str(out).rstrip()
				if self.diff is not None and not comp:
					for line in self.diff(exp.replace("$n", self.linesep).splitlines(), str(out).rstrip().splitlines(), stream, "expecation"):
						if line.startswith("+"):
							logger.log(TermColor.colorText(line.rstrip(), TermColor.Green))
						elif line.startswith("-"):
							logger.log(TermColor.colorText(line.rstrip(), TermColor.Red))
						elif line.startswith("?") or line.startswith("@"):
							logger.log(TermColor.colorText(line.rstrip(), TermColor.Cyan))
						else:
							logger.log(line)
				return comp
		elif exp is None:
			return True
		return False
	
	def checkList(self, lst, out):
		"""
		Tests a list of expectations against an output
		all elements in the list must match to be successful
		@type	lst: List
		@param	lst: List with expectation
		@type 	out: String, Int
		@param	out: output The output
		@rtype:	Boolean
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
		@type	lst: List
		@param	lst: List with expectation
		@type 	out: String, Int
		@param	out: output The output
		@rtype:	Boolean
		@return: Result of the comparison
		"""
		for exp in st:
			if self.check(exp, out):
				return True
		return False	
	
	def runCmd(self, command):
		_cmd = Command(cmd=str(command).replace("$DUT", self.DUT))
		cmdRet = _cmd.execute(self.timeout)
		if cmdRet == TestState.Success:
			self.output = _cmd.out
			self.error = _cmd.err
			self.retCode = _cmd.ret
			if self.check(self.expectRetCode, self.retCode) \
			and self.check(self.expectStdout,self.output, "stdout") \
			and self.check(self.expectStderr,self.error, "stderr"):
				self.state = TestState.Success
			else:
				if 'Assertion' in self.error or 'assertion' in self.error:
					self.state = TestState.Assertion
				elif "stackdump" in self.error or "coredump" in self.error or "Segmentation Fault" in self.error or self.retCode < 0:
					self.state = TestState.SegFault
				else:
					self.state = TestState.Fail
			if (self.pipe) or (self.outputOnFail and self.state is TestState.Fail):
				sys.stdout.write( TermColor.colorText("{}".format(self.retCode), fg=TermColor.Black, bg=TermColor.Yellow)+" " )
				for line in self.output.splitlines():
					sys.stdout.write( TermColor.colorText(line+" ", fg=TermColor.Black, bg=TermColor.Green)+"\n"  )
				for line in self.error.splitlines():
					sys.stderr.write( TermColor.colorText(line+" ", fg=TermColor.Black, bg=TermColor.Red)+"\n"  )
		else:
			self.state = cmdRet
			
	def run(self):
		"""Runs the test"""
		if self.state == TestState.Disabled:
			return TestState.Disabled
		if self.state == TestState.InfoOnly:
			if self.descr is None:
				print "{}".format(self.name)
			else:
				print "{} - {}".format(self.name, self.descr)
			return TestState.InfoOnly
		if self.cmd is not None and self.DUT is not None:
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
		
		@rtype: 	String
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
