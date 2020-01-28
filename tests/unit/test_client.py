from tests.base_test_case import BaseCLITestCase

from orquestaconvert.client import Client

import mock


class TestClient(BaseCLITestCase):
    __test__ = True

    def setUp(self):
        super(TestClient, self).setUp()
        self.client = Client()
        self.maxDiff = 20000

    def _validate_args(self, args, filename, expected_filename=None):
        # path to fixture file
        fixture_path = self.get_fixture_path('mistral/' + filename)

        # run
        exit_status = Client().run(args + [fixture_path], self.stdout)
        self.assertEqual(exit_status, 0)

        # read expected data
        if not expected_filename:
            expected_filename = filename
        expected = self.get_fixture_content('orquesta/' + expected_filename)

        # compare
        self.stdout.seek(0)
        stdout = self.stdout.read()
        self.assertMultiLineEqual(stdout, expected)

    def test_run(self):
        self._validate_args([], 'nasa_apod_twitter_post.yaml')

    def test_run_jinja(self):
        self._validate_args(['-e', 'jinja'], 'nasa_apod_twitter_post.yaml')

    def test_run_yaql(self):
        self._validate_args(['-e', 'yaql'],
                            'nasa_apod_twitter_post_yaql.yaml',
                            'nasa_apod_twitter_post_yaql.yaml')

    def test_run_expression_jinja(self):
        self._validate_args(['--expression', 'jinja'], 'nasa_apod_twitter_post.yaml')

    def test_run_expression_yaql(self):
        self._validate_args(['--expression', 'yaql'],
                            'nasa_apod_twitter_post_yaql.yaml',
                            'nasa_apod_twitter_post_yaql.yaml')

    def test_validate_workflow_spec_raises(self):
        wf_spec = mock.MagicMock()
        wf_spec.inspect_syntax.return_value = "some error string"

        with self.assertRaises(ValueError):
            self.client.validate_workflow_spec(wf_spec)
