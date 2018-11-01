from __future__ import print_function

from tests.base_test_case import BasePackClientRunTestCase

from orquestaconvert.pack_client import PackClient

import mock


class PackClientTestCase(BasePackClientRunTestCase):
    __test__ = True

    def setUp(self):
        super(PackClientTestCase, self).setUp()

        self.client = mock.MagicMock()
        self.client.run = mock.MagicMock(return_value=0)
        self.pack_client = PackClient()

    def test_get_mistral_workflow_files_in_p_dir(self):
        workflows = self.pack_client.get_workflow_files('mistral-v2', self.p_actions_dir)
        self.assertEqual(workflows, self.pristine_action_wfs)

    def test_get_orquesta_workflow_files_in_p_dir(self):
        workflows = self.pack_client.get_workflow_files('orquesta', self.p_actions_dir)
        self.assertEqual(workflows, {})

    def test_get_orquesta_workflow_files_in_o_dir(self):
        workflows = self.pack_client.get_workflow_files('orquesta', self.o_actions_dir)
        self.assertEqual(self.orquesta_action_wfs, workflows)

    def test_validate_nothing(self):
        args = ['--validate', '--actions-dir={}'.format(self.m_actions_dir)]
        result = self.pack_client.run(args, self.stdout, client=self.client)

        self.assertEqual(result, 0)

        self.assertEqual(self.client.run.call_count, 0)

    def test_validate_orquesta(self):
        args = ['--validate', '--actions-dir={}'.format(self.o_actions_dir)]
        result = self.pack_client.run(args, self.stdout, client=self.client)

        self.assertEqual(result, 0)

        self.assertEqual(self.client.run.call_count, 7)

        calls = [
            mock.call(['--validate', wf], self.stdout)
            for wf in self.orquesta_action_wfs.values()
        ]
        self.client.run.assert_has_calls(calls, any_order=True)

    def test_convert_pack(self):
        args = ['-e', 'yaql', '--actions-dir={}'.format(self.m_actions_dir)]
        result = self.pack_client.run(args, self.stdout, client=self.client)

        self.assertEqual(result, 0)

        self.assertEqual(self.client.run.call_count, len(self.action_files))

        expected = [
            ['-e', 'yaql', wf]
            for wf in self.action_wfs.values()
        ]
        self.assertItemsEqual([call_args[0][0] for call_args in self.client.run.call_args_list],
                              expected)
