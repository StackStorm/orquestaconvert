# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from orquestaconvert.utils import task_utils

from tests import base_test_case


class TestTaskUtils(base_test_case.BaseTestCase):
    __test__ = True

    def test_convert_dashes_to_underscores(self):
        self.assertEqual(task_utils.translate_task_name('foo-bar-baz'), 'foo_bar_baz')
        self.assertEqual(task_utils.translate_task_name('baz_foo'), 'baz_foo')
