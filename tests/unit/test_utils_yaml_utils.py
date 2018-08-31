from tests.base_test_case import BaseTestCase

from orquestaconvert.utils import yaml_utils

import ruamel.yaml
OrderedMap = ruamel.yaml.comments.CommentedMap


class TestYamlUtils(BaseTestCase):
    __test__ = True

    def test_yaml_to_obj(self):
        yaml_str = ("test_dict:\n"
                    "  a: b\n"
                    "\n"
                    "test_list:\n"
                    "  - x\n"
                    "  - y\n")
        result = yaml_utils.yaml_to_obj(yaml_str)
        self.assertEquals(result, OrderedMap([
            ('test_dict', OrderedMap([
                ('a', 'b')
            ])),
            ('test_list', ['x', 'y'])
        ]))

    def test_read_yaml(self):
        fixture_path = self.get_fixture_path('yaml/simple.yaml')
        data, ruamel_data = yaml_utils.read_yaml(fixture_path)
        self.assertEquals(data, {'test_dict': {'a': True}})
        self.assertEquals(data, OrderedMap([
            ('test_dict', OrderedMap([
                ('a', True)
            ]))
        ]))

    def test_obj_to_yaml(self):
        ruamel_data = OrderedMap([
            ('test_dict', OrderedMap([
                ('a', True)
            ]))
        ])
        result = yaml_utils.obj_to_yaml(ruamel_data)
        self.assertEquals(result, self.get_fixture_content('yaml/simple.yaml'))

    def test_obj_to_yaml_dict(self):
        ruamel_data = {'test_dict': {'a': True}}
        result = yaml_utils.obj_to_yaml(ruamel_data)
        self.assertEquals(result, self.get_fixture_content('yaml/simple.yaml'))

    def test_obj_to_yaml_no_line_wrap(self):
        ruamel_data = {
            'key': ("this is some super super super long line that would normally cause"
                    " a line wrap when converting from dict to yaml. instead we don't want"
                    " to do that and just keep this one crazy long line.")
        }
        result = yaml_utils.obj_to_yaml(ruamel_data)
        self.assertEquals(result, self.get_fixture_content('yaml/no_line_wrap.yaml'))
