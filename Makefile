# pyTest creation makefile
# author: Hanno Sternberg
# 

PY	=python
SETUP	=$(PY) setup.py
DOC	=$(PY) epydoc.py

SRC_EGG	=$(shell $(SETUP) --fullname)-py2.7.egg
TARGET	=$(shell $(SETUP) --name).egg

.PHONY: build egg dist clean doc license description info

default: all

all: build dist egg

build:
	$(SETUP) build

egg: 
	$(SETUP) bdist_egg
	cp dist/$(SRC_EGG) $(TARGET)
	
dist:
	$(SETUP) sdist

doc:
	$(DOC) --config=epydocfile
	
license:
	@$(SETUP) --license
	
description:
	@$(SETUP) --long-description
	
info: license description
	
clean:
	$(SETUP) clean
	rm -rf build dist pyTest.egg-info doc
	rm -f pyTestCore/*.pyc pyTestGui/*.pyc *.pyc $(TARGET)
	
	


