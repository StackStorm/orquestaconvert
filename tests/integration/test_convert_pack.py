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

from __future__ import print_function

import filecmp
import os
import six
import sys

from orquestaconvert import client
from orquestaconvert import pack_client

from tests import base_test_case


class PackClientRunTestCase(base_test_case.BasePackClientRunTestCase):
    __test__ = True

    def setUp(self):
        super(PackClientRunTestCase, self).setUp()

        self.client = client.Client()
        self.pack_client = pack_client.PackClient()

    def _validate_dirs(self, dir1, dir2):
        '''Make sure the directories are the same'''
        dirdiff = filecmp.dircmp(dir1, dir2)

        for diff_file in dirdiff.diff_files:
            sys.__stdout__.write(os.system("diff {} {}\n".format(
                os.path.join(self.m_actions_dir, diff_file),
                os.path.join(self.o_actions_dir, diff_file),
            )))

        self.assertEqual(dirdiff.diff_files, [])
        self.assertEqual(dirdiff.funny_files, [])

    def test_list_mistral_workflows_in_pack(self):
        args = ['--list-workflows=mistral-v2', '--actions-dir={}'.format(self.m_actions_dir)]
        self.pack_client.run(args, self.stdout, client=self.client)

        out = self.stdout.getvalue()

        self.assertEqual(len([line for line in out.split('\n') if line]), len(self.action_files))
        for action_file, wf_file in six.iteritems(self.action_wfs):
            self.assertIn('{action_file} --> {wf_file}\n'
                          .format(action_file=action_file, wf_file=wf_file),
                          out)
        self.assertEqual(self.stderr.getvalue(), '')

        self._validate_dirs(self.p_actions_dir, self.m_actions_dir)

    def test_list_orquesta_workflows_in_mistral_directory(self):
        args = ['--list-workflows=orquesta', '--actions-dir={}'.format(self.m_actions_dir)]
        self.pack_client.run(args, self.stdout, client=self.client)

        self.assertEqual(self.stdout.getvalue(), '')
        self.assertEqual(self.stderr.getvalue(), '')

        self._validate_dirs(self.p_actions_dir, self.m_actions_dir)

    def test_list_orquesta_workflows_in_pack(self):
        args = ['--list-workflows=orquesta', '--actions-dir={}'.format(self.o_actions_dir)]
        self.pack_client.run(args, self.stdout, client=self.client)

        out = self.stdout.getvalue()
        self.assertEqual(self.stderr.getvalue(), '')
        for action_file, wf_file in six.iteritems(self.orquesta_action_wfs):
            self.assertIn('{action_file} --> {wf_file}\n'
                          .format(action_file=action_file, wf_file=wf_file),
                          out)

    def test_partially_convert_pack(self):
        args = ['-e', 'yaql', '--actions-dir={}'.format(self.m_actions_dir)]
        result = self.pack_client.run(args, self.stdout, client=self.client)

        # Check the exit code
        self.assertEqual(1, result)

        # Check the stdout and stderr
        self.assertEqual(self.stdout.getvalue(), '')
        err = self.stderr.getvalue()
        self.assertIn("ERROR: Unable to convert all Mistral workflows.\n", err)
        self.assertIn(
            "Cannot convert continue-on (<% $.foo = 'continue' %>) and break-on "
            "({{{{ _.bar = \"BREAK\" }}}}) expressions that are different types in task "
            "'test-error-undo-retry'\n"
            "Affected files:\n"
            "  - {m_wfs_dir}/mistral-fail-retry-continue-and-break-on.yaml\n"
            "\n".format(m_wfs_dir=self.m_wfs_dir),
            err)

        # Check the failing actions failed conversion
        for action in self.action_failing_files:
            m_actual_action = self.get_fixture_content('pack/actions/{}'.format(action))
            m_expected_action = self.get_fixture_content('pack/pristine_actions/{}'.format(action))

            self.assertEqual(m_expected_action, m_actual_action)

            m_actual_wf = self.get_fixture_content('pack/actions/workflows/{}'.format(action))
            m_expected_wf = self.get_fixture_content('pack/pristine_actions/workflows/{}'
                                                     .format(action))

            self.assertEqual(m_expected_wf, m_actual_wf)

        # Check all of the remaining actions worked
        for o_action in self.action_passing_files:
            o_actual_action = self.get_fixture_content('pack/actions/{}'.format(o_action))
            o_expected_action = self.get_fixture_content('pack/o_actions/{}'.format(o_action))

            self.assertEqual(o_expected_action, o_actual_action)

            o_actual_wf = self.get_fixture_content('pack/actions/workflows/{}'.format(o_action))
            o_expected_wf = self.get_fixture_content('pack/o_actions/workflows/{}'.format(o_action))

            self.assertEqual(o_expected_wf, o_actual_wf)

        self._validate_dirs(self.m_actions_dir, self.o_actions_dir)

    def test_completely_convert_pack(self):
        for afile in self.action_failing_files:
            os.remove(os.path.join(self.m_actions_dir, afile))
            os.remove(os.path.join(self.m_wfs_dir, afile))

        args = ['-e', 'yaql', '--actions-dir={}'.format(self.m_actions_dir)]
        result = self.pack_client.run(args, self.stdout, client=self.client)

        self.assertEqual(0, result)

        self.assertEqual(self.stdout.getvalue(), '')
        self.assertEqual(self.stderr.getvalue(), '')

        for o_wf in self.action_passing_files:
            actual = self.get_fixture_content('pack/actions/workflows/{}'.format(o_wf))
            expected = self.get_fixture_content('pack/o_actions/workflows/{}'.format(o_wf))

            self.assertEqual(expected, actual)

        self._validate_dirs(self.m_actions_dir, self.o_actions_dir)

    def test_validate_nothing(self):
        args = ['--validate', '--actions-dir={}'.format(self.m_actions_dir)]
        result = self.pack_client.run(args, self.stdout, client=self.client)

        self.assertEqual(self.stdout.getvalue(), '')
        self.assertEqual(self.stderr.getvalue(), '')

        self.assertEqual(0, result)

        self._validate_dirs(self.p_actions_dir, self.m_actions_dir)

    def test_validate_verbose_nothing(self):
        args = ['--validate', '--verbose', '--actions-dir={}'.format(self.m_actions_dir)]
        result = self.pack_client.run(args, self.stdout, client=self.client)

        self.assertEqual(self.stdout.getvalue(), '')
        self.assertEqual(self.stderr.getvalue(), '')

        self.assertEqual(0, result)

        self._validate_dirs(self.p_actions_dir, self.m_actions_dir)

    def test_validate_orquesta(self):
        files = ['mistral-test-cancel.yaml', os.path.join('workflows', 'mistral-test-cancel.yaml')]
        before_dirhash = self._hash_directory(self.o_actions_dir, files)

        args = ['--validate', '--actions-dir={}'.format(self.o_actions_dir)]
        result = self.pack_client.run(args, self.stdout, client=self.client)

        after_dirhash = self._hash_directory(self.o_actions_dir, files)

        self.assertEqual(self.stdout.getvalue(), '')
        self.assertEqual(self.stderr.getvalue(), '')

        self.assertEqual(0, result)

        self.assertEqual(before_dirhash, after_dirhash)

    def test_validate_verbose_orquesta(self):
        files = ['mistral-test-cancel.yaml', os.path.join('workflows', 'mistral-test-cancel.yaml')]
        before_dirhash = self._hash_directory(self.o_actions_dir, files)

        args = ['--validate', '--verbose', '--actions-dir={}'.format(self.o_actions_dir)]
        result = self.pack_client.run(args, self.stdout, client=self.client)

        after_dirhash = self._hash_directory(self.o_actions_dir, files)

        self.assertEqual(0, result)

        self.assertEqual(self.stderr.getvalue(), '')

        out = self.stdout.getvalue()
        for action in self.action_passing_files:
            wf = os.path.join(self.o_wfs_dir, action)
            self.assertIn("Successfully validated workflow from {}\n".format(wf), out)

        self.assertEqual(before_dirhash, after_dirhash)

    def test_validate_partially_converted_pack(self):
        self.test_partially_convert_pack()

        self.setup_captures()

        args = ['--validate', '--actions-dir={}'.format(self.m_actions_dir)]
        result = self.pack_client.run(args, self.stdout, client=self.client)

        self.assertEqual(self.stdout.getvalue(), '')
        self.assertEqual(self.stderr.getvalue(), '')

        self.assertEqual(0, result)

        self._validate_dirs(self.m_actions_dir, self.o_actions_dir)

    def test_validate_verbose_partially_converted_pack(self):
        self.test_partially_convert_pack()

        self.setup_captures()

        args = ['--validate', '--verbose', '--actions-dir={}'.format(self.m_actions_dir)]
        result = self.pack_client.run(args, self.stdout, client=self.client)

        self.assertEqual(0, result)

        self.assertEqual(self.stderr.getvalue(), '')

        out = self.stdout.getvalue()
        for o_action in self.action_passing_files:
            o_wf = os.path.join(self.m_wfs_dir, o_action)
            self.assertIn("Successfully validated workflow from {}\n".format(o_wf), out)

        self._validate_dirs(self.m_actions_dir, self.o_actions_dir)
