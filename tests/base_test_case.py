import hashlib
import json
import os
import shutil
import six
import sys
import unittest2
import yaml


# The pristine actions directory - this is not touched, simply copied as the
# Mistral actions directory
P_ACTIONS_DIR = os.path.join('tests', 'fixtures', 'pack', 'pristine_actions')
# The Orquesta actions directory - this is not touched, this is used to compare
# autoconverted results against - autoconverted files should match files in
# this directory
O_ACTIONS_DIR = os.path.join('tests', 'fixtures', 'pack', 'o_actions')
# The Mistral actions directory - this is a copy of the pristine actions
# directory, and files within get mangled by the autoconvert script, then
# compared against files in the Orquesta actions directory
M_ACTIONS_DIR = os.path.join('tests', 'fixtures', 'pack', 'actions')

# These files should fail autoconversion
ACTION_FAILING_FILES = [
    'mistral-fail-retry-continue-and-break-on.yaml',
]
# All of these files should be successfully converted
ACTION_PASSING_FILES = [
    'mistral-test-cancel.yaml',
    'mistral-with-items-jinja.yaml',
    'mistral-with-items-static-list.yaml',
    'mistral-with-items-mixed-list.yaml',
    'mistral-with-items-yaql.yaml',
    'mistral-with-items-yaml-list.yaml',
    'mistral-with-items-yaql-list.yaml',
    'mistral-with-items-concurrency.yaml',
    'mistral-with-items-concurrency-str.yaml',
    'mistral-with-items-concurrency-jinja.yaml',
    'mistral-with-items-concurrency-yaql.yaml',
    'mistral-transition-expressions.yaml',
    'mistral-publish-only-transitions.yaml',
    'mistral-retry.yaml',
    'mistral-retry-continue-on.yaml',
    'mistral-retry-break-on.yaml',
    'mistral-retry-continue-and-break-on.yaml',
]


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
        self.p_actions_dir = P_ACTIONS_DIR
        # The Orquesta actions directory - this is not touched
        self.o_actions_dir = O_ACTIONS_DIR
        # The Mistral actions directory - this is a copy of pristine actions
        self.m_actions_dir = M_ACTIONS_DIR

        self.action_failing_files = ACTION_FAILING_FILES
        self.action_passing_files = ACTION_PASSING_FILES
        self.action_files = self.action_failing_files + self.action_passing_files

        self.p_wfs_dir = os.path.join(self.p_actions_dir, 'workflows')
        self.o_wfs_dir = os.path.join(self.o_actions_dir, 'workflows')
        self.m_wfs_dir = os.path.join(self.m_actions_dir, 'workflows')

        self.pristine_action_wfs = {
            os.path.join(self.p_actions_dir, af): os.path.join(self.p_wfs_dir, af)
            for af in self.action_files
        }
        self.mistral_action_wfs = {
            os.path.join(self.m_actions_dir, af): os.path.join(self.m_wfs_dir, af)
            for af in self.action_failing_files
        }
        self.orquesta_action_wfs = {
            os.path.join(self.o_actions_dir, af): os.path.join(self.o_wfs_dir, af)
            for af in self.action_passing_files
        }
        self.action_wfs = {
            os.path.join(self.m_actions_dir, af): os.path.join(self.m_wfs_dir, af)
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
                fdata = f.read()
                if not six.PY2:
                    fdata = fdata.encode('utf-8')
                dirhash[dirf] = hashlib.sha256(fdata).hexdigest()
        return dirhash
