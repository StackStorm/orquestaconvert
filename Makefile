# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

SHELL := /bin/bash

ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PYMODULE_DIR := $(ROOT_DIR)
PYMODULE_TESTS_DIR ?= $(PYMODULE_DIR)/tests
PYMODULE_NAME = $(shell python $(PYMODULE_DIR)/setup.py --name )
YAML_FILES := $(shell git ls-files '*.yaml' '*.yml')
JSON_FILES := $(shell git ls-files '*.json')
PY_FILES   := $(shell git ls-files '*.py')
TEST_COVERAGE_DIR ?= $(ROOT_DIR)/cover
NOSE_OPTS := -s -v --exe --rednose --immediate --with-coverage --cover-inclusive --cover-erase --cover-package=$(PYMODULE_NAME)

# Detect the OS
# https://stackoverflow.com/a/14777895
ifeq ($(OS),Windows_NT)
	detected_OS := Windows
else
	detected_OS := $(shell sh -c 'uname -s 2>/dev/null || echo no')
endif

# For a list of unames, see https://stackoverflow.com/a/14777895
BSD_USERLANDS := Darwin FreeBSD NetBSD DragonFly
# Note: GNU/kFreeBSD is the Debian GNU userland running on the BSD kernel
GNU_USERLANDS := Linux GNU GNU/kFreeBSD

# From https://stackoverflow.com/a/27335439
# If the result of searching for the detected_OS value in BSD_USERLANDS is not
# empty, then run the BSD sed block, run the same check for GNU_USERLANDS, or
# if nothing matches, then we simply guess how to tell sed to modify files
# in-place.
ifneq ($(filter $(detected_OS),$(BSD_USERLANDS)),)
	# BSD sed requires an extension after the -i flag for the extension of the
	# backup file it creates (so...it's not actually "in-place"). Here we
	# disable that by passing in an empty string, and telling sed to go back
	# to parsing it's normal expressions by adding the -e flag.
	SED_INPLACE_FLAGS := -i'' -e
else ifneq ($(filter $(detected_OS),$(GNU_USERLANDS)),)
	# Asking sed to replace files in-place is a little easier with GNU sed
	SED_INPLACE_FLAGS := -i
else
	# All bets are off. We need to guess.
	SED_INPLACE_FLAGS := -i
endif

# Virtual Environment
VIRTUALENV_DIR ?= $(ROOT_DIR)/virtualenv
ORQUESTA_DIR ?= $(VIRTUALENV_DIR)/orquesta


# Run all targets
.PHONY: all
all: requirements lint test #  test-coveralls

.PHONY: clean
clean: .clean-virtualenv .clean-test-coverage .clean-pyc

.PHONY: lint
lint: requirements flake8 pylint json-lint yaml-lint

.PHONY: flake8
flake8: requirements .flake8

.PHONY: pylint
pylint: requirements .pylint

.PHONY: json-lint
pylint: requirements .json-lint

.PHONY: yaml-lint
pylint: requirements .yaml-lint

.PHONY: test
test: requirements .test

.PHONY: test-coverage-html
test-coverage-html: requirements .test-coverage-html

.PHONY: test-coveralls
test-coveralls: requirements .test-coveralls

.PHONY: codecov
codecov: requirements .codecov

.PHONY: clean-test-coverage
clean-test-coverage: .clean-test-coverage

# list all makefile targets
.PHONY: list
list:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' | xargs


.PHONY: .clean-pyc
.clean-pyc:
	@echo "==================== clean *.pyc ===================="
	find $(ROOT_DIR) -name 'virtualenv' -prune -or -name '.git' -or -type f -name "*.pyc" -print | xargs --no-run-if-empty rm 


.PHONY: virtualenv
virtualenv: $(VIRTUALENV_DIR)/bin/activate
$(VIRTUALENV_DIR)/bin/activate:
	@echo "==================== virtualenv ===================="
	test -d $(VIRTUALENV_DIR) || virtualenv --no-site-packages $(VIRTUALENV_DIR)
# Setup PYTHONPATH in bash activate script...
# Delete existing entries (if any)
	sed $(SED_INPLACE_FLAGS) '/_OLD_PYTHONPATHp/d' $(VIRTUALENV_DIR)/bin/activate
	sed $(SED_INPLACE_FLAGS) '/PYTHONPATH=/d' $(VIRTUALENV_DIR)/bin/activate
	sed $(SED_INPLACE_FLAGS) '/export PYTHONPATH/d' $(VIRTUALENV_DIR)/bin/activate
	echo '_OLD_PYTHONPATH=$$PYTHONPATH' >> $(VIRTUALENV_DIR)/bin/activate
	echo 'PYTHONPATH=${ROOT_DIR}' >> $(VIRTUALENV_DIR)/bin/activate
	echo 'export PYTHONPATH' >> $(VIRTUALENV_DIR)/bin/activate
	touch $(VIRTUALENV_DIR)/bin/activate


