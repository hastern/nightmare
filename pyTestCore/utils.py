

import sys
import os
import time
try:
	import colorama
except:
	colorama = None

def isLambda(v):
	""" 
	Test if a given value is a lambda function
	
	@type		v: Anything (preferable a lambda function)
	@param		v: Some value
	@rtype: 	Boolean
	@return:	True, if the value is a lambda function
	"""
	return isinstance(v, type(lambda: None)) and v.__name__ == '<lambda>'

class TermColor:
	__slots__ = [
		'Black', 'Red', 'Green', 'Yellow', 'Blue', 'Purple', 'Cyan', 'White',
		'Normal', 'Bold', 'Dim', 'Background', 'Text', 'active']
	""" Print colored text """
	Black = 0
	"""Black color code"""
	Red = 1
	"""Red color code"""
	Green = 2
	"""Green color code"""
	Yellow = 3
	"""Yellow color code"""
	Blue = 4
	"""Blue color code"""
	Purple = 5
	"""Purple color code"""
	Cyan = 6
	"""Cyan color code"""
	White = 7
	"""White color code"""
	Normal = 0
	"""Normal text style"""
	Bold = 1
	"""Bold text style"""
	Dim = 2
	"""Dim text style"""
	Background = 40
	"""Change background color"""
	Text = 30
	"""Change text color"""
	
	active = True
	"""activate colourful output"""
	
	
	@staticmethod
	def colorText(text, color = 7, where = 30, style = 0):
		if TermColor.active and ((colorama is not None) or (os.getenv('ANSI_COLORS_DISABLED') is not None)):
			colStr = str(where + color)
			styleStr = "{:02}".format(style)
			return "\033[{};{}m{}".format(styleStr, colStr, text)
		else:
			return text
			
	@staticmethod
	def init():
		if colorama is not None:
			colorama.init(autoreset=True)
		
		

class logger:
	__slots__ = ['_buffer']
	"""Logger class"""
	_buffer = []
	"""Message buffer"""
	@staticmethod
	def log(str):
		"""
		Writes a log message to the buffer
		
		@type	str: String
		@param	str: Log message
		"""
		msg = "[{0}] {1}".format(time.strftime("%H:%M:%S") , str.strip("\r\n") )
		logger._buffer.append(msg)
		
	@staticmethod
	def flush(quiet = False):
		"""
		flushes the message buffer
		
		@type	quiet: Boolean
		@param	quiet: Flag if the buffer should be printed or not
		"""
		if not quiet:
			for b in logger._buffer:
				print b
			sys.stdout.flush()
		logger.clear()
	
	@staticmethod
	def clear():
		"""
		Clears the buffer
		"""
		logger._buffer = []