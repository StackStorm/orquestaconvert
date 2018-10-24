from __future__ import print_function

import filecmp
import hashlib
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

    def _hash_directory(self, directory, files):
        '''
        Hash files in a directory for comparison, returns a dictinary of hashes
        '''
        dirhash = {}
        for dirf in files:
            with open(os.path.join(directory, dirf), 'r') as f:
                dirhash[dirf] = hashlib.sha256(f.read()).hexdigest()
        return dirhash

    def _validate_dirs(self, dir1, dir2):
        '''Make sure the directories are the same'''
        dirdiff = filecmp.dircmp(dir1, dir2)

        for diff_file in dirdiff.diff_files:
            print(os.system("diff {} {}".format(
                os.path.join(m_actions_dir, diff_file),
                os.path.join(o_actions_dir, diff_file),
            )))

        self.assertEqual(dirdiff.diff_files, [])
        self.assertEqual(dirdiff.funny_files, [])

    def test_list_mistral_workflows_in_pack(self):
        args = ['--list-workflows=mistral-v2', '--actions-dir={}'.format(m_actions_dir)]
        self.pack_client.run(args, client=self.client)

        out = self.stdout.getvalue()

        self.assertEqual(len([line for line in out.split('\n') if line]), 2)
        self.assertIn('tests/fixtures/pack/actions/mistral-test-cancel.yaml'
                      ' --> '
                      'tests/fixtures/pack/actions/workflows/mistral-test-cancel.yaml\n',
                      out)
        self.assertIn('tests/fixtures/pack/actions/mistral-repeat.yaml'
                      ' --> '
                      'tests/fixtures/pack/actions/workflows/mistral-repeat.yaml\n',
                      out)
        self.assertEqual(self.stderr.getvalue(), '')

        self._validate_dirs(p_actions_dir, m_actions_dir)

    def test_list_orquesta_workflows_in_mistral_directory(self):
        args = ['--list-workflows=orquesta', '--actions-dir={}'.format(m_actions_dir)]
        self.pack_client.run(args, client=self.client)

        self.assertEqual(self.stdout.getvalue(), '')
        self.assertEqual(self.stderr.getvalue(), '')

        self._validate_dirs(p_actions_dir, m_actions_dir)

    def test_list_orquesta_workflows_in_pack(self):
        args = ['--list-workflows=orquesta', '--actions-dir={}'.format(o_actions_dir)]
        self.pack_client.run(args, client=self.client)

        self.assertEqual(self.stdout.getvalue(),
                         'tests/fixtures/pack/o_actions/mistral-test-cancel.yaml'
                         ' --> '
                         'tests/fixtures/pack/o_actions/workflows/mistral-test-cancel.yaml\n')
        self.assertEqual(self.stderr.getvalue(), '')

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

    def test_validate_nothing(self):
        args = ['--validate', '--actions-dir={}'.format(m_actions_dir)]
        result = self.pack_client.run(args, client=self.client)

        self.assertEqual(self.stdout.getvalue(), '')
        self.assertEqual(self.stderr.getvalue(), '')

        self.assertEqual(result, 0)

        self._validate_dirs(p_actions_dir, m_actions_dir)

    def test_validate_verbose_nothing(self):
        args = ['--validate', '--verbose', '--actions-dir={}'.format(m_actions_dir)]
        result = self.pack_client.run(args, client=self.client)

        self.assertEqual(self.stdout.getvalue(), '')
        self.assertEqual(self.stderr.getvalue(), '')

        self.assertEqual(result, 0)

        self._validate_dirs(p_actions_dir, m_actions_dir)

    def test_validate_orquesta(self):
        files = ['mistral-test-cancel.yaml', os.path.join('workflows', 'mistral-test-cancel.yaml')]
        before_dirhash = self._hash_directory(o_actions_dir, files)

        args = ['--validate', '--actions-dir={}'.format(o_actions_dir)]
        result = self.pack_client.run(args, client=self.client)

        after_dirhash = self._hash_directory(o_actions_dir, files)

        self.assertEqual(self.stdout.getvalue(), '')
        self.assertEqual(self.stderr.getvalue(), '')

        self.assertEqual(result, 0)

        self.assertEqual(before_dirhash, after_dirhash)

    def test_validate_verbose_orquesta(self):
        files = ['mistral-test-cancel.yaml', os.path.join('workflows', 'mistral-test-cancel.yaml')]
        before_dirhash = self._hash_directory(o_actions_dir, files)

        args = ['--validate', '--verbose', '--actions-dir={}'.format(o_actions_dir)]
        result = self.pack_client.run(args, client=self.client)

        after_dirhash = self._hash_directory(o_actions_dir, files)

        wf = os.path.join(o_actions_dir, 'workflows', 'mistral-test-cancel.yaml')
        self.assertEqual(
            self.stdout.getvalue(),
            'Successfully validated workflow from {}\n'.format(wf))
        self.assertEqual(self.stderr.getvalue(), '')

        self.assertEqual(result, 0)

        self.assertEqual(before_dirhash, after_dirhash)

    def test_validate_partially_converted_pack(self):
        self.test_partially_convert_pack()

        self.setup_captures()

        args = ['--validate', '--actions-dir={}'.format(m_actions_dir)]
        result = self.pack_client.run(args, client=self.client)

        self.assertEqual(self.stdout.getvalue(), '')
        self.assertEqual(self.stderr.getvalue(), '')

        self.assertEqual(result, 0)

        self._validate_dirs(m_actions_dir, o_actions_dir)

    def test_validate_verbose_partially_converted_pack(self):
        self.test_partially_convert_pack()

        self.setup_captures()

        args = ['--validate', '--verbose', '--actions-dir={}'.format(m_actions_dir)]
        result = self.pack_client.run(args, client=self.client)

        wf = os.path.join(m_actions_dir, 'workflows', 'mistral-test-cancel.yaml')
        self.assertEqual(
            self.stdout.getvalue(),
            'Successfully validated workflow from {}\n'.format(wf))
        self.assertEqual(self.stderr.getvalue(), '')

        self.assertEqual(result, 0)

        self._validate_dirs(m_actions_dir, o_actions_dir)
