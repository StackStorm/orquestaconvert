import hashlib
import json
import os
import shutil
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

    def setup_captures(self):
        if self.capture_output:
            # Make sure we reset it for each test class instance
            self.stdout = six.moves.StringIO()
            self.stderr = six.moves.StringIO()

            sys.stdout = self.stdout
            sys.stderr = self.stderr

    def reset_captures(self):
        if self.capture_output:
            # Reset to original stdout and stderr.
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

    def setUp(self):
        super(BaseCLITestCase, self).setUp()
        self.setup_captures()

    def tearDown(self):
        super(BaseCLITestCase, self).tearDown()
        self.reset_captures()


class BasePackClientRunTestCase(BaseCLITestCase):
    def setUp(self):
        super(BasePackClientRunTestCase, self).setUp()

        # The pristine actions directory - this is not touched
        self.p_actions_dir = os.path.join('tests', 'fixtures', 'pack', 'pristine_actions')
        # The Orquesta actions directory - this is not touched
        self.o_actions_dir = os.path.join('tests', 'fixtures', 'pack', 'o_actions')
        # The Mistral actions directory - this is a copy of pristine actions
        self.m_actions_dir = os.path.join('tests', 'fixtures', 'pack', 'actions')

        self.action_failing_files = [
            'mistral-fail-retry.yaml',
        ]
        self.action_passing_files = [
            'mistral-test-cancel.yaml',
            'mistral-with-items-jinja.yaml',
            'mistral-with-items-static-list.yaml',
            'mistral-with-items-yaql.yaml',
            'mistral-with-items-yaml-list.yaml',
            'mistral-with-items-yaql-list.yaml',
            'mistral-with-items-concurrency.yaml',
        ]
        self.action_files = self.action_failing_files + self.action_passing_files

        self.pristine_action_wfs = {
            os.path.join(self.p_actions_dir, af): os.path.join(self.p_actions_dir, 'workflows', af)
            for af in self.action_files
        }
        self.mistral_action_wfs = {
            os.path.join(self.m_actions_dir, af): os.path.join(self.m_actions_dir, 'workflows', af)
            for af in self.action_failing_files
        }
        self.orquesta_action_wfs = {
            os.path.join(self.o_actions_dir, af): os.path.join(self.o_actions_dir, 'workflows', af)
            for af in self.action_passing_files
        }
        self.action_wfs = {
            os.path.join(self.m_actions_dir, af): os.path.join(self.m_actions_dir, 'workflows', af)
            for af in (self.action_failing_files + self.action_passing_files)
        }

        self.maxDiff = None

        if os.path.isdir(self.m_actions_dir):
            shutil.rmtree(self.m_actions_dir)

        shutil.copytree(self.p_actions_dir, self.m_actions_dir)

    def tearDown(self):
        super(BasePackClientRunTestCase, self).tearDown()

        if os.path.isdir(self.m_actions_dir):
            shutil.rmtree(self.m_actions_dir)

    def _hash_directory(self, directory, files):
        '''
        Hash files in a directory for comparison, returns a dictinary of hashes
        '''
        dirhash = {}
        for dirf in files:
            with open(os.path.join(directory, dirf), 'r') as f:
                dirhash[dirf] = hashlib.sha256(f.read()).hexdigest()
        return dirhash
