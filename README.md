# orchestraconvert

Converts Mistral workflows into Orchestra workflows

# Setup

This package relies on [Orchestra](https://github.com/StackStorm/orchestra) itself
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

To run the `orchestraconvert.py` script we now need to activate the virtualenv:

``` shell
source ./virtualenv/bin/activate
./orchestraconvert.py ./test/fixtures/mistral/nasa_apod_twitter_post.yaml
```

We've also make a simple shell wrapper script that does this same thing in one command.
(**NOTE:** It will also create the `virtualenv` if it doesn't exist):

``` shell
./orchestraconvert.sh ./test/fixtures/mistral/nasa_apod_twitter_post.yaml
```


