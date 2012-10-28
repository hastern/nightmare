pyTest
======
You must really, really love to test!

---

pyTest is a tool for automatic testing of non-interactive commandline 
applications.

	Usage: pyTest.py [OPTIONS]
	  OPTIONS:
		-bench:TESTBENCH
			Load the testbench form the file TESTBENCH.
		-suite:SUITE
			Use the testsuite SUITE from the testbench.
		-test:TEST
			Only run test number TEST.
		-dut:DUT
			Set the device under test to the file DUT.
		-c
			Continuous mode (Don't halt on failed tests).
		-e
			Same as '-c', but will halt if an error occurs.
		-l
			Print only the number of tests in the suite.
		--no-color
			Don't use any colored output.
		--no-gui
			Don't use the GUI.
		-q
			Quiet mode. There will be no output except results.
		-v
			Verbose mode. The program gets chatty.
		-h, --help, -?
			Print this help
			
Additional to the commandline interface there is a GUI using the 
tkinter-package. The GUI is limited in its capabilities compared to the CLI,
especially when it comes to testbench editing.

Be careful when you save your testbench! You might loose data, if it originates
 from a handwritten testbench.


Testbench files
---------------

A collection of test is called a "testbench".
Inside a testbench there are a number of suites grouping tests together.

The testbench files a normal python files, which get evaluated by calling
the internal "execfile" function. This might not be the savest approach, but
it is definitly one of the easiest ones.

Here is a example for a minimal testbench.

	#!/usr/bin/env python
	
	# pyTest - Testsuite
	# Saved at 21:12:26
	# 

	# Device Under Test
	DUT = "echo"

	# Test definitions
	suite = [
		Test (
			name = "Test 1",
			description = "A successfull run",
			command = "$DUT pyTest",
			stdout = "pyTest",
			returnCode = 0
		),
		Test (
			name = "Test 2",
			description = "Testing output on stderr",
			command = "$DUT pyTest 1>2",
			stderr = "pyTest"
		)
	]
	
This example contains on testsuite name "suite" with two tests.
I hope the syntax is selfexplanatory.

The Pattern $DUT is a substitute for the application that gets tested.

Here's a list of all possible fields in a test definition:

-name: The (brief) name of the test.
-description: A longer description, about the purpose of this test.
-command: The command to be executed.
-stdout: The expected result on stdout.
-stderr: The expected result on stderr.
-returnCode: The expected returncode.

Almost every field in the test is optional expect the command. The reason 
should be obvious.

One reason for the testfiles to be real python script is the possibility to use 
lambda functions for testing the output against an expectation.

The following example shows a test using a lambda function:

	Test (
		name "Lambda",
		description = "A test with lambda function",
		command = "echo Hello World",
		stdout = lambda x : x.find("o") > 0
	)
	
All expectation fields (stdout, stderr, returnCode) may contain lambda 
a lambda expression.


