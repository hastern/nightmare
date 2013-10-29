#!/usr/bin/env python

# An example suite with direct suite instantiation 



suite = Suite(
	Test (
		name = "Segfault Example",
		description= "This test is a SegFault", 
		command = "$DUT 2", 
		returnCode = 0
	),
	Test (
		name = "Assertion Example",
		description= "This test is an assertion", 
		command = "$DUT 1", 
		returnCode = 0
	),
)