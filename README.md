# orquestaconvert

Converts Mistral workflows into Orquesta workflows

# Setup

This package relies on [Orquesta](https://github.com/StackStorm/orquesta) itself
along with a few other Python dependencies found in [requirements.txt](requirements.txt).

To handle all of this we have a [Makefile](Makefile) that sets up a
[virtualenv](https://virtualenv.pypa.io/en/stable/) in the directory `virtualenv/`.
Creating the `virtualenv` is easy!

``` shell
make
```

# Usage

The script takes a single argument, which is the name of the Mistral workflow
YAML file to convert.

We've made a shell script that sets up the `virtualenv` (if it doesn't exist) and
then executes the conversion:

``` shell
./bin/orquestaconvert.sh ./test/fixtures/mistral/nasa_apod_twitter_post.yaml
```

# Features

* Converts `direct` Mistral Workflows into Orquesta Workflows (general structure)
* Handles `input`, `output`, `tasks`
* For each task, `action`, `input`, `publish`, `on-success`, `on-error`, and `on-complete` are all converted

# Limitations

* Does not yet convert `task()`, `st2kv`, `_.xxx` / `$.xxx`, etc in Jinja and YAQL expressions
* Does not convert `reverse` workflows
* Does not convert workbooks

