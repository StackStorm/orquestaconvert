SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
ORQUESTACONVERT_DIR="${SCRIPT_DIR}/.."
VIRTUALENV_DIR="${ORQUESTACONVERT_DIR}/virtualenv"

# create virtualenv if it doesn't exit
test -d "$VIRTUALENV_DIR" || VIRTUALENV_DIR=$VIRTUALENV_DIR make -C $ORQUESTACONVERT_DIR requirements

# activate the virtualenv
source ${VIRTUALENV_DIR}/bin/activate

# run the script, forwarding all arguments passed to this shell script
${ORQUESTACONVERT_DIR}/orquestaconvert/pack_client.py "$@"
exit $?
