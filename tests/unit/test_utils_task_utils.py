from tests.base_test_case import BaseTestCase

from orquestaconvert.utils import task_utils


class TestTaskUtils(BaseTestCase):
    __test__ = True

    def test_convert_dashes_to_underscores(self):
        self.assertEqual(task_utils.translate_task_name('foo-bar-baz'), 'foo_bar_baz')
        self.assertEqual(task_utils.translate_task_name('baz_foo'), 'baz_foo')
