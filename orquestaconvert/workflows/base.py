import ruamel.yaml
import six

from orquestaconvert.expressions import ExpressionConverter
from orquestaconvert.expressions.base import BaseExpressionConverter
from orquestaconvert.expressions.jinja import JinjaExpressionConverter
from orquestaconvert.expressions.yaql import YaqlExpressionConverter
from orquestaconvert.utils import type_utils


class WorkflowConverter(object):

    def group_task_transitions(self, mistral_transition_list):
        expr_transitions = ruamel.yaml.comments.CommentedMap()
        simple_transitions = []
        for transition in mistral_transition_list:
            # if this is a string, then the transition is simply the name of the
            # next task
            if isinstance(transition, six.string_types):
                simple_transitions.append(transition)

            # if the transition is a dict, then it has an expression
            #  key = next task name
            #  value = conditional expression for when this transition should take place
            elif isinstance(transition, type_utils.dict_types):
                # group transitions by their common expression, this way we can keep
                # all of the transitions with the same expressions in the same
                # `when:` condition
                for task_name, expr in six.iteritems(transition):
                    if expr not in expr_transitions:
                        expr_transitions[expr] = []
                    expr_transitions[expr].append(task_name)
            else:
                raise ValueError('Task transition is not a "string" or "dict": {}  type={}'
                                 .format(transition, type(transition)))

        return simple_transitions, expr_transitions

    def dict_to_list(self, d):
        return [{k: v} for k, v in six.iteritems(d)]

    def convert_task_transition_simple(self, transitions, publish, orquesta_expr, expr_type):
        # if this is a simple name of a task:
        # on-success:
        #   - do_thing_a
        #   - do_thing_b
        #
        # this should produce the following in orquesta
        # next:
        #   - when: "{{ succeeded() }}"
        #     do:
        #       - do_thing_a
        #       - do_thing_b
        simple_transition = ruamel.yaml.comments.CommentedMap()

        # on-complete doesn't have an orquesta_expr, so we should not
        # add the 'when' clause in that case
        if orquesta_expr:
            simple_transition['when'] = expr_type.wrap_expression(orquesta_expr)

        # add in published variables
        if publish:
            publish_converted = ExpressionConverter.convert_dict(publish)
            simple_transition['publish'] = self.dict_to_list(publish_converted)

        # add in the transition list
        if transitions:
            simple_transition['do'] = transitions

        return simple_transition

    def convert_task_transition_expr(self, expression_list, orquesta_expr):
        # group all complex expressions by their common expression
        # this way we can keep all of the transitions with the same
        # expressions in the same `when:` condition
        #
        # on-success:
        #   - do_thing_a: "{{ _.x }}"
        #   - do_thing_b: "{{ _.x }}"
        #   - do_thing_c: "{{ not _.x }}"
        #
        # should produce the following in orquesta
        #
        # next:
        #   - when: "{{ succeeded() and _.x }}"
        #     do:
        #       - do_thing_a
        #       - do_thing_b
        #   - when: "{{ succeeded() and not _.x }}"
        #     do:
        #       - do_thing_c
        transitions = []
        for expr, task_list in six.iteritems(expression_list):
            expr_transition = ruamel.yaml.comments.CommentedMap()
            expr_converted = ExpressionConverter.convert(expr)

            # for some transitions (on-complete) the orquesta_expr may be empty
            # so only add it in, if it's necessary
            if orquesta_expr:
                converter = ExpressionConverter.get_converter(expr_converted)
                expr_converted = converter.unwrap_expression(expr_converted)
                o_expr = '{} and ({})'.format(orquesta_expr, expr_converted)
                o_expr = converter.wrap_expression(o_expr)
            else:
                o_expr = expr_converted

            expr_transition['when'] = o_expr
            expr_transition['do'] = task_list
            transitions.append(expr_transition)
        return transitions

    def convert_task_transitions(self, m_task_spec, expr_type):
        o_task_spec = ruamel.yaml.comments.CommentedMap()
        o_task_spec['next'] = []

        transitions = ruamel.yaml.comments.CommentedMap()
        transitions['on-success'] = ruamel.yaml.comments.CommentedMap()
        transitions['on-success']['publish'] = ruamel.yaml.comments.CommentedMap()
        transitions['on-success']['orquesta_expr'] = 'succeeded()'

        transitions['on-error'] = ruamel.yaml.comments.CommentedMap()
        transitions['on-error']['publish'] = ruamel.yaml.comments.CommentedMap()
        transitions['on-error']['orquesta_expr'] = 'failed()'

        transitions['on-complete'] = ruamel.yaml.comments.CommentedMap()
        transitions['on-complete']['publish'] = ruamel.yaml.comments.CommentedMap()
        transitions['on-complete']['orquesta_expr'] = None

        if m_task_spec.get('publish'):
            transitions['on-success']['publish'] = m_task_spec['publish']

        if m_task_spec.get('publish-on-error'):
            transitions['on-error']['publish'] = m_task_spec['publish']

        for m_transition_name, data in six.iteritems(transitions):
            m_transitions = m_task_spec.get(m_transition_name, [])
            trans_simple, trans_expr = self.group_task_transitions(m_transitions)

            # Create a transition for the simple task lists
            if data['publish'] or trans_simple:
                o_trans_simple = self.convert_task_transition_simple(trans_simple,
                                                                     data['publish'],
                                                                     data['orquesta_expr'],
                                                                     expr_type)
                o_task_spec['next'].append(o_trans_simple)

            # Create multiple transitions, one for each unique expression
            o_trans_expr_list = self.convert_task_transition_expr(trans_expr,
                                                                  data['orquesta_expr'])
            o_task_spec['next'].extend(o_trans_expr_list)

        return o_task_spec if o_task_spec['next'] else ruamel.yaml.comments.CommentedMap()

    def convert_tasks(self, mistral_wf_tasks, expr_type):
        orquesta_wf_tasks = ruamel.yaml.comments.CommentedMap()
        for task_name, m_task_spec in six.iteritems(mistral_wf_tasks):
            o_task_spec = ruamel.yaml.comments.CommentedMap()

            if m_task_spec.get('action'):
                o_task_spec['action'] = m_task_spec['action']

            if m_task_spec.get('join'):
                o_task_spec['join'] = m_task_spec['join']

            if m_task_spec.get('input'):
                o_task_spec['input'] = ExpressionConverter.convert_dict(m_task_spec['input'])

            o_task_transitions = self.convert_task_transitions(m_task_spec, expr_type)
            o_task_spec.update(o_task_transitions)

            orquesta_wf_tasks[task_name] = o_task_spec

        return orquesta_wf_tasks

    def convert(self, mistral_wf, expr_type=None):
        if expr_type is None:
            expr_type = JinjaExpressionConverter
        elif isinstance(expr_type, six.string_types):
            if expr_type == 'jinja':
                expr_type = JinjaExpressionConverter
            elif expr_type == 'yaql':
                expr_type = YaqlExpressionConverter
            else:
                raise ValueError("Unknown expression type: {}".format(expr_type))
        elif isinstance(expr_type, BaseExpressionConverter):
            pass
        else:
            raise ValueError("Unknown expression class type: {}".format(type(expr_type)))

        orquesta_wf = ruamel.yaml.comments.CommentedMap()
        orquesta_wf['version'] = '1.0'

        if mistral_wf.get('description'):
            orquesta_wf['description'] = mistral_wf['description']

        if mistral_wf.get('input'):
            orquesta_wf['input'] = ExpressionConverter.convert_list(mistral_wf['input'])

        if mistral_wf.get('vars'):
            orquesta_wf['vars'] = ExpressionConverter.convert_list(mistral_wf['vars'])

        if mistral_wf.get('output'):
            orquesta_wf['output'] = ExpressionConverter.convert_list(mistral_wf['output'])

        if mistral_wf.get('tasks'):
            o_tasks = self.convert_tasks(mistral_wf['tasks'], expr_type)
            if o_tasks:
                orquesta_wf['tasks'] = o_tasks

        return orquesta_wf
