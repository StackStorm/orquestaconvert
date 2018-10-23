[![Build Status](https://circleci.com/gh/EncoreTechnologies/orquestaconvert.svg?style=shield&circle-token=:circle-token)](https://circleci.com/gh/EncoreTechnologies/orquestaconvert) [![codecov](https://codecov.io/gh/EncoreTechnologies/orquestaconvert/branch/master/graph/badge.svg)](https://codecov.io/gh/EncoreTechnologies/orquestaconvert) [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# orquestaconvert

Converts Mistral workflows into Orquesta workflows

# Usage

## `orquestaconvert.sh` - convert a single workflow and print to stdout

The script automatically sets up a `virtualenv` (if it doesn't exist) that contains all of the necessary depedencies to run.

You must specify one or more workflow YAML files to convert as the last arguments to the script.

There are also some options you can use:

- `-e <type>` - Type of expressions (YAQL or Jinja) to use when inserting new expressions (such as task transitions in the `when` clause)
- `--force` - Forces the script to convert and print the workflow even if it does not successfully validate against the Orquesta YAML schema.

### Examples

```shell
./bin/orquestaconvert.sh ./tests/fixtures/mistral/nasa_apod_twitter_post.yaml
```

```shell
./bin/orquestaconvert.sh -e yaql ./tests/fixtures/mistral/nasa_apod_twitter_post.yaml
```

```shell
./bin/orquestaconvert.sh --force ./tests/fixtures/mistral/nasa_apod_twitter_post.yaml
```

## `orquestaconvert-pack.sh` - convert all Mistral workflows in a pack

This script scans a directory for all action metadata files and attempts to convert all Mistral workflows to (and metadata files) to Orquesta.

The script also automatically sets up (if it doesn't exist) and uses the `virtualenv` that contains all necessary depedencies to run.

You must either run this command from the base directory of a pack or you must specify the directory that contains action metadata files with the `--actions-dir` option.

Other options are:

- `--list-workflows <type>` - List all workflows of the specified type (must either be `action-chain` for ActionChain, `mistral-v2` for Mistral, or `orquesta` or `orchestra` for Orquesta workflows)
- `--actions-dir <dir>` - Specifies the directory to scan and convert

All unrecognized options are passed directly to the `orquestaconvert.sh` command.

### Examples

```shell
./bin/orquestaconvert-pack.sh
```

```shell
./bin/orquestaconvert-pack.sh --list-workflows mistral-v2
```

```shell
./bin/orquestaconvert-pack.sh --expressions yaql --actions-dir mypack/actions
```

# Features

* Converts `direct` Mistral Workflows into Orquesta Workflows (general structure)
* Handles `input`, `output`, `tasks`
* For each task, `action`, `input`, `publish`, `on-success`, `on-error`, and `on-complete` are all converted
* Converts _simple_ Jinja and YAQL expressions
* Converts `task()`, `st2kv`, `_.xxx` / `$.xxx`, etc in Jinja and YAQL expressions

# Limitations

* Does not convert `{% %}` Jinja expressions
* Does not convert complex Jinja / YAQL expressions
* Does not convert `reverse` type workflows
* Does not convert workbooks (multiple workflows in the same file
* Does not convert `task('xxx')` references to non-local tasks, the current task is always assumed.
* Does not convert workflows with an `output-on-error` stanza
* Does not convert workflows if the tasks contain one or more of the following attributes
    * `concurrency`
    * `keep-result`
    * `pause-before`
    * `retry`
    * `safe-rerun`
    * `target`
    * `timeout`
    * `wait-after`
    * `wait-before`
    * `with-items`
    * `workflow`
