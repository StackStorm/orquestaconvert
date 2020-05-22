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
import os
import re
import sys

from distutils.version import StrictVersion

GET_PIP = 'curl https://bootstrap.pypa.io/get-pip.py | python'

try:
    import pip
except ImportError as e:
    print('Failed to import pip: %s' % (str(e)))
    print('')
    print('Download pip:\n%s' % (GET_PIP))
    sys.exit(1)

__all__ = [
    'check_pip_version',
    'fetch_requirements',
    'apply_vagrant_workaround',
    'get_version_string',
    'parse_version_string'
]


def check_pip_version(min_version='6.0.0'):
    """
    Ensure that a minimum supported version of pip is installed.
    """
    if StrictVersion(pip.__version__) < StrictVersion(min_version):
        print("Upgrade pip, your version '{0}' "
              "is outdated. Minimum required version is '{1}':\n{2}".format(pip.__version__,
                                                                            min_version,
                                                                            GET_PIP))
        sys.exit(1)


def fetch_requirements(requirements_file_path):
    """
    Return a list of requirements and links by parsing the provided requirements file.
    """
    links = []
    reqs = []

    def _get_link(line):
        vcs_prefixes = ['git+', 'svn+', 'hg+', 'bzr+']

        for vcs_prefix in vcs_prefixes:
            if line.startswith(vcs_prefix) or line.startswith('-e %s' % (vcs_prefix)):
                req_name = re.findall('.*#egg=(.+)([&|@]).*$', line)

                if not req_name:
                    req_name = re.findall('.*#egg=(.+?)$', line)
                else:
                    req_name = req_name[0]

                if not req_name:
                    raise ValueError('Line "%s" is missing "#egg=<package name>"' % (line))

                link = line.replace('-e ', '').strip()
                return link, req_name[0]

        return None, None

    with open(requirements_file_path, 'r') as fp:
        for line in fp.readlines():
            line = line.strip()

            if line.startswith('#') or not line:
                continue

            link, req_name = _get_link(line=line)

            if link:
                links.append(link)
            else:
                req_name = line

                if ';' in req_name:
                    req_name = req_name.split(';')[0].strip()

            reqs.append(req_name)

    return (reqs, links)


def apply_vagrant_workaround():
    """
    Function which detects if the script is being executed inside vagrant and if it is, it deletes
    "os.link" attribute.
    Note: Without this workaround, setup.py sdist will fail when running inside a shared directory
    (nfs / virtualbox shared folders).
    """
    if os.environ.get('USER', None) == 'vagrant':
        del os.link


def get_version_string(init_file):
    """
    Read __version__ string for an init file.
    """

    with open(init_file, 'r') as fp:
        content = fp.read()
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                                  content, re.M)
        if version_match:
            return version_match.group(1)

        raise RuntimeError('Unable to find version string in %s.' % (init_file))


# alias for get_version_string
parse_version_string = get_version_string
