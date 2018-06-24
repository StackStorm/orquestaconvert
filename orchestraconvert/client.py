#!/usr/bin/env python

import argparse
import json
import os
import ruamel.yaml
import six
import sys
import StringIO
import yaml

from orchestra.specs.mistral.v2 import workflows as mistral_workflow
from orchestra.specs.native.v1 import models as orchestra_workflow

from orchestraconvert import expressions

# hard coded for testing
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
MISTRAL_WF_PATH = os.path.join(SCRIPT_DIR, 'test/fixtures/mistral/nasa_apod_twitter_post.yaml')

def parse_args():
    parser = argparse.ArgumentParser(description='Convert Mistral workflows to Orchestra')
    parser.add_argument('filename', metavar='FILENAME', nargs=1,
                        help='Path to the Mistral Workflow YAML file to convert')
    return parser.parse_args()


def read_yaml(yaml_filename):
    with open(yaml_filename, 'r') as stream:
        return yaml.safe_load(stream)

def obj_to_yaml(obj, indent=4):
    # use this different library because PyYAML doesn't handle indenting properly
    ruyaml = ruamel.yaml.YAML()
    ruyaml.explicit_start = True
    # this crazyness basically sets indents to 'indent'
    # 'sequence' is always supposed to be 'offset' + 2
    ruyaml.indent(mapping=indent, sequence=(indent + 2), offset=indent)
    stream = StringIO.StringIO()
    ruyaml.dump(obj, stream)
    return stream.getvalue()

def validate_workflow_spec(wf_spec):
    result = wf_spec.inspect_syntax()
    if result:
        raise ValueError(result)

def group_task_transitions(mistral_transition_list):
    expr_transitions = {}
    simple_transitions = []
    for transition in mistral_transition_list:
        # if this is a string, then the transition is simply the name of the
        # next task
        if isinstance(transition, six.string_types):
            simple_transitions.append(transition)

        # if the transition is a dict, then it has an expression
        #  key = next task name
        #  value = conditional expression for when this transition should take place
        elif isinstance(transition, dict):
            # group transitions by their common expression, this way we can keep
            # all of the transitions with the same expressions in the same
            # `when:` condition
            for task_name, expr in six.iteritems(transition):
                if expr not in expr_transitions:
                    expr_transitions[expr] = []
                expr_transitions[expr].append(task_name)
        else:
            raise ValueError('Task transition is not a "string" or "dict": {}'
                             .format(transition))

    return simple_transitions, expr_transitions

def dict_to_list(d):
    return [{k: v} for k, v in six.iteritems(d)]

def convert_workflow_task_transition_simple(transitions, publish, orchestra_expr):
    # if this is a simple name of a task:
    # on-success:
    #   - do_thing_a
    #   - do_thing_b
    #
    # this should produce the following in orchestra
    # next:
    #   - when: "{{ succeeded() }}"
    #     do:
    #       - do_thing_a
    #       - do_thing_b
    simple_transition = {}

    # on-complete doesn't have an orchestra_expr, so we should not
    # add the 'when' clause in that case
    if orchestra_expr:
        simple_transition['when'] = '{{ ' + orchestra_expr + ' }}'

    # add in published variables
    if publish:
        publish_converted = expressions.convert_expression_dict(publish)
        simple_transition['publish'] = dict_to_list(publish_converted)

    # add in the transition list
    if transitions:
        simple_transition['do'] = transitions

    return simple_transition

def convert_workflow_task_transition_expr(expression_list, orchestra_expr):
    # group all complex expressions by their common expression
    # this way we can keep all of the transitions with the same
    # expressions in the same `when:` condition
    #
    # on-success:
    #   - do_thing_a: "{{ _.x }}"
    #   - do_thing_b: "{{ _.x }}"
    #   - do_thing_c: "{{ not _.x }}"
    #
    # should produce the following in orchestra
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
        expr_transition = {}
        expr_converted = expressions.convert_expression(expr)

        # for some transitions (on-complete) the orchestra_expr may be empty
        # so only add it in, if it's necessary
        if orchestra_expr:
            o_expr = '{} and {}'.format(orchestra_expr, expr_converted)
        else:
            o_expr = expr_converted

        expr_transition['when'] = '{{ ' + o_expr + ' }}'
        expr_transition['do'] = task_list
        transitions.append(expr_transition)
    return transitions

