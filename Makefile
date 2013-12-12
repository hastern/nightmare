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

build: validate
	$(SETUP) build

egg: validate
	$(SETUP) bdist_egg
	
exe: validate
	$(SETUP) py2exe
	
dist:
	$(SETUP) sdist

doc:
	$(PY) -c "from epydoc.cli import cli; cli()" --config=epydocfile
	
profile:
	$(PY) -m cProfile -o profile.out pyTestMain.py
	
validate:
	@$(PY) validation.py
	
license:
	@$(SETUP) --license
	
version:
	@$(PY) version.py
	
description:
	@$(SETUP) --long-description
	
info: license description
	
clean:
	$(SETUP) clean
	rm -rf build dist $(shell $(SETUP) --fullname).egg-info doc
	rm -f *.pyc
	
	


