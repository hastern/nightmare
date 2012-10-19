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
test4 = {
	"name":"Example 4",
	"descr":"Lambda expression success",
	"cmd":"dut.py Some more text",
	"expect":lambda x: x.find("text") > 0 
}
test5 = {
	"name":"Example 5",
	"descr":"Lambda expression fail",
	"cmd":"dut.py Some more text",
	"expect":lambda x: x.find("test") > 0 
}
suite = [test1, test2, test3, test4, test5]