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
ORCHESTRA_DIR ?= $(VIRTUALENV_DIR)/orchestra

# Run all targets
.PHONY: all
all: virtualenv orchestra requirements

.PHONY: clean
clean:
	rm -rf $(VIRTUALENV_DIR)
	rm -rf requirements-orchestra.txt

.PHONY: virtualenv
virtualenv:
	test -d $(VIRTUALENV_DIR) || virtualenv --no-site-packages $(VIRTUALENV_DIR)

.PHONY: orchestra
orchestra: virtualenv
	test -d $(ORCHESTRA_DIR) || git clone "https://github.com/StackStorm/orchestra" $(ORCHESTRA_DIR)
	cp $(ORCHESTRA_DIR)/requirements.txt requirements-orchestra.txt

.PHONY: requirements
requirements: virtualenv
	$(VIRTUALENV_DIR)/bin/pip install -r requirements.txt
	$(VIRTUALENV_DIR)/bin/pip install -r requirements-orchestra.txt
