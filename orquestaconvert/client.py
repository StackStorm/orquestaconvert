#!/usr/bin/env python

import argparse
import collections
import json
import os
import ruamel.yaml
import ruamel.yaml.comments
import six
import sys
import StringIO
import yaml
import yamlloader

from orquesta.specs.mistral.v2 import workflows as mistral_workflow
from orquesta.specs.native.v1 import models as orquesta_workflow

from orquestaconvert import expressions

# hard coded for testing
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
MISTRAL_WF_PATH = os.path.join(SCRIPT_DIR, 'test/fixtures/mistral/nasa_apod_twitter_post.yaml')


def parse_args():
    parser = argparse.ArgumentParser(description='Convert Mistral workflows to Orquesta')
    parser.add_argument('filename', metavar='FILENAME', nargs=1,
                        help='Path to the Mistral Workflow YAML file to convert')
    return parser.parse_args()


def read_yaml(yaml_filename):
    # parse data in a format that preserves ordering
    with open(yaml_filename, 'r') as stream:
        # safe load with ordered dicts
        ruamel_data = ruamel.yaml.round_trip_load(stream)

    # parse YAML into a dict
    with open(yaml_filename, 'r') as stream:
        data = yaml.load(stream, Loader=yamlloader.ordereddict.CSafeLoader)

    return (data, ruamel_data)

def obj_to_yaml(obj, indent=4):
    # use this different library because PyYAML doesn't handle indenting properly
    # rt = round-trip
    ruyaml = ruamel.yaml.YAML(typ='rt')
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
        elif (isinstance(transition, dict) or
              isinstance(transition, ruamel.yaml.comments.CommentedMap)):
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

def dict_to_list(d):
    return [{k: v} for k, v in six.iteritems(d)]

def convert_workflow_task_transition_simple(transitions, publish, orquesta_expr):
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
        simple_transition['when'] = '{{ ' + orquesta_expr + ' }}'

    # add in published variables
    if publish:
        publish_converted = expressions.convert_expression_dict(publish)
        simple_transition['publish'] = dict_to_list(publish_converted)

    # add in the transition list
    if transitions:
        simple_transition['do'] = transitions

    return simple_transition

def convert_workflow_task_transition_expr(expression_list, orquesta_expr):
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
        expr_converted = expressions.convert_expression(expr)

        # for some transitions (on-complete) the orquesta_expr may be empty
        # so only add it in, if it's necessary
        if orquesta_expr:
            o_expr = '{} and {}'.format(orquesta_expr, expr_converted)
        else:
            o_expr = expr_converted

        expr_transition['when'] = '{{ ' + o_expr + ' }}'
        expr_transition['do'] = task_list
        transitions.append(expr_transition)
    return transitions

def convert_workflow_task_transitions(m_task_spec):
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
        trans_simple, trans_expr = group_task_transitions(m_transitions)

        # Create a transition for the simple task lists
        if data['publish'] or trans_simple:
            o_trans_simple = convert_workflow_task_transition_simple(trans_simple,
                                                                     data['publish'],
                                                                     data['orquesta_expr'])
            o_task_spec['next'].append(o_trans_simple)

        # Create multiple transitions, one for each unique expression
        o_trans_expr_list = convert_workflow_task_transition_expr(trans_expr,
                                                                  data['orquesta_expr'])
        o_task_spec['next'].extend(o_trans_expr_list)

    return o_task_spec if o_task_spec['next'] else ruamel.yaml.comments.CommentedMap()

def convert_workflow_tasks(mistral_wf_tasks):
    orquesta_wf_tasks = ruamel.yaml.comments.CommentedMap()
    for task_name, m_task_spec in six.iteritems(mistral_wf_tasks):
        o_task_spec = ruamel.yaml.comments.CommentedMap()

        if m_task_spec.get('action'):
            o_task_spec['action'] = m_task_spec['action']

        if m_task_spec.get('join'):
            o_task_spec['join'] = m_task_spec['join']

        if m_task_spec.get('input'):
            o_task_spec['input'] = expressions.convert_expression_dict(m_task_spec['input'])

        o_task_transitions = convert_workflow_task_transitions(m_task_spec)
        o_task_spec.update(o_task_transitions)

        orquesta_wf_tasks[task_name] = o_task_spec

    return orquesta_wf_tasks

def convert_workflow(mistral_wf):
    orquesta_wf = ruamel.yaml.comments.CommentedMap()
    orquesta_wf['version'] = '1.0'

    if mistral_wf.get('description'):
        orquesta_wf['description'] = mistral_wf['description']

    if mistral_wf.get('input'):
        orquesta_wf['input'] = expressions.convert_expression_list(mistral_wf['input'])

    if mistral_wf.get('vars'):
        orquesta_wf['vars'] = expressions.convert_expression_list(mistral_wf['vars'])

    if mistral_wf.get('output'):
        orquesta_wf['output'] = expressions.convert_expression_list(mistral_wf['output'])

    if mistral_wf.get('tasks'):
        o_tasks = convert_workflow_tasks(mistral_wf['tasks'])
        if o_tasks:
            orquesta_wf['tasks'] = o_tasks

    return orquesta_wf

def run():
    args = parse_args()
    for f in args.filename:
        # parse the Mistral workflow from file
        mistral_wf_data, mistral_wf_data_ruamel = read_yaml(f)

        # validate the Mistral workflow before we start
        mistral_wf_spec = mistral_workflow.instantiate(mistral_wf_data)
        validate_workflow_spec(mistral_wf_spec)

        # convert Mistral -> Orquesta
        orquesta_wf_data_ruamel = convert_workflow(mistral_wf_data_ruamel[mistral_wf_spec.name])
        orquesta_wf_data_str = obj_to_yaml(orquesta_wf_data_ruamel)
        orquesta_wf_data = yaml.load(orquesta_wf_data_str, Loader=yamlloader.ordereddict.CSafeLoader)

        # validate we've generated a proper Orquesta workflow
        orquesta_wf_spec = orquesta_workflow.instantiate(orquesta_wf_data)
        validate_workflow_spec(orquesta_wf_spec)

        # write out the new Orquesta workflow
        print obj_to_yaml(orquesta_wf_data_ruamel)
    return 0
