from tests.base_test_case import BaseTestCase

from orquestaconvert.client import Client


class TestEndToEnd(BaseTestCase):
    __test__ = True

    def setUp(self):
        super(TestEndToEnd, self).setUp()
        self.client = Client()

    def e2e_from_file(self, wf_filename):
        fixture_path = self.get_fixture_path('mistral/' + wf_filename)
        result = self.client.convert_file(fixture_path)
        expected = self.get_fixture_content('orquesta/' + wf_filename)
        self.assertMultiLineEqual(result, expected)

    def test_e2e_nasa_apod_twitter_post(self):
        self.e2e_from_file('nasa_apod_twitter_post.yaml')

    def test_e2e_emptywee_test(self):
        with self.assertRaises(NotImplementedError):
            self.e2e_from_file('emptywee_test.yaml')

    def test_e2e_output_test(self):
        self.e2e_from_file('output_test.yaml')
