import re

from tests.base_test_case import BaseTestCase

from orquestaconvert.expressions.mixed import MixedExpressionConverter


class TestExpressionsMixed(BaseTestCase):
    __test__ = True

    def test_convert_string(self):
        s = "ABC {{ _.test }}"
        result = MixedExpressionConverter.convert(s)
        self.assertEqual(result, "ABC {{ ctx().test }}")

    def test_convert_string_items(self):
        s = "i in {{ _.test1 }}<% $.test2 %>{{ _.test3 }}<% $.test4 %>"
        result = MixedExpressionConverter.convert(s, item_vars=['test1', 'test2'])
        expected = "i in {{ item(test1) }}<% item(test2) %>{{ ctx().test3 }}<% ctx().test4 %>"
        self.assertEqual(result, expected)

    def test_convert_dict(self):
        data = {
            "test1": "FOO {{ _.bar }}",
            "test2": "FOOBAR <% $.baz %>",
        }
        expected = {
            "test1": "FOO {{ ctx().bar }}",
            "test2": "FOOBAR <% ctx().baz %>",
        }
        result = MixedExpressionConverter.convert(data)
        self.assertEqual(expected, result)

    def test_convert_list(self):
        data = [
            "FOO {{ _.bar }}",
            "FOOBAR <% $.baz %>",
        ]
        expected = [
            "FOO {{ ctx().bar }}",
            "FOOBAR <% ctx().baz %>",
        ]
        result = MixedExpressionConverter.convert(data)
        self.assertEqual(expected, result)

    def test_convert_dict_of_lists_of_dicts(self):
        data = {
            "list1": [
                {
                    "key1": "FOO1 {{ _.bar }}",
                    "key2": "FOO2 {{ _.baz }}",
                },
                {
                    "key3": "FOO3 <% $.car %>",
                    "key4": "FOO4 <% $.caz %>",
                },
            ],
            "int1": 1,
            "bool1": False,
            "null1": None,
        }
        expected = {
            "list1": [
                {
                    "key1": "FOO1 {{ ctx().bar }}",
                    "key2": "FOO2 {{ ctx().baz }}",
                },
                {
                    "key3": "FOO3 <% ctx().car %>",
                    "key4": "FOO4 <% ctx().caz %>",
                },
            ],
            "int1": 1,
            "bool1": False,
            "null1": None,
        }
        result = MixedExpressionConverter.convert(data)
        self.assertItemsEqual(expected.keys(), result.keys())
        self.assertItemsEqual(expected['list1'][0].keys(), result['list1'][0].keys())
        self.assertItemsEqual(expected['list1'][0].values(), result['list1'][0].values())
        self.assertEqual(expected['int1'], result['int1'])
        self.assertEqual(expected['bool1'], result['bool1'])
        self.assertEqual(expected['null1'], result['null1'])

    def test_convert_expr_obj_raises_warning(self):
        expr_obj = object()
        expected_warning_regex = re.compile(
            r"Could not recognize expression '<object object at 0x[0-9a-f]+>'; "
            r"results may not be accurate.")
        with self.assertWarnsRegex(SyntaxWarning, expected_warning_regex):
            result = MixedExpressionConverter.convert(expr_obj)
        self.assertEqual(result, expr_obj)