def convert_workflow_task_transitions(m_task_spec):
    o_task_spec = {'next': []}

    transitions = {
        'on-success': {
            'publish': {},
            'orchestra_expr': 'succeeded()'
        },
        'on-error': {
            'publish': {},
            'orchestra_expr': 'failed()'
        },
        'on-complete': {
            'publish': {},
            'orchestra_expr': None
        },
    }

    if m_task_spec.get('publish'):
        transitions['on-success']['publish'] = m_task_spec['publish']

    if m_task_spec.get('publish-on-error'):
        transitions['on-error']['publish'] = m_task_spec['publish']

    for m_transition_name, data in six.iteritems(transitions):
        m_transitions = m_task_spec.get(m_transition_name, [])
        trans_simple, trans_expr = group_task_transitions(m_transitions)

        # Create a transition for the simple task lists
        if data['publish'] or trans_simple:
            o_trans_simple = convert_workflow_task_transition_simple(trans_simple,
                                                                     data['publish'],
                                                                     data['orchestra_expr'])
            o_task_spec['next'].append(o_trans_simple)

        # Create multiple transitions, one for each unique expression
        o_trans_expr_list = convert_workflow_task_transition_expr(trans_expr,
                                                                  data['orchestra_expr'])
        o_task_spec['next'].extend(o_trans_expr_list)

    return o_task_spec if o_task_spec['next'] else {}

def convert_workflow_tasks(mistral_wf_tasks):
    orchestra_wf_tasks = {}
    for task_name, m_task_spec in six.iteritems(mistral_wf_tasks):
        o_task_spec = {}

        if m_task_spec.get('action'):
            o_task_spec['action'] = m_task_spec['action']

        if m_task_spec.get('input'):
            o_task_spec['input'] = expressions.convert_expression_dict(m_task_spec['input'])

        o_task_transitions = convert_workflow_task_transitions(m_task_spec)
        o_task_spec.update(o_task_transitions)

        orchestra_wf_tasks[task_name] = o_task_spec

    return orchestra_wf_tasks

def convert_workflow(mistral_wf):
    orchestra_wf = {'version': '1.0'}

    if mistral_wf.get('description'):
        orchestra_wf['description'] = mistral_wf['description']

    if mistral_wf.get('input'):
        orchestra_wf['input'] = expressions.convert_expression_list(mistral_wf['input'])

    if mistral_wf.get('vars'):
        orchestra_wf['vars'] = expressions.convert_expression_list(mistral_wf['vars'])

    if mistral_wf.get('output'):
        orchestra_wf['output'] = expressions.convert_expression_list(mistral_wf['output'])

    if mistral_wf.get('tasks'):
        o_tasks = convert_workflow_tasks(mistral_wf['tasks'])
        if o_tasks:
            orchestra_wf['tasks'] = o_tasks

    return orchestra_wf

def run():
    args = parse_args()
    for f in args.filename:
        # parse the Mistral workflow from file
        mistral_wf_data = read_yaml(f)

        # validate the Mistral workflow before we start
        mistral_wf_spec = mistral_workflow.instantiate(mistral_wf_data)
        validate_workflow_spec(mistral_wf_spec)

        # convert Mistral -> Orchestra
        orchestra_wf_data = convert_workflow(mistral_wf_spec.spec)

        # validate we've generated a proper Orchestra workflow
        orchestra_wf_spec = orchestra_workflow.instantiate(orchestra_wf_data)
        validate_workflow_spec(orchestra_wf_spec)

        # write out the new Orchestra workflow
        print obj_to_yaml(orchestra_wf_spec.spec)
    return 0
