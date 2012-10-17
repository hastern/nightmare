#!/usr/bin/env python

# An example suite

test1 = {
	"cmd":"dut.py hello", 
	"name":"Hello", 
	"descr":"prints hello", 
	"expect":"hello\n", 
	"returnCode":0
}
test2 = {
	"cmd":"dut.py world", 
	"name":"World", 
	"descr":"prints world", 
	"expect":"World",
	"returnCode":0
}
test3 = {
	"name":"Test with Error"
}

suite = [test1, test3, test2]