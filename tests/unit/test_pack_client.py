from __future__ import print_function

import filecmp
import os
import shutil

from tests.base_test_case import BaseCLITestCase

from orquestaconvert.pack_client import PackClient

import mock


p_actions_dir = os.path.join('tests', 'fixtures', 'pack', 'pristine_actions')
m_actions_dir = os.path.join('tests', 'fixtures', 'pack', 'actions')
o_actions_dir = os.path.join('tests', 'fixtures', 'pack', 'o_actions')


class PackClientTestCase(BaseCLITestCase):
    __test__ = True

    def setUp(self):
        super(PackClientTestCase, self).setUp()

        self.client = mock.MagicMock()
        self.client.run = mock.MagicMock(return_value=0)
        self.pack_client = PackClient()
        self.maxDiff = None

        if os.path.isdir(m_actions_dir):
            shutil.rmtree(m_actions_dir)

        shutil.copytree(p_actions_dir, m_actions_dir)

    def tearDown(self):
        super(PackClientTestCase, self).tearDown()

        if os.path.isdir(m_actions_dir):
            shutil.rmtree(m_actions_dir)

    def _validate_dirs(self, dir1, dir2):
        # Make sure the directories are the same
        dirdiff = filecmp.dircmp(dir1, dir2)

        self.assertEqual(dirdiff.diff_files, [])
        self.assertEqual(dirdiff.funny_files, [])

    def test_get_mistral_workflow_files_in_pack(self):
        workflows = self.pack_client.get_workflow_files('mistral-v2', m_actions_dir)
        self.assertEqual(workflows, {
            os.path.join(m_actions_dir, a_f): os.path.join(m_actions_dir, 'workflows', a_f)
            for a_f in ['mistral-repeat.yaml', 'mistral-test-cancel.yaml']
        })

        self._validate_dirs(p_actions_dir, m_actions_dir)

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

        self.assertEqual(self.client.run.call_count, 0)

        self._validate_dirs(p_actions_dir, m_actions_dir)

    def test_get_orquesta_workflow_files_in_mistral_directory(self):
        workflows = self.pack_client.get_workflow_files('orquesta', m_actions_dir)
        self.assertEqual(workflows, {})

        self._validate_dirs(p_actions_dir, m_actions_dir)

    def test_list_orquesta_workflows_in_mistral_directory(self):
        args = ['--list-workflows=orquesta', '--actions-dir={}'.format(m_actions_dir)]
        self.pack_client.run(args, client=self.client)

        self.assertEqual(self.stdout.getvalue(), '')
        self.assertEqual(self.stderr.getvalue(), '')

        self.assertEqual(self.client.run.call_count, 0)

        self._validate_dirs(p_actions_dir, m_actions_dir)

    def test_get_orquesta_workflow_files_in_pack(self):
        workflows = self.pack_client.get_workflow_files('orquesta', o_actions_dir)
        a_f = 'mistral-test-cancel.yaml'
        self.assertEqual(workflows, {
            os.path.join(o_actions_dir, a_f): os.path.join(o_actions_dir, 'workflows', a_f)
        })

    def test_list_orquesta_workflows_in_pack(self):
        args = ['--list-workflows=orquesta', '--actions-dir={}'.format(o_actions_dir)]
        self.pack_client.run(args, client=self.client)

        self.assertEqual(self.stdout.getvalue(),
                         'tests/fixtures/pack/o_actions/mistral-test-cancel.yaml'
                         ' --> '
                         'tests/fixtures/pack/o_actions/workflows/mistral-test-cancel.yaml\n')
        self.assertEqual(self.stderr.getvalue(), '')

        self.assertEqual(self.client.run.call_count, 0)

    def test_convert_pack(self):
        args = ['-e', 'yaql', '--actions-dir={}'.format(m_actions_dir)]
        result = self.pack_client.run(args, client=self.client)

        self.assertEqual(self.stdout.getvalue(), '')
        self.assertEqual(self.stderr.getvalue(), '')

        self.assertEqual(result, 0)

        self.assertEqual(self.client.run.call_count, 2)
        expected = (
            ['-e', 'yaql', os.path.join(m_actions_dir, 'workflows/mistral-repeat.yaml')],
            ['-e', 'yaql', os.path.join(m_actions_dir, 'workflows/mistral-test-cancel.yaml')],
        )
        self.assertEqual(tuple([call_args[0][0] for call_args in self.client.run.call_args_list]),
                         expected)
