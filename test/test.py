#!/usr/bin/evn python

import os
import re
import sys
import subprocess

from threading import Thread

from testState import TestState
from utils import isLambda


class Command():
	#__slots__ = ['_cmd', '_process', '_thread', 'out', 'err', 'ret', 'killed']
	"""Command execution"""
	def __init__(self, cmd):
		"""
		Initialises the command
		
		@type	cmd: str
		@param	cmd: Command
		"""
		self._cmd = cmd
		self._process = None
		self._thread = None
		self.out = ""
		self.err = ""
		self.ret = 0
		self.killed = False

	def commandFunc(self):
		"""command to be run in the thread"""
		self._process = subprocess.Popen(self._cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
		self.out, self.err = self._process.communicate()
		self.ret = self._process.wait()
		
	def execute(self, timeout):
		"""
		executes the command
				
		@type	timeout: float
		@param	timeout: Timeout in seconds
		"""
		self._thread = Thread(target=self.commandFunc)
		self._thread.start()
		self._thread.join(timeout)
		if self._thread.isAlive():
			if sys.platform == "win32":
				subprocess.Popen(['taskkill', '/F', '/T', '/PID', str(self._process.pid)]).communicate()
			else:
				os.killgp(self._process.pid)
			self._thread.join()
			return TestState.Timeout
		return TestState.Success
	
class Test:
	"""A single test"""
	
	def __init__(self, DUT=None, name=None, description=None, command=None, stdout=None, stderr=None, returnCode=None, timeout=10.0):
		"""
		Initalises a test
		
		@type	data: Dictionary
		@param	data: Dictionary with test definitions
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
		if DUT is not None:
			self.DUT = DUT
		self.output = ""
		"""The stdout"""
		self.error = ""
		"""The stderr"""
		self.retCode = 0
		"""The return code"""
		self.state = TestState.Waiting
		"""The state of the game"""
		self.pipe = False
		"""Flag, set if the output streams should be piped"""
		self.outputOnFail = False
		"""Flag, set if the output streams should be piped on failed test"""
		self.timeout = timeout
		"""Timeout after the DUT gets killed"""
		self.linesep = os.linesep
			
	def _check(self, exp, out):
		"""
		Test an expectation against an output
		If it's a lambda function, it will be executed with the output
		If it's a string, it will be treated as a regular expression.
		If it's an integer, it gets compared with the output
		@type	exp: String, Int, lambda 
		@param	exp: Expected result
		@type 	out: String, Int
		@param	out: output The output
		@rtype:	Boolean
		@return: Result of the comparison
		"""
		if (isLambda(exp)):
			return exp(out)
		elif (isinstance(exp, int) and isinstance(out, int)):
			return exp == out
		elif isinstance(exp, list):
			return self._checkList(exp, out)
		elif isinstance(exp, str):
			if exp.startswith("lambda"):
				f = eval(exp)
				return f(out)
			if exp.startswith("regex:"):
				patCode = re.compile(exp[6:].replace("$n", self.linesep), re.IGNORECASE)
				return (patCode.match(str(out)) != None)
			else:
				return exp.replace("$n", self.linesep) == str(out)
		elif exp is None:
			return True
		return False
	
	def _checkList(self, lst, out):
		"""
		Tests a list of expectations against an output
		@type	lst: List
		@param	lst: List with expectation
		@type 	out: String, Int
		@param	out: output The output
		@rtype:	Boolean
		@return: Result of the comparison
		"""
		if isinstance(lst, list):
			for exp in lst:
				if not self._check(exp, out):
					return False
			return True
		else:
			return self._check(lst, out)
	
	def runCmd(self, command):
		_cmd = Command(cmd=str(command).replace("$DUT", self.DUT))
		cmdRet = _cmd.execute(self.timeout)
		if cmdRet == TestState.Success:
			self.output = _cmd.out
			self.error = _cmd.err
			self.retCode = _cmd.ret
			if self._check(self.expectRetCode, self.retCode) \
				and self._check(self.expectStdout,self.output) \
				and self._check(self.expectStderr,self.error):
				self.state = TestState.Success
			else:
				self.state = TestState.Fail
			if (self.pipe) or (self.outputOnFail and self.state is TestState.Fail):
				sys.stdout.write( "{} ".format(self.retCode) )
				sys.stdout.write( self.output )
				sys.stderr.write( self.error )
		else:
			self.state = cmdRet
			
	def run(self):
		"""Runs the test"""
		if self.state == TestState.Disabled:
			return TestState.Disabled
		if self.state == TestState.InfoOnly:
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
		
	def toString(self, prefix="\t"):
		"""
		Creates a textual representation of the test.
		The output can be saved to a file.
		
		@rtype: 	String
		"""
		fields = []
		fields.append("{}\tname = \"{:s}\"".format(prefix, self.name))
		if self.descr is not None and self.descr != "":
			fields.append("{}\tdescription = \"{:s}\"".format(prefix, self.descr))
		fields.append("{}\tcommand = \"{:s}\"".format(prefix, self.cmd))
		if self.expectStdout is not None:
			fields.append("{}\tstdout = \"{}\"".format(prefix, self.expectStdout))
		if self.expectStderr is not None:
			fields.append("{}\tstderr = \"{}\"".format(prefix, self.expectStderr))
		if self.expectRetCode is not None:
			fields.append("{}\treturnCode = \"{}\"".format(prefix, self.expectRetCode))
		if self.timeout is not None:
			fields.append("{}\ttimeout = {:.1f}".format(prefix, self.timeout))
		return "Test (\n{}\n{})".format(",\n".join(fields), prefix)
