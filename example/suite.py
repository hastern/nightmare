#!/usr/bin/env python

# An example suite
# This suite must be run from this diretory 

DUT = "example\dut.py"

suite = [
	Test (
		name = "Example 1",
		description= "This test should be a success", 
		command = "$DUT success", 
		stdout = "success"
	),
	Test (
		name = "Example 2", 
		description = "This test is doomed to fail", 
		command = "$DUT FAIL", 
		stdout = "failed"
	),
	Test (
		name = "Example 3",
		description = "This test will produce an error"
	),
	Test (
		name = "Example 4",
		description = "Lambda expression fail",
		command = "$DUT Some more text",
		stdout = "lambda x: x.find('test') > 0 "
	),
	Test (
		name = "Example 5",
		description = "Lambda expression success",
		command = "$DUT Some more text",
		stdout = "lambda x: x.find('text') > 0"
	),
	Test (
		name = "Example 6",
		description = "Timeout",
		command = "$DUT sleep",
		timeout = 1
	)
]