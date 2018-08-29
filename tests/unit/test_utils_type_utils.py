from base_test_case import BaseActionTestCase

from orquestaconvert.utils import type_utils

import ruamel.yaml


class TestTypeUtils(BaseActionTestCase):
    __test__ = True

    def test_dict_types(self):
        self.assertIsInstance({}, type_utils.dict_types)
        self.assertIsInstance(ruamel.yaml.comments.CommentedMap(), type_utils.dict_types)
