from __future__ import print_function

import filecmp
import os
import shutil

from tests.base_test_case import BaseCLITestCase

from orquestaconvert.client import Client
from orquestaconvert.pack_client import PackClient


p_actions_dir = os.path.join('tests', 'fixtures', 'pack', 'pristine_actions')
m_actions_dir = os.path.join('tests', 'fixtures', 'pack', 'actions')
o_actions_dir = os.path.join('tests', 'fixtures', 'pack', 'o_actions')


class PackClientRunTestCase(BaseCLITestCase):
    __test__ = True

    def setUp(self):
        super(PackClientRunTestCase, self).setUp()

        self.client = Client()
        self.pack_client = PackClient()
        self.maxDiff = None

        if os.path.isdir(m_actions_dir):
            shutil.rmtree(m_actions_dir)

        shutil.copytree(p_actions_dir, m_actions_dir)

    def tearDown(self):
        super(PackClientRunTestCase, self).tearDown()

        if os.path.isdir(m_actions_dir):
            shutil.rmtree(m_actions_dir)

    def _validate_dirs(self, dir1, dir2):
        # Make sure the directories are the same
        dirdiff = filecmp.dircmp(dir1, dir2)

        for diff_file in dirdiff.diff_files:
            print(os.system("diff {} {}".format(
                os.path.join(m_actions_dir, diff_file),
                os.path.join(o_actions_dir, diff_file),
            )))

        self.assertEqual(dirdiff.diff_files, [])
        self.assertEqual(dirdiff.funny_files, [])

    def test_partially_convert_pack(self):
        args = ['-e', 'yaql', '--actions-dir={}'.format(m_actions_dir)]
        result = self.pack_client.run(args, client=self.client)

        self.assertEqual(result, 1)

        self.assertEqual(self.stdout.getvalue(), '')
        self.assertEqual(
            self.stderr.getvalue(),
            "ERROR: Unable to convert all Mistral workflows.\n"
            "ISSUE: Task 'repeat' contains an attribute 'with-items' that is not supported in orquesta.\n"  # noqa: E501
            "Affected files:\n"
            "  - tests/fixtures/pack/actions/workflows/mistral-repeat.yaml\n"
            "\n"
        )

        m_actual_action = self.get_fixture_content('pack/actions/mistral-repeat.yaml')
        m_expected_action = self.get_fixture_content('pack/pristine_actions/mistral-repeat.yaml')

        self.assertEqual(m_actual_action, m_expected_action)

        m_actual_wf = self.get_fixture_content('pack/actions/workflows/mistral-repeat.yaml')
        m_expected_wf = self.get_fixture_content('pack/pristine_actions/workflows/mistral-repeat.yaml')  # noqa: E501

        self.assertEqual(m_actual_wf, m_expected_wf)

        o_actual_action = self.get_fixture_content('pack/actions/mistral-test-cancel.yaml')
        o_expected_action = self.get_fixture_content('pack/o_actions/mistral-test-cancel.yaml')

        self.assertEqual(o_actual_action, o_expected_action)

        o_actual_wf = self.get_fixture_content('pack/actions/workflows/mistral-test-cancel.yaml')
        o_expected_wf = self.get_fixture_content('pack/o_actions/workflows/mistral-test-cancel.yaml')  # noqa: E501

        self.assertEqual(o_actual_wf, o_expected_wf)

        self._validate_dirs(m_actions_dir, o_actions_dir)

    def test_completely_convert_pack(self):
        os.remove(os.path.join(m_actions_dir, 'mistral-repeat.yaml'))
        os.remove(os.path.join(m_actions_dir, 'workflows', 'mistral-repeat.yaml'))

        args = ['-e', 'yaql', '--actions-dir={}'.format(m_actions_dir)]
        result = self.pack_client.run(args, client=self.client)

        self.assertEqual(result, 0)

        self.assertEqual(self.stdout.getvalue(), '')
        self.assertEqual(self.stderr.getvalue(), '')

        actual = self.get_fixture_content('pack/actions/workflows/mistral-test-cancel.yaml')
        expected = self.get_fixture_content('pack/o_actions/workflows/mistral-test-cancel.yaml')

        self.assertEqual(actual, expected)

        self._validate_dirs(m_actions_dir, o_actions_dir)
