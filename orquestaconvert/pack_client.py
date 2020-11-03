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
import glob
import os
import shutil
import six
import sys

import yaml

from orquestaconvert import client
from orquestaconvert.utils import yaml_utils


# The file extension to use for backup files - these files are backups of the
# original workflow and action metadata files, and normally be removed upon
# success or failure. However, sending a SIGINT or SIGHUP to the process may
# leave these files behind.
BACKUP_EXTENSION = 'orquestaconvert.bak.yaml'
# The file extension to use for temporary files. These files are the converted
# workflow and action metadata files, and should also be removed upon success
# or failure. However, it may sometimes be useful to keep these files,
# especially when using the --force option.
TMP_EXTENSION = 'orquesta.temp.yaml'


class PackClient(object):
    def parser(self):
        parser = argparse.ArgumentParser(description='Convert all Mistral workflows in a pack')
        parser.add_argument('--validate', default=False, action='store_true',
                            help='Validate the Orquesta workflow')
        parser.add_argument('--list-workflows', dest='workflow_type', type=str,
                            help='List Mistral workflows in the pack and exit')
        parser.add_argument('--actions-dir', dest='actions_directory', default=None, type=str,
                            help='The action directory to convert')
        return parser

    def get_workflow_files(self, workflow_type, directory=None):
        action_directory = directory if directory else 'actions'
        glob_string = '{}/*.yaml'.format(action_directory)
        a_files = glob.glob(glob_string)
        mistral_workflows = {}
        for a_file in a_files:
            with open(a_file, 'r') as f:
                action_data = yaml.safe_load(f.read())
            runner = action_data.get('runner_type')

            if runner == workflow_type:
                mistral_workflows[a_file] = os.path.join(
                    action_directory,
                    *os.path.split(action_data.get('entry_point')))

        return mistral_workflows

    def run(self, argv, output_stream, client=None):
        self.args, args = self.parser().parse_known_args(argv)
        wf_type = self.args.workflow_type
        directory = self.args.actions_directory
        if wf_type:
            for action, workflow in self.get_workflow_files(wf_type, directory).items():
                output_stream.write("{} --> {}\n".format(action, workflow))
            return 0

        if self.args.validate:
            args.append('--validate')
            filenames = self.get_workflow_files('orquesta', directory).values()
            total = 0
            for f in filenames:
                fargs = list(args)
                fargs.append(f)
                total += client.run(fargs, output_stream)
            return total

        filenames = self.get_workflow_files('mistral-v2', directory)

        exceptions = {}
        for a_f, m_f in six.iteritems(filenames):
            fargs = list(args)  # make a copy
            fargs.append(m_f)

            # Get the backup filenames
            m_f_backup = '{}.{}'.format(m_f, BACKUP_EXTENSION)
            a_f_backup = '{}.{}'.format(a_f, BACKUP_EXTENSION)
            o_f = '{}.{}'.format(m_f, TMP_EXTENSION)  # Orquesta workflow file

            # Convert the workflow and save the YAML string in output
            output = six.moves.StringIO()
            # In this next block of code we are attempting to create a filesystem
            # transaction, where we either want to commit all of the changes to
            # disk or none of the changes.
            # Usually you want to minimize what you put into a try block, so you
            # can catch different errors and handle them differently. However, in
            # this case, there are so many file operations that can fail that it
            # ends up nesting try/except/else blocks very deep, and exception
            # handlers simply do cleanup and re-raise the exception.
            # So instead, we do all of our work in the try block, and handle
            # cleaning up after the different failure conditions in the except
            # block, and handle success conditions in the else block.
            try:
                client.run(fargs, output)

                # Write the workflow file
                with open(o_f, 'w') as o_file:
                    o_file.write(str(output.getvalue()))

                # If the backup files already exist, they were created by a
                # previous run. In that case, we want to preserve the original
                # backup file, because it is more likely a valid Mistral
                # workflow than whatever the current workflow file is.
                if not os.path.isfile(m_f_backup):
                    # Move the existing workflow file to a backup
                    os.rename(m_f, m_f_backup)

                if not os.path.isfile(a_f_backup):
                    # Move the existing metadata file to a backup
                    shutil.copy2(a_f, a_f_backup)

                # Read the file into a dict, tweak the runner_type, and write
                # the dict back into a string
                action_data, action_data_ruamel = yaml_utils.read_yaml(a_f)
                action_data_ruamel['runner_type'] = 'orquesta'
                write_data = yaml_utils.obj_to_yaml(action_data_ruamel)

                # Promote/move the new workflow file into place
                shutil.move(o_f, m_f)

                # Rewrite the metadata file with the tweaked runner_rtype
                with open(a_f, 'w') as a_file:
                    a_file.write(write_data)
                # SUCCESS!

            except Exception as e:
                # Anything could have happened, so we check for bad conditions

                # If we have a backup workflow file, revert it
                if os.path.isfile(m_f_backup):
                    # Remove the converted workflow file
                    if os.path.isfile(m_f):
                        os.remove(m_f)
                    # Move the backup file back
                    os.rename(m_f_backup, m_f)

                # If we have a backup action metadata file
                if os.path.isfile(a_f_backup):
                    # Remove the converted metadata file
                    if os.path.isfile(a_f):
                        os.remove(a_f)
                    # Move the backup file back
                    os.rename(a_f_backup, a_f)

                # If we ever support just Python 3, we can add the exception
                # directly to the dictionary value:
                #
                # .append({'file': m_f, 'exception': e})
                #
                exceptions.setdefault(str(e), []).append(m_f)
            else:
                # Remove the backup files
                os.remove(m_f_backup)
                os.remove(a_f_backup)

        if exceptions:
            sys.stderr.write("ERROR: Unable to convert all Mistral workflows.\n")
            for e, wfs in exceptions.items():
                sys.stderr.write("ISSUE: {}\n".format(e))
                sys.stderr.write("Affected files:\n")
                for wf in wfs:
                    sys.stderr.write("  - {}\n".format(wf))
                sys.stderr.write("\n")

        return len(exceptions)


if __name__ == '__main__':
    sys.exit(PackClient().run(sys.argv[1:], sys.stdout, client=client.Client()))
