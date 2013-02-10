#!/usr/bin/env python

from Tkinter import *
from ttk import *

class LabeledEntry(Frame):
	def __init__(self, parent, lbl, var, pos=LEFT, anch=NW):
		"""
		Initialise the labeled entry
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	lbl: String
		@param	lbl: The caption for the label
		
		@type	var: StringVar
		@param	var: The variable holding the content in the entry field
		
		@param	pos: Packing position for both widgets
		@param	anch: Packing anchor for both widgets
		"""
		Frame.__init__(self, parent)
		self.label = Label(self, text=lbl, width=10, justify=LEFT)
		self.entry = Entry(self, textvariable=var, width=20, justify=LEFT)
		self.label.pack(side=pos, anchor=anch)
		self.entry.pack(side=pos, anchor=anch, fill=X, expand=1)