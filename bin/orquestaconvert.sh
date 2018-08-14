VIRTUALENV_DIR="virtualenv"

# create virtualenv if it doesn't exit
test -d "$VIRTUALENV_DIR" || make

# activate the virtualenv
source virtualenv/bin/activate

# run the script, forwarding all arguments passed to this shell script
./bin/mistral_to_orquesta.py "$@"
