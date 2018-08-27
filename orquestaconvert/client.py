#!/usr/bin/env python

import argparse

from orquesta.specs.mistral.v2 import workflows as mistral_workflow
from orquesta.specs.native.v1 import models as orquesta_workflow

from orquestaconvert import workflows
from orquestaconvert.utils import yaml_utils



def parse_args():
    parser = argparse.ArgumentParser(description='Convert Mistral workflows to Orquesta')
    parser.add_argument('filename', metavar='FILENAME', nargs=1,
                        help='Path to the Mistral Workflow YAML file to convert')
    return parser.parse_args()

def validate_workflow_spec(wf_spec):
    result = wf_spec.inspect_syntax()
    if result:
        raise ValueError(result)

def run():
    args = parse_args()
    for f in args.filename:
        # parse the Mistral workflow from file
        mistral_wf_data, mistral_wf_data_ruamel = yaml_utils.read_yaml(f)

        # validate the Mistral workflow before we start
        mistral_wf_spec = mistral_workflow.instantiate(mistral_wf_data)
        validate_workflow_spec(mistral_wf_spec)

        # convert Mistral -> Orquesta
        mistral_wf = mistral_wf_data_ruamel[mistral_wf_spec.name]
        orquesta_wf_data_ruamel = workflows.convert_workflow(mistral_wf)
        orquesta_wf_data_str = yaml_utils.obj_to_yaml(orquesta_wf_data_ruamel)
        orquesta_wf_data = yaml_utils.yaml_to_obj(orquesta_wf_data_str)

        # validate we've generated a proper Orquesta workflow
        orquesta_wf_spec = orquesta_workflow.instantiate(orquesta_wf_data)
        validate_workflow_spec(orquesta_wf_spec)

        # write out the new Orquesta workflow
        print yaml_utils.obj_to_yaml(orquesta_wf_data_ruamel)
    return 0
