#!/usr/bin/env python

# An example suite

test1 = {
	"cmd":"dut.py success", 
	"name":"Example 1", 
	"descr":"This test should be a success", 
	"expect":"success"
}
test2 = {
	"cmd":"dut.py FAIL", 
	"name":"Example 2", 
	"descr":"This test is doomed to fail", 
	"expect":"failed"
}
test3 = {
	"name":"Example 3",
	"descr":"This test will produce an error"
}

suite = [test1, test2, test3]