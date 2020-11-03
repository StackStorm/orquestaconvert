#!/usr/bin/env python
#
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

import argparse
import sys

from orquesta.specs.native.v1 import models as native_v1_models
from orquestaconvert.specs.mistral.v2 import workflows as mistral_workflow
from orquestaconvert.utils import yaml_utils
from orquestaconvert.workflows import base as workflows_base


class Client(object):

    def parser(self):
        parser = argparse.ArgumentParser(description='Convert Mistral workflows to Orquesta')
        parser.add_argument('-v', '--verbose', default=False, action='store_true',
                            help='Print success message when validating, otherwise ignored')
        parser.add_argument('-e', '--expressions',
                            choices=['jinja', 'yaql'],
                            default='jinja',
                            help=('Type of expressions to use when inserting new expressions'
                                  ' (things like task transitions in the "when" clause.'))
        parser.add_argument('--force', default=False, action='store_true',
                            help='Include unsupported attributes in the generated outputs')
        parser.add_argument('--validate', default=False, action='store_true',
                            help='Validate the Orquesta workflow')
        parser.add_argument('filename', metavar='FILENAME', nargs=1,
                            help='Path to the Mistral Workflow YAML file to convert')
        return parser

    def validate_workflow_spec(self, wf_spec):
        result = wf_spec.inspect_syntax()
        if result:
            raise ValueError(result)

    def convert_file(self, filename, expr_type=None):
        # parse the Mistral workflow from file
        mistral_wf_data, mistral_wf_data_ruamel = yaml_utils.read_yaml(filename)

        # validate the Mistral workflow before we start
        mistral_wf_spec = mistral_workflow.instantiate(mistral_wf_data)
        self.validate_workflow_spec(mistral_wf_spec)

        # convert Mistral -> Orquesta
        mistral_wf = mistral_wf_data_ruamel[mistral_wf_spec.name]
        workflow_converter = workflows_base.WorkflowConverter()
        orquesta_wf_data_ruamel = workflow_converter.convert(mistral_wf, expr_type,
                                                             force=self.args.force)
        orquesta_wf_data_str = yaml_utils.obj_to_yaml(orquesta_wf_data_ruamel)
        orquesta_wf_data = yaml_utils.yaml_to_obj(orquesta_wf_data_str)

        # validate we've generated a proper Orquesta workflow
        orquesta_wf_spec = native_v1_models.instantiate(orquesta_wf_data)
        if not self.args.force:
            self.validate_workflow_spec(orquesta_wf_spec)

        # write out the new Orquesta workflow to a YAML string
        return yaml_utils.obj_to_yaml(orquesta_wf_data_ruamel)

    def validate_file(self, filename):
        # parse the Orquesta workflow from file
        orquesta_wf_data, orquesta_wf_data_ruamel = yaml_utils.read_yaml(filename)

        # validate the Orquesta workflow
        orquesta_wf_spec = native_v1_models.instantiate(orquesta_wf_data)
        self.validate_workflow_spec(orquesta_wf_spec)

        if self.args.verbose:
            print("Successfully validated workflow from {}".format(filename))

    def run(self, argv, output_stream):
        # Write the file to the output_stream
        self.args = self.parser().parse_args(argv)
        expr_type = self.args.expressions
        if self.args.validate:
            for f in self.args.filename:
                self.validate_file(f)
        else:
            for f in self.args.filename:
                output_stream.write(self.convert_file(f, expr_type))
        return 0


if __name__ == '__main__':
    # Write the converted workflow to stdout
    sys.exit(Client().run(sys.argv[1:], sys.stdout))
