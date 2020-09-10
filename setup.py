# -*- coding: utf-8 -*-
# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
import os.path

from setuptools import setup, find_packages

from dist_utils import fetch_requirements
from dist_utils import apply_vagrant_workaround
from dist_utils import get_version_string

MODULE_NAME = 'orquestaconvert'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS_FILE = os.path.join(BASE_DIR, 'requirements.txt')
INIT_FILE = os.path.join(BASE_DIR, MODULE_NAME + '/__init__.py')

install_reqs, dep_links = fetch_requirements(REQUIREMENTS_FILE)

with open("README.md", "r") as fh:
    long_description = fh.read()

apply_vagrant_workaround()
setup(
    name=MODULE_NAME,
    version=get_version_string(INIT_FILE),
    description='Tool to convert OpenStack Mistral workflows to StackStorm Orquesta workflows',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='StackStorm',
    author_email='info@stackstorm.com',
    url='https://stackstorm.com/',
    install_requires=install_reqs,
    dependency_links=dep_links,
    test_suite=MODULE_NAME,
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(exclude=['setuptools', 'tests']),
    scripts=[
        'bin/orquestaconvert.sh',
        'bin/orquestaconvert-pack.sh',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Intended Audience :: Developers',
        'Environment :: Console',
    ],
)
