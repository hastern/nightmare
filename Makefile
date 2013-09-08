# pyTest creation makefile
# author: Hanno Sternberg
# 

PY	=python
SETUP	=$(PY) setup.py
DOC	=epydoc

SRC_EGG	=$(shell $(SETUP) --fullname)-py2.7.egg

.PHONY: build egg exe dist clean doc profile license description info

default: all

all: build egg exe

build:
	$(SETUP) build

egg: 
	$(SETUP) bdist_egg
	
exe:
	$(SETUP) py2exe
	
dist:
	$(SETUP) sdist

doc:
	python -c "from epydoc.cli import cli; cli()" --config=epydocfile
	
profile:
	$(PY) -m cProfile -o profile.out pyTestMain.py
	
license:
	@$(SETUP) --license
	
description:
	@$(SETUP) --long-description
	
info: license description
	
clean:
	$(SETUP) clean
	rm -rf build dist pyTest.egg-info doc
	rm -f *.pyc
	
	


