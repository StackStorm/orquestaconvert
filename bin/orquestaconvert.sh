VIRTUALENV_DIR="virtualenv"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

# create virtualenv if it doesn't exit
test -d "$VIRTUALENV_DIR" || make

# activate the virtualenv
source ${SCRIPT_DIR}/../virtualenv/bin/activate

# run the script, forwarding all arguments passed to this shell script
${SCRIPT_DIR}/../orquestaconvert/client.py "$@"
