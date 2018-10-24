from __future__ import print_function

import os
import shutil

from tests.base_test_case import BaseTestCase

from orquestaconvert.pack_client import PackClient

import mock


p_actions_dir = os.path.join('tests', 'fixtures', 'pack', 'pristine_actions')
m_actions_dir = os.path.join('tests', 'fixtures', 'pack', 'actions')
o_actions_dir = os.path.join('tests', 'fixtures', 'pack', 'o_actions')


class PackClientTestCase(BaseTestCase):
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

    def test_get_mistral_workflow_files_in_p_dir(self):
        workflows = self.pack_client.get_workflow_files('mistral-v2', p_actions_dir)
        self.assertEqual(workflows, {
            os.path.join(p_actions_dir, a_f): os.path.join(p_actions_dir, 'workflows', a_f)
            for a_f in ['mistral-repeat.yaml', 'mistral-test-cancel.yaml']
        })

    def test_get_orquesta_workflow_files_in_p_dir(self):
        workflows = self.pack_client.get_workflow_files('orquesta', p_actions_dir)
        self.assertEqual(workflows, {})

    def test_get_orquesta_workflow_files_in_o_dir(self):
        workflows = self.pack_client.get_workflow_files('orquesta', o_actions_dir)
        a_f = 'mistral-test-cancel.yaml'
        self.assertEqual(workflows, {
            os.path.join(o_actions_dir, a_f): os.path.join(o_actions_dir, 'workflows', a_f)
        })

    def test_validate_nothing(self):
        args = ['--validate', '--actions-dir={}'.format(m_actions_dir)]
        result = self.pack_client.run(args, client=self.client)

        self.assertEqual(result, 0)

        self.assertEqual(self.client.run.call_count, 0)

    def test_validate_orquesta(self):
        args = ['--validate', '--actions-dir={}'.format(o_actions_dir)]
        result = self.pack_client.run(args, client=self.client)

        self.assertEqual(result, 0)

        self.assertEqual(self.client.run.call_count, 1)

        wf = os.path.join(o_actions_dir, 'workflows', 'mistral-test-cancel.yaml')
        self.assertEqual(self.client.run.call_args_list[0][0][0], ['--validate', wf])

    def test_convert_pack(self):
        args = ['-e', 'yaql', '--actions-dir={}'.format(m_actions_dir)]
        result = self.pack_client.run(args, client=self.client)

        self.assertEqual(result, 0)

        self.assertEqual(self.client.run.call_count, 2)
        expected = (
            ['-e', 'yaql', os.path.join(m_actions_dir, 'workflows/mistral-repeat.yaml')],
            ['-e', 'yaql', os.path.join(m_actions_dir, 'workflows/mistral-test-cancel.yaml')],
        )
        self.assertEqual(tuple([call_args[0][0] for call_args in self.client.run.call_args_list]),
                         expected)
