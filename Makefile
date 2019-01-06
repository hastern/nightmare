# pyTest creation makefile
# author: Hanno Sternberg
#

PY               =python
DIST_DIR         =dist
BUILD_DIR        =build
SETUP            =$(PY) setup.py
NAME             =$(shell $(SETUP) --name)

VALIDATION_BENCH =validation.py
VALIDATION_SUITE =validateThisNightmare
VALIDATION_FLAGS =-o

RES         =resource

DIST_EGG    =$(DIST_DIR)/$(shell $(SETUP) --fullname)-py3.7.egg
DIST_EXE    =$(DIST_DIR)/$(NAME).exe

.PHONY: build dist egg exe clean doc validate info icon

default: all

all: build egg exe

build: validate
	$(SETUP) build --build-base $(BUILD_DIR)

egg: $(DIST_EGG) ## Build an egg

$(DIST_EGG):
	$(SETUP) bdist_egg --dist-dir $(DIST_DIR)

exe: $(DIST_EXE) ## Build an exe

$(DIST_EXE):
	pyinstaller -F main.py -n nightmare -i resource/nightmare.ico

dist:
	$(SETUP) sdist --dist-dir $(DIST_DIR)

release: validate egg exe ## Make a release

doc: ## Build the docs
	cd docs && sphinx-build . _build/html

validate: ## Do a self validation
	@$(PY) -m nightmare --no-gui --bench nightmare/$(VALIDATION_BENCH) --dut "$(PY) -m nightmare" --suite $(VALIDATION_SUITE) $(VALIDATION_FLAGS)

icon:
	@png2ico $(RES)/$(NAME).ico $(RES)/$(NAME).png $(RES)/$(NAME)128.png $(RES)/$(NAME)48.png $(RES)/$(NAME)32.png $(RES)/$(NAME)16.png

clean: ## Clean up
	$(SETUP) clean
	rm -rf $(BUILD_DIR) $(DIST_DIR) $(shell $(SETUP) --fullname).egg-info doc
	rm -f *.pyc

help: ## Show this help
	@grep -E '^[a-zA-Z0-9%._-]+:.*?## .*$$' Makefile | sed 's/%/<FILE>/g' | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