.PHONY: .clean-virtualenv
.clean-virtualenv:
	@echo "==================== cleaning virtualenv ===================="
	rm -rf $(VIRTUALENV_DIR)


.PHONY: requirements
requirements: virtualenv
	@echo
	@echo "==================== requirements ===================="
	@echo
	. $(VIRTUALENV_DIR)/bin/activate; \
	$(VIRTUALENV_DIR)/bin/pip install --upgrade pip; \
	$(VIRTUALENV_DIR)/bin/pip install --cache-dir $(HOME)/.pip-cache -q -r $(PYMODULE_DIR)/requirements.txt -r $(PYMODULE_DIR)/requirements-test.txt -r $(PYMODULE_DIR)/requirements-orquesta.txt;


.PHONY: update-orquesta-requirements
update-orquesta-requirements: virtualenv
	test -d $(ORQUESTA_DIR) || git clone "https://github.com/StackStorm/orquesta" $(ORQUESTA_DIR)
	cp $(ORQUESTA_DIR)/requirements.txt requirements-orquesta.txt


.PHONY: .flake8
.flake8:
	@echo
	@echo "==================== flake8 ===================="
	@echo
	. $(VIRTUALENV_DIR)/bin/activate; \
	for py in $(PY_FILES); do \
		echo "Checking $$py"; \
		flake8 --config $(PYMODULE_DIR)/lint-configs/python/.flake8 $$py || exit 1; \
	done


.PHONY: .pylint
.pylint:
	@echo
	@echo "==================== pylint ===================="
	@echo
	. $(VIRTUALENV_DIR)/bin/activate; \
	echo $(PY_FILES) | xargs python -m pylint -E --rcfile=$(PYMODULE_DIR)/lint-configs/python/.pylintrc && echo "--> No pylint issues found." || exit 1


.PHONY: .json-lint
.json-lint:
	@echo
	@echo "==================== json-lint ===================="
	@echo
	. $(VIRTUALENV_DIR)/bin/activate; \
	for json in $(JSON_FILES); do \
		echo "Checking $$json"; \
		python -mjson.tool $$json > /dev/null || exit 1; \
	done


.PHONY: .yaml-lint
.yaml-lint:
	@echo
	@echo "==================== yaml-lint ===================="
	@echo
	. $(VIRTUALENV_DIR)/bin/activate; \
	for yaml in $(YAML_FILES); do \
		echo "Checking $$yaml"; \
		python -c "import yaml; yaml.safe_load(open('$$yaml', 'r'))" || exit 1; \
	done


.PHONY: .test
.test:
	@echo
	@echo "==================== test ===================="
	@echo
	. $(VIRTUALENV_DIR)/bin/activate; \
	if [ -d "$(PYMODULE_TESTS_DIR)" ]; then \
		nosetests $(NOSE_OPTS) $(PYMODULE_TESTS_DIR) || exit 1; \
	else \
		echo "Tests directory not found: $(PYMODULE_TESTS_DIR)";\
	fi;


.PHONY: .test-coverage-html
.test-coverage-html:
	@echo
	@echo "==================== test-coverage-html ===================="
	@echo
	. $(VIRTUALENV_DIR)/bin/activate; \
	if [ -d "$(PYMODULE_TESTS_DIR)" ]; then \
		nosetests $(NOSE_OPTS) --cover-html $(PYMODULE_TESTS_DIR) || exit 1; \
	else \
		echo "Tests directory not found: $(PYMODULE_TESTS_DIR)";\
	fi;


.PHONY: .test-test-coverage-html
.test-test-coverage-html:
	@echo
	@echo "================== test-test-coverage-html =================="
	@echo
	. $(VIRTUALENV_DIR)/bin/activate; \
	if [ -d "$(PYMODULE_TESTS_DIR)" ]; then \
		nosetests $(NOSE_OPTS),tests --cover-tests --cover-html $(PYMODULE_TESTS_DIR) || exit 1; \
	else \
		echo "Tests directory not found: $(PYMODULE_TESTS_DIR)";\
	fi;


.PHONY: .test-coveralls
.test-coveralls:
	@echo
	@echo "==================== test-coveralls ===================="
	@echo
	. $(VIRTUALENV_DIR)/bin/activate; \
	if [ ! -z "$$COVERALLS_REPO_TOKEN" ]; then \
		coveralls; \
	else \
		echo "COVERALLS_REPO_TOKEN env variable is not set! Skipping test coverage submission to coveralls.io."; \
	fi;


.PHONY: .clean-test-coverage
.clean-test-coverage:
	@echo
	@echo "==================== clean-test-coverage ===================="
	@echo
	rm -rf $(TEST_COVERAGE_DIR)
	rm -f $(PYMODULE_DIR)/.coverage

.PHONY: .codecov
.codecov:
	@echo
	@echo "==================== codecov ===================="
	@echo
	. $(VIRTUALENV_DIR)/bin/activate; \
		codecov
