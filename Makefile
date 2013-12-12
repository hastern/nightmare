# pyTest creation makefile
# author: Hanno Sternberg
# 

PY	=python
SETUP	=$(PY) setup.py
DOC	=epydoc
NAME 	=$(shell $(SETUP) --name)

RES	=resource

SRC_EGG	=$(shell $(SETUP) --fullname)-py2.7.egg

.PHONY: build egg exe dist clean doc profile license validate description info version icon

default: all

all: build egg exe

build: validate
	$(SETUP) build

egg: 
	$(SETUP) bdist_egg
	
exe: 
	$(SETUP) py2exe
	
dist:
	$(SETUP) sdist
	
release: validate version egg exe

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

icon:
	@png2ico $(RES)/$(NAME).ico $(RES)/$(NAME).png $(RES)/$(NAME)128.png $(RES)/$(NAME)48.png $(RES)/$(NAME)32.png $(RES)/$(NAME)16.png

clean:
	$(SETUP) clean
	rm -rf build dist $(shell $(SETUP) --fullname).egg-info doc
	rm -f *.pyc
	
	


