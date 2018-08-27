import json
import os
import unittest
import yaml


class BaseActionTestCase(unittest.TestCase):
    __test__ = False

    def get_fixture_content(self, fixture_path):
        """
        Return raw fixture content for the provided fixture path.
        :param fixture_path: Fixture path relative to the tests/fixtures/ directory.
        :type fixture_path: ``str``
        """
        base_path = self._get_base_path()
        fixtures_path = os.path.join(base_path, 'tests/fixtures/')
        fixture_path = os.path.join(fixtures_path, fixture_path)

        with open(fixture_path, 'r') as fp:
            content = fp.read()

        return content

    def _get_base_path(self):
        base_path = os.path.join(os.path.dirname(__file__), '..')
        base_path = os.path.abspath(base_path)
        return base_path

    def setUp(self):
        super(BaseActionTestCase, self).setUp()

    def load_yaml(self, filename):
        return yaml.safe_load(self.get_fixture_content(filename))

    def load_json(self, filename):
        return json.loads(self.get_fixture_content(filename))
