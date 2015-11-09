# pyTest creation makefile
# author: Hanno Sternberg
# 

PY               =python
DIST_DIR         =dist
BUILD_DIR        =build
SETUP            =$(PY) setup.py
DOC              =epydoc
NAME             =$(shell $(SETUP) --name)

VALIDATION_BENCH =validation.py
VALIDATION_SUITE =validateThisNightmare
VALIDATION_FLAGS =-o

RES         =resource

DIST_EGG    =$(DIST_DIR)/$(shell $(SETUP) --fullname)-py2.7.egg
DIST_EXE    =$(DIST_DIR)/$(NAME).exe

.PHONY: build dist clean doc profile license validate description info version icon

default: all

all: build egg exe

build: validate
	$(SETUP) build --build-base $(BUILD_DIR)

egg: $(DIST_EGG)

$(DIST_EGG):
	$(SETUP) bdist_egg --dist-dir $(DIST_DIR)

exe: $(DIST_EXE)

$(DIST_EXE): 
	$(SETUP) py2exe --dist-dir $(DIST_DIR)


dist:
	$(SETUP) sdist --dist-dir $(DIST_DIR)

release: validate version egg exe

doc:
	$(PY) -c "from epydoc.cli import cli; cli()" --config=epydocfile

profile:
	$(PY) -m cProfile -o profile.out pyTestMain.py

validate:
	@$(PY) $(VALIDATION_BENCH)

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
	
	


