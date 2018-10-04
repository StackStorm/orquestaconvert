import json
import os
import six
import sys
import unittest2
import yaml


class BaseTestCase(unittest2.TestCase):
    __test__ = False

    def get_fixture_content(self, filename):
        """
        Return raw fixture content for the provided fixture path.
        :param fixture_path: Fixture path relative to the tests/fixtures/ directory.
        :type fixture_path: ``str``
        """
        fixture_path = self.get_fixture_path(filename)
        with open(fixture_path, 'r') as fp:
            content = fp.read()
        return content

    def get_fixture_path(self, filename):
        base_path = self._get_base_path()
        fixtures_path = os.path.join(base_path, 'fixtures')
        return os.path.join(fixtures_path, filename)

    def _get_base_path(self):
        base_path = os.path.dirname(__file__)
        return os.path.abspath(base_path)

    def load_yaml(self, filename):
        return yaml.safe_load(self.get_fixture_content(filename))

    def load_json(self, filename):
        return json.loads(self.get_fixture_content(filename))


class BaseCLITestCase(BaseTestCase):
    capture_output = True  # if True, stdout and stderr are saved to self.stdout and self.stderr

    stdout = six.moves.StringIO()
    stderr = six.moves.StringIO()

    def setUp(self):
        super(BaseCLITestCase, self).setUp()

        if self.capture_output:
            # Make sure we reset it for each test class instance
            self.stdout = six.moves.StringIO()
            self.stderr = six.moves.StringIO()

            sys.stdout = self.stdout
            sys.stderr = self.stderr

    def tearDown(self):
        super(BaseCLITestCase, self).tearDown()

        if self.capture_output:
            # Reset to original stdout and stderr.
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
