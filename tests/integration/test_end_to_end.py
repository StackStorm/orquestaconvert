import six
import warnings

from tests.base_test_case import BaseTestCase

from orquestaconvert.client import Client


class TestEndToEnd(BaseTestCase):
    __test__ = True

    def setUp(self):
        super(TestEndToEnd, self).setUp()
        self.maxDiff = 20000
        self.client = Client()
        parser = self.client.parser()
        # Ensure that the client has an args attribute
        self.client.args = parser.parse_args(['file.yaml'])

    def e2e_from_file(self, m_wf_filename, o_wf_filename=None):
        if o_wf_filename is None:
            o_wf_filename = m_wf_filename
        fixture_path = self.get_fixture_path('mistral/' + m_wf_filename)
        result = self.client.convert_file(fixture_path)
        expected = self.get_fixture_content('orquesta/' + o_wf_filename)
        self.assertMultiLineEqual(result, expected)

    def test_e2e_force_option(self):
        parser = self.client.parser()
        self.client.args = parser.parse_args(['--force', 'file.yaml'])
        self.e2e_from_file('unsupported_attributes.yaml',
                           '../broken/unsupported_attributes.yaml')

    def test_e2e_nasa_apod_twitter_post(self):
        self.e2e_from_file('nasa_apod_twitter_post.yaml')

    def test_e2e_emptywee_test(self):
        with self.assertRaises(NotImplementedError):
            self.e2e_from_file('emptywee_test.yaml')

    def test_e2e_output_test(self):
        self.e2e_from_file('output_test.yaml')

    def test_e2e_transition_strings_test(self):
        self.e2e_from_file('transition_strings.yaml')

    def test_e2e_boolean_publish_parameters(self):
        self.e2e_from_file('boolean_publish_parameters.yaml')

    def test_e2e_null_publish_parameters(self):
        self.e2e_from_file('null_publish_parameters.yaml')

    def test_e2e_int_publish_parameters(self):
        self.e2e_from_file('int_publish_parameters.yaml')

    def test_e2e_convert_dashes_in_task_names_to_underscores(self):
        self.e2e_from_file('dashes_in_task_names.yaml')

    def test_e2e_immediately_referenced_context_variables(self):
        with warnings.catch_warnings(record=True) as ws:
            self.e2e_from_file('immediately_referenced_context_variables.yaml')

            self.assertGreater(len(ws), 0)
            expected_warning = (
                "The transition \"{{ succeeded() and (ctx().operations) }}\" "
                "in task_1 references the 'operations' context variable, which "
                "is published in the same transition. You will need to "
                "manually convert the operations expression in the transition.")
            if six.PY2:
                self.assertEqual(expected_warning, ws[0].message.message)
            else:
                self.assertEqual(expected_warning, str(ws[0].message))
