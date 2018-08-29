from base_test_case import BaseActionTestCase

from orquestaconvert.expressions.jinja import JinjaExpressionConverter
from orquestaconvert.expressions.yaql import YaqlExpressionConverter
from orquestaconvert.workflows.base import WorkflowConverter

import ruamel.yaml
OrderedMap = ruamel.yaml.comments.CommentedMap


class TestWorkflows(BaseActionTestCase):
    __test__ = True

    def test_group_task_transitions(self):
        converter = WorkflowConverter()
        transitions_list = [
            "simple transition string",
            {"key": "expr"},
            "another simple transition string",
            {"key2": "expression"},
            {"key3": "expr"},
        ]
        simple, expr = converter.group_task_transitions(transitions_list)
        self.assertEquals(simple, ["simple transition string",
                                   "another simple transition string"])
        expected = OrderedMap([("expr", ["key", "key3"]),
                               ("expression", ["key2"])])
        self.assertEquals(expr, expected)

    def test_group_task_transitions_raises_bad_type(self):
        converter = WorkflowConverter()
        transitions_list = [["list is bad"]]
        with self.assertRaises(ValueError):
            converter.group_task_transitions(transitions_list)

    def test_dict_to_list(self):
        converter = WorkflowConverter()
        d = OrderedMap([('key1', 'value1'),
                        ('key2', 'value2'),
                        ('key3', 'value3')])
        result = converter.dict_to_list(d)
        self.assertEquals(result, [{'key1': 'value1'},
                                   {'key2': 'value2'},
                                   {'key3': 'value3'}])

    def test_convert_task_transition_simple(self):
        converter = WorkflowConverter()
        transitions = ['a', 'b', 'c']
        publish = OrderedMap([('key_plain', 'data'),
                              ('key_expr', '{{ _.test }}')])
        orquesta_expr = 'succeeded()'
        expr_converter = JinjaExpressionConverter()

        result = converter.convert_task_transition_simple(transitions,
                                                          publish,
                                                          orquesta_expr,
                                                          expr_converter)

        expected = OrderedMap([
            ('when', '{{ succeeded() }}'),
            ('publish', [
                {'key_plain': 'data'},
                {'key_expr': '{{ ctx().test }}'}
            ]),
            ('do', ['a', 'b', 'c']),
        ])
        self.assertEquals(result, expected)

    def test_convert_task_transition_simple_yaql(self):
        converter = WorkflowConverter()
        transitions = ['a', 'b', 'c']
        publish = OrderedMap([('key_plain', 'data'),
                              ('key_expr', '{{ _.test }}')])
        orquesta_expr = 'succeeded()'
        expr_converter = YaqlExpressionConverter()

        result = converter.convert_task_transition_simple(transitions,
                                                          publish,
                                                          orquesta_expr,
                                                          expr_converter)

        # note: only the orquesta_expr is converted using YAQL, the expressions
        #       in the rest are converted independently because they may each
        #       be a different type
        expected = OrderedMap([
            ('when', '<% succeeded() %>'),
            ('publish', [
                {'key_plain': 'data'},
                {'key_expr': '{{ ctx().test }}'}
            ]),
            ('do', ['a', 'b', 'c']),
        ])
        self.assertEquals(result, expected)

    def test_convert_task_transition_simple_no_orquesta_expr(self):
        converter = WorkflowConverter()
        transitions = ['a', 'b', 'c']
        publish = OrderedMap([('key_plain', 'data'),
                              ('key_expr', '{{ _.test }}')])
        orquesta_expr = None
        expr_converter = JinjaExpressionConverter()

        result = converter.convert_task_transition_simple(transitions,
                                                          publish,
                                                          orquesta_expr,
                                                          expr_converter)

        expected = OrderedMap([
            ('publish', [
                {'key_plain': 'data'},
                {'key_expr': '{{ ctx().test }}'}
            ]),
            ('do', ['a', 'b', 'c']),
        ])
        self.assertEquals(result, expected)

    def test_convert_task_transition_simple_no_publish(self):
        converter = WorkflowConverter()
        transitions = ['a', 'b', 'c']
        publish = None
        orquesta_expr = 'succeeded()'
        expr_converter = JinjaExpressionConverter()

        result = converter.convert_task_transition_simple(transitions,
                                                          publish,
                                                          orquesta_expr,
                                                          expr_converter)

        expected = OrderedMap([
            ('when', '{{ succeeded() }}'),
            ('do', ['a', 'b', 'c']),
        ])
        self.assertEquals(result, expected)

    def test_convert_task_transition_simple_no_transitions(self):
        converter = WorkflowConverter()
        transitions = None
        publish = OrderedMap([('key_plain', 'data'),
                              ('key_expr', '{{ _.test }}')])
        orquesta_expr = 'succeeded()'
        expr_converter = JinjaExpressionConverter()

        result = converter.convert_task_transition_simple(transitions,
                                                          publish,
                                                          orquesta_expr,
                                                          expr_converter)

        expected = OrderedMap([
            ('when', '{{ succeeded() }}'),
            ('publish', [
                {'key_plain': 'data'},
                {'key_expr': '{{ ctx().test }}'}
            ]),
        ])
        self.assertEquals(result, expected)

    def test_convert_task_transition_expr(self):
        converter = WorkflowConverter()
        expression_list = OrderedMap([('<% $.test %>', ['task1', 'task3']),
                                      ('{{ _.other }}', ['task2'])])
        orquesta_expr = 'succeeded()'

        result = converter.convert_task_transition_expr(expression_list,
                                                        orquesta_expr)

        expected = [
            OrderedMap([
                ('when', '<% succeeded() and (ctx().test) %>'),
                ('do', ['task1', 'task3']),
            ]),
            OrderedMap([
                ('when', '{{ succeeded() and (ctx().other) }}'),
                ('do', ['task2']),
            ]),
        ]
        self.assertEquals(result, expected)

    def test_convert_task_transition_expr_no_orquesta_expr(self):
        converter = WorkflowConverter()
        expression_list = OrderedMap([('<% $.test %>', ['task1', 'task3']),
                                      ('{{ _.other }}', ['task2'])])
        orquesta_expr = None

        result = converter.convert_task_transition_expr(expression_list,
                                                        orquesta_expr)

        expected = [
            OrderedMap([
                ('when', '<% ctx().test %>'),
                ('do', ['task1', 'task3']),
            ]),
            OrderedMap([
                ('when', '{{ ctx().other }}'),
                ('do', ['task2']),
            ]),
        ]
        self.assertEquals(result, expected)

    def test_default_task_transition_map(self):
        converter = WorkflowConverter()
        result = converter.default_task_transition_map()
        self.assertEquals(result, OrderedMap([
            ('on-success', OrderedMap([
                ('publish', OrderedMap()),
                ('orquesta_expr', 'succeeded()'),
            ])),
            ('on-error', OrderedMap([
                ('publish', OrderedMap()),
                ('orquesta_expr', 'failed()'),
            ])),
            ('on-complete', OrderedMap([
                ('publish', OrderedMap()),
                ('orquesta_expr', None),
            ])),
        ]))

    def test_convert_task_transitions(self):
        converter = WorkflowConverter()
        task_spec = OrderedMap([
            ('publish', OrderedMap([
                ('good_data', '{{ _.good }}'),
            ])),
            ('publish-on-error', OrderedMap([
                ('bad_data', '{{ _.bad }}'),
            ])),
            ('on-success', [
                OrderedMap([('do_thing_a', '{{ _.x }}')]),
                OrderedMap([('do_thing_b', '{{ _.x }}')])
            ]),
            ('on-error', [
                OrderedMap([('do_thing_error', '{{ _.e }}')]),
            ]),
            ('on-complete', [
                OrderedMap([('do_thing_sometimes', '{{ _.d }}')]),
                'do_thing_always'
            ]),
        ])
        expr_converter = JinjaExpressionConverter()
        result = converter.convert_task_transitions(task_spec, expr_converter)
        self.assertEquals(result, OrderedMap([
            ('next', [
                OrderedMap([
                    ('when', '{{ succeeded() }}'),
                    ('publish', [
                        {'good_data': '{{ ctx().good }}'}
                    ])
                ]),
                OrderedMap([
                    ('when', '{{ succeeded() and (ctx().x) }}'),
                    ('do', [
                        'do_thing_a',
                        'do_thing_b',
                    ])
                ]),
                OrderedMap([
                    ('when', '{{ failed() }}'),
                    ('publish', [
                        {'bad_data': '{{ ctx().bad }}'}
                    ])
                ]),
                OrderedMap([
                    ('when', '{{ failed() and (ctx().e) }}'),
                    ('do', [
                        'do_thing_error',
                    ])
                ]),
                OrderedMap([
                    ('do', [
                        'do_thing_always',
                    ])
                ]),
                OrderedMap([
                    ('when', '{{ ctx().d }}'),
                    ('do', [
                        'do_thing_sometimes',
                    ])
                ]),
            ]),
        ]))

    def test_convert_task_transitions_empty(self):
        converter = WorkflowConverter()
        task_spec = OrderedMap([])
        expr_converter = JinjaExpressionConverter()
        result = converter.convert_task_transitions(task_spec, expr_converter)
        self.assertEquals(result, OrderedMap([]))

    def test_convert_tasks(self):
        converter = WorkflowConverter()
        expr_converter = JinjaExpressionConverter()
        mistral_tasks = OrderedMap([
            ('jinja_task', OrderedMap([
                ('action', 'mypack.actionname'),
                ('input', OrderedMap([
                    ('cmd', '{{ _.test }}'),
                ])),
                ('on-success', ['next_task']),
            ]))
        ])
        result = converter.convert_tasks(mistral_tasks, expr_converter)
        self.assertEquals(result, OrderedMap([
            ('jinja_task', OrderedMap([
                ('action', 'mypack.actionname'),
                ('input', OrderedMap([
                    ('cmd', '{{ ctx().test }}'),
                ])),
                ('next', [
                    OrderedMap([
                        ('when', '{{ succeeded() }}'),
                        ('do', [
                            'next_task',
                        ])
                    ]),
                ]),
            ]))
        ]))

    def test_convert_tasks_yaql(self):
        converter = WorkflowConverter()
        expr_converter = YaqlExpressionConverter()
        mistral_tasks = OrderedMap([
            ('jinja_task', OrderedMap([
                ('action', 'mypack.actionname'),
                ('input', OrderedMap([
                    ('cmd', '<% $.test %>'),
                ])),
                ('on-success', ['next_task']),
            ]))
        ])
        result = converter.convert_tasks(mistral_tasks, expr_converter)
        self.assertEquals(result, OrderedMap([
            ('jinja_task', OrderedMap([
                ('action', 'mypack.actionname'),
                ('input', OrderedMap([
                    ('cmd', '<% ctx().test %>'),
                ])),
                ('next', [
                    OrderedMap([
                        ('when', '<% succeeded() %>'),
                        ('do', [
                            'next_task',
                        ])
                    ]),
                ]),
            ]))
        ]))

    def test_convert_tasks_join(self):
        converter = WorkflowConverter()
        expr_converter = YaqlExpressionConverter()
        mistral_tasks = OrderedMap([
            ('jinja_task', OrderedMap([
                ('action', 'mypack.actionname'),
                ('join', 'all'),
            ]))
        ])
        result = converter.convert_tasks(mistral_tasks, expr_converter)
        self.assertEquals(result, OrderedMap([
            ('jinja_task', OrderedMap([
                ('action', 'mypack.actionname'),
                ('join', 'all'),
            ]))
        ]))

    def test_expr_type_converter_none(self):
        expr_type = None
        converter = WorkflowConverter()
        result = converter.expr_type_converter(expr_type)
        self.assertIsInstance(result, JinjaExpressionConverter)

    def test_expr_type_converter_string_jinja(self):
        expr_type = 'jinja'
        converter = WorkflowConverter()
        result = converter.expr_type_converter(expr_type)
        self.assertIsInstance(result, JinjaExpressionConverter)

    def test_expr_type_converter_string_yaql(self):
        expr_type = 'yaql'
        converter = WorkflowConverter()
        result = converter.expr_type_converter(expr_type)
        self.assertIsInstance(result, YaqlExpressionConverter)

    def test_expr_type_converter_string_bad_raises(self):
        expr_type = 'junk'
        converter = WorkflowConverter()
        with self.assertRaises(ValueError):
            converter.expr_type_converter(expr_type)

    def test_expr_type_converter_class_jinja(self):
        expr_type = JinjaExpressionConverter()
        converter = WorkflowConverter()
        result = converter.expr_type_converter(expr_type)
        self.assertIs(result, expr_type)

    def test_expr_type_converter_class_yaql(self):
        expr_type = YaqlExpressionConverter()
        converter = WorkflowConverter()
        result = converter.expr_type_converter(expr_type)
        self.assertIs(result, expr_type)

    def test_expr_type_converter_class_bad_raises(self):
        expr_type = []
        converter = WorkflowConverter()
        with self.assertRaises(ValueError):
            converter.expr_type_converter(expr_type)

    def test_convert_empty(self):
        mistral_wf = {}
        converter = WorkflowConverter()
        result = converter.convert(mistral_wf)
        self.assertEquals(result, {'version': '1.0'})

    def test_convert_all(self):
        mistral_wf = OrderedMap([
            ('description', 'test description'),
            ('input', [
                'data',
                {'jinja_expr': "{{ _.test }}"},
                {'yaql_expr': "<% $.test %>"},
            ]),
            ('vars', [
                'var_data',
                {'var_expr_jinja': "{{ _.ex }}"},
                {'var_expr_yaql': "<% $.ex %>"},
            ]),
            ('output', OrderedMap([
                ('stdout', "{{ _.stdout }}"),
                ('stderr', "<% $.stderr %>"),
            ])),
            ('tasks', OrderedMap([
                ('jinja_task', OrderedMap([
                    ('action', 'mypack.actionname'),
                    ('input', OrderedMap([
                        ('cmd', '{{ _.test }}'),
                    ])),
                ])),
            ])),
        ])
        converter = WorkflowConverter()
        result = converter.convert(mistral_wf)

        self.assertEquals(result, OrderedMap([
            ('version', '1.0'),
            ('description', 'test description'),
            ('input', [
                'data',
                OrderedMap([
                    ('jinja_expr', "{{ ctx().test }}"),
                ]),
                OrderedMap([
                    ('yaql_expr', "<% ctx().test %>"),
                ]),
            ]),
            ('vars', [
                'var_data',
                OrderedMap([
                    ('var_expr_jinja', "{{ ctx().ex }}"),
                ]),
                OrderedMap([
                    ('var_expr_yaql', "<% ctx().ex %>"),
                ]),
            ]),
            ('output', OrderedMap([
                ('stdout', '{{ ctx().stdout }}'),
                ('stderr', '<% ctx().stderr %>'),
            ])),
            ('tasks', OrderedMap([
                ('jinja_task', OrderedMap([
                    ('action', 'mypack.actionname'),
                    ('input', OrderedMap([
                        ('cmd', '{{ ctx().test }}'),
                    ])),
                ])),
            ])),
        ]))