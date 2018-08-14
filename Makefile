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

# Virtual Environment
VIRTUALENV_DIR ?= virtualenv
ORQUESTA_DIR ?= $(VIRTUALENV_DIR)/orquesta
ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

# Run all targets
.PHONY: all
all: virtualenv orquesta requirements

.PHONY: clean
clean:
	rm -rf $(VIRTUALENV_DIR)
	rm -rf requirements-orquesta.txt
	find $(ROOT_DIR) -name 'virtualenv' -prune -or -name '.git' -or -type f -name "*.pyc" -print | xargs --no-run-if-empty rm 

.PHONY: virtualenv
virtualenv:
	test -d $(VIRTUALENV_DIR) || virtualenv --no-site-packages $(VIRTUALENV_DIR)
	# Setup PYTHONPATH in bash activate script...
	# Delete existing entries (if any)
	sed -i '/_OLD_PYTHONPATHp/d' $(VIRTUALENV_DIR)/bin/activate
	sed -i '/PYTHONPATH=/d' $(VIRTUALENV_DIR)/bin/activate
	sed -i '/export PYTHONPATH/d' $(VIRTUALENV_DIR)/bin/activate
	echo '_OLD_PYTHONPATH=$$PYTHONPATH' >> $(VIRTUALENV_DIR)/bin/activate
	echo 'PYTHONPATH=${ROOT_DIR}' >> $(VIRTUALENV_DIR)/bin/activate
	echo 'export PYTHONPATH' >> $(VIRTUALENV_DIR)/bin/activate
	touch $(VIRTUALENV_DIR)/bin/activate

.PHONY: orquesta
orquesta: virtualenv
	test -d $(ORQUESTA_DIR) || git clone "https://github.com/StackStorm/orquesta" $(ORQUESTA_DIR)
	cp $(ORQUESTA_DIR)/requirements.txt requirements-orquesta.txt

.PHONY: requirements
requirements: virtualenv
	$(VIRTUALENV_DIR)/bin/pip install -r requirements.txt
	$(VIRTUALENV_DIR)/bin/pip install -r requirements-orquesta.txt
