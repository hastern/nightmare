#!/usr/bin/env python

from Tkinter import *
from ttk import *
import tkFileDialog as fileDiag


class FileLoaderButton(Button):
	"""Button for handling file selection"""
	def __init__(self, parent, caption, callback, func=fileDiag.askopenfilename, filetypes=[("All files","*")], defaultExt=""):
		"""
		Initialises the button
		
		@type 	parent: Widget
		@param	parent: Parent widget
		
		@type	caption: String
		@param	caption: Caption for the button
		
		@type	cb: Function
		@param 	cb: Callback function, called after successfull selection
		
		@type	func: Function
		@param	func: Function to be called for file selection
		"""
		Button.__init__(self, parent, text=caption, command=self.selectFile)
		self._cb = callback
		self._func = func
		self._caption = caption
		self._filetypes = filetypes
		self._defaultExt = defaultExt
	
	def selectFile(self):
		"""Eventhandler for button click"""
		if self._func is not None:
			fn = self._func(initialdir=".", filetypes=self._filetypes, defaultextension=self._defaultExt, title=self._caption)
			if fn != "":
				self._cb(fn)
