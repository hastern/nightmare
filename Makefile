# pyTest creation makefile
# author: Hanno Sternberg
# 

PY	=python
SETUP	=setup.py

SRC_EGG	=pyTest-1.0-py2.7.egg
TARGET	=pyTest.egg

default: all

all: build dist egg

build:
	$(PY) $(SETUP) build

egg:
	$(PY) $(SETUP) bdist_egg
	cp dist/$(SRC_EGG) $(TARGET)
	
dist:
	$(PY) $(SETUP) sdist

clean:
	$(PY) $(SETUP) clean
	rm -rf build dist pyTest.egg-info
	rm -f pyTestCore/*.py pyTestGui/*.py *.pyc $(TARGET)
	
	


