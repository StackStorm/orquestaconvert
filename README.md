[![Build Status](https://circleci.com/gh/EncoreTechnologies/orquestaconvert.svg?style=shield&circle-token=:circle-token)](https://circleci.com/gh/EncoreTechnologies/orquestaconvert) [![codecov](https://codecov.io/gh/EncoreTechnologies/orquestaconvert/branch/master/graph/badge.svg)](https://codecov.io/gh/EncoreTechnologies/orquestaconvert) [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# orquestaconvert

Converts Mistral workflows into Orquesta workflows

# Usage

The script takes a single argument, which is the name of the Mistral workflow
YAML file to convert.

We've made a shell script that sets up a `virtualenv` (if it doesn't exist) that contains
all dependencies necessary to run the code!

``` shell
./bin/orquestaconvert.sh ./tests/fixtures/mistral/nasa_apod_twitter_post.yaml
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


Testing CircleCI build
